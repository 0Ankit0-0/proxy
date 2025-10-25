import { Toaster as HotToaster } from 'react-hot-toast';

export function Toaster() {
  return (
    <HotToaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: 'hsl(210 20% 7%)',
          color: 'hsl(210 40% 98%)',
          border: '1px solid hsl(215 20% 20%)',
          borderRadius: '8px',
        },
        success: {
          iconTheme: {
            primary: '#00FF88',
            secondary: 'hsl(210 20% 7%)',
          },
        },
        error: {
          iconTheme: {
            primary: '#FF3B3B',
            secondary: 'hsl(210 20% 7%)',
          },
        },
      }}
    />
  );
}