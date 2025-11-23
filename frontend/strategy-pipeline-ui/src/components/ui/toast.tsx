import { useEffect, useState } from 'react';
import { CheckCircle, X, AlertCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'success' | 'error' | 'info';
  duration?: number;
}

const toastStore: {
  toasts: Toast[];
  listeners: Set<(toasts: Toast[]) => void>;
} = {
  toasts: [],
  listeners: new Set(),
};

export const toast = {
  success: (title: string, description?: string) => {
    const id = Math.random().toString(36).slice(2);
    const newToast: Toast = { id, title, description, variant: 'success', duration: 3000 };
    toastStore.toasts.push(newToast);
    toastStore.listeners.forEach(listener => listener([...toastStore.toasts]));

    setTimeout(() => {
      toastStore.toasts = toastStore.toasts.filter(t => t.id !== id);
      toastStore.listeners.forEach(listener => listener([...toastStore.toasts]));
    }, newToast.duration);
  },
  error: (title: string, description?: string) => {
    const id = Math.random().toString(36).slice(2);
    const newToast: Toast = { id, title, description, variant: 'error', duration: 5000 };
    toastStore.toasts.push(newToast);
    toastStore.listeners.forEach(listener => listener([...toastStore.toasts]));

    setTimeout(() => {
      toastStore.toasts = toastStore.toasts.filter(t => t.id !== id);
      toastStore.listeners.forEach(listener => listener([...toastStore.toasts]));
    }, newToast.duration);
  },
  info: (title: string, description?: string) => {
    const id = Math.random().toString(36).slice(2);
    const newToast: Toast = { id, title, description, variant: 'info', duration: 3000 };
    toastStore.toasts.push(newToast);
    toastStore.listeners.forEach(listener => listener([...toastStore.toasts]));

    setTimeout(() => {
      toastStore.toasts = toastStore.toasts.filter(t => t.id !== id);
      toastStore.listeners.forEach(listener => listener([...toastStore.toasts]));
    }, newToast.duration);
  },
};

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const listener = (newToasts: Toast[]) => setToasts(newToasts);
    toastStore.listeners.add(listener);
    return () => { toastStore.listeners.delete(listener); };
  }, []);

  const removeToast = (id: string) => {
    toastStore.toasts = toastStore.toasts.filter(t => t.id !== id);
    toastStore.listeners.forEach(listener => listener([...toastStore.toasts]));
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={cn(
            "rounded-lg border p-4 shadow-lg backdrop-blur-sm animate-in slide-in-from-top-2",
            t.variant === 'success' && "bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800",
            t.variant === 'error' && "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800",
            t.variant === 'info' && "bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800"
          )}
        >
          <div className="flex items-start gap-3">
            {t.variant === 'success' && <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />}
            {t.variant === 'error' && <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />}
            {t.variant === 'info' && <Info className="h-5 w-5 text-blue-600 dark:text-blue-400" />}

            <div className="flex-1">
              <p className="font-medium text-sm">{t.title}</p>
              {t.description && (
                <p className="text-sm text-muted-foreground mt-1">{t.description}</p>
              )}
            </div>

            <button
              onClick={() => removeToast(t.id)}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

