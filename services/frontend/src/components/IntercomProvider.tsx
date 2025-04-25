'use client';

import { useEffect, ReactNode } from 'react';
import { useToast } from './ui/toast';

declare global {
  interface Window {
    Intercom: any;
    intercomSettings: any;
  }
}

interface IntercomProviderProps {
  children: ReactNode;
}

export default function IntercomProvider({ children }: IntercomProviderProps) {
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const appId = process.env.NEXT_PUBLIC_INTERCOM_APP_ID;
      
      // Only load Intercom if app ID is provided
      if (appId) {
        window.intercomSettings = {
          api_base: 'https://api-iam.intercom.io',
          app_id: appId,
        };

        // Load the Intercom script
        (function() {
          var w = window as any;
          var ic = w.Intercom;
          if (typeof ic === "function") {
            ic('reattach_activator');
            ic('update', w.intercomSettings);
          } else {
            var d = document;
            var i = function() {} as any;
            i.q = [];
            i.c = function(args: any) {
              i.q.push(args);
            };
            w.Intercom = i;
            var s = d.createElement('script');
            s.type = 'text/javascript';
            s.async = true;
            s.src = 'https://widget.intercom.io/widget/' + appId;
            var x = d.getElementsByTagName('script')[0];
            x.parentNode?.insertBefore(s, x);
          }
        })();
      }
    }

    return () => {
      // Clean up when the component unmounts
      if (typeof window !== 'undefined' && window.Intercom) {
        window.Intercom('shutdown');
      }
    };
  }, []);

  return <>{children}</>;
}

// Helper function to show Intercom chat
export function showIntercomChat() {
  if (typeof window !== 'undefined' && window.Intercom) {
    window.Intercom('show');
  }
}

// Custom hook to handle API errors with Intercom integration
export function useApiErrorHandler() {
  const { toast } = useToast();

  const handleApiError = (error: any) => {
    // Check if it's a server error (5xx)
    const is5xxError = error?.data?.httpStatus >= 500 || 
                      error?.shape?.data?.httpStatus >= 500 ||
                      error?.status >= 500;
    
    if (is5xxError) {
      toast({
        title: "Something broke",
        description: "We encountered an error. Click 'Chat with us' for support.",
        variant: "destructive",
      });
      
      // Show Intercom chat after a brief delay
      setTimeout(() => {
        showIntercomChat();
      }, 1000);
    } else {
      // For other errors, show a regular error toast
      toast({
        title: "Error",
        description: error?.message || "An unexpected error occurred",
        variant: "destructive",
      });
    }
  };

  return { handleApiError };
}