'use client';

import { useState, useEffect, createContext, useContext } from 'react';

interface ToastProviderProps {
  children: React.ReactNode;
}

interface Toast {
  id: string;
  title?: string;
  description: string;
  variant?: 'default' | 'destructive' | 'success';
}

interface ToastContextType {
  toast: (props: Omit<Toast, 'id'>) => void;
  dismiss: (id: string) => void;
  toasts: Toast[];
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = (props: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prevToasts) => [...prevToasts, { id, ...props }]);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
      dismiss(id);
    }, 5000);
  };

  const dismiss = (id: string) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toast, dismiss, toasts }}>
      {children}
      {toasts.length > 0 && (
        <div className="fixed bottom-0 right-0 p-4 z-50 flex flex-col items-end space-y-2">
          {toasts.map((toast) => (
            <div
              key={toast.id}
              className={`rounded-md border p-4 shadow-md transition-all max-w-sm ${
                toast.variant === 'destructive'
                  ? 'bg-destructive text-destructive-foreground border-destructive'
                  : toast.variant === 'success'
                  ? 'bg-green-600 text-white border-green-600'
                  : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700'
              }`}
            >
              {toast.title && (
                <div className="font-medium mb-1">{toast.title}</div>
              )}
              <div className="text-sm">{toast.description}</div>
              <button
                className="absolute top-2 right-2 text-sm opacity-70 hover:opacity-100"
                onClick={() => dismiss(toast.id)}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}