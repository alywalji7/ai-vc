'use client'

import React, { createContext, useContext, useState, useCallback } from 'react'
import { cn } from '@/lib/utils'

// Toast types
type ToastType = 'default' | 'success' | 'error' | 'warning' | 'destructive'

interface Toast {
  id: string
  title?: string
  description?: string
  variant?: ToastType
  duration?: number
}

interface ToastContextType {
  toasts: Toast[]
  toast: (props: Omit<Toast, 'id'>) => void
  dismissToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const toast = useCallback((props: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9)
    const newToast: Toast = {
      id,
      duration: 5000,
      variant: 'default',
      ...props
    }

    setToasts((prevToasts) => [...prevToasts, newToast])

    // Auto dismiss after duration
    setTimeout(() => {
      dismissToast(id)
    }, newToast.duration)
  }, [])

  const dismissToast = useCallback((id: string) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, toast, dismissToast }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

function ToastContainer() {
  const { toasts, dismissToast } = useToast()
  
  return (
    <div className="fixed bottom-0 right-0 z-50 p-4 space-y-4 max-w-md w-full md:max-w-sm">
      {toasts.map((toast) => (
        <div 
          key={toast.id}
          className={cn(
            "p-4 rounded-md shadow-lg transition-all transform translate-y-0 opacity-100 flex flex-col",
            "bg-background text-foreground border",
            toast.variant === 'success' && "border-green-500",
            toast.variant === 'error' && "border-red-500",
            toast.variant === 'warning' && "border-yellow-500",
            toast.variant === 'destructive' && "bg-destructive text-destructive-foreground"
          )}
        >
          <div className="flex justify-between items-start">
            {toast.title && (
              <h3 className="font-medium text-sm">{toast.title}</h3>
            )}
            <button 
              onClick={() => dismissToast(toast.id)}
              className="ml-auto text-foreground/50 hover:text-foreground"
            >
              <span className="sr-only">Close</span>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="24" 
                height="24" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                className="w-4 h-4"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          {toast.description && (
            <div className="mt-1 text-sm">{toast.description}</div>
          )}
        </div>
      ))}
    </div>
  )
}