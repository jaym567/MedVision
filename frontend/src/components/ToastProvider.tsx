// frontend/src/components/ToastProvider.tsx
/**
 * Toast notification provider wrapper
 */

import { Toaster } from 'react-hot-toast';

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        // Default options
        duration: 4000,
        style: {
          background: '#1f2937', // gray-800
          color: '#fff',
          border: '1px solid #374151', // gray-700
        },
        // Success toast style
        success: {
          iconTheme: {
            primary: '#10b981', // green-500
            secondary: '#fff',
          },
        },
        // Error toast style
        error: {
          iconTheme: {
            primary: '#ef4444', // red-500
            secondary: '#fff',
          },
          duration: 5000,
        },
      }}
    />
  );
}

export default ToastProvider;
