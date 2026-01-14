import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, GlobalStyles } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { router } from './utils/router';
import { theme } from './theme/theme';
import { AuthProvider } from './context/AuthContext';
import { LoadingProvider } from './context/LoadingContext';
import { ChatProvider } from './context/ChatContext';

// Global styles
const globalStyles = (
  <GlobalStyles
    styles={{
      '*': {
        margin: 0,
        padding: 0,
        boxSizing: 'border-box',
      },
      html: {
        height: '100%',
      },
      body: {
        height: '100%',
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      },
      '#root': {
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      },
      // Custom scrollbar styles
      '::-webkit-scrollbar': {
        width: '8px',
        height: '8px',
      },
      '::-webkit-scrollbar-track': {
        background: '#f1f1f1',
        borderRadius: '4px',
      },
      '::-webkit-scrollbar-thumb': {
        background: '#c1c1c1',
        borderRadius: '4px',
        '&:hover': {
          background: '#a8a8a8',
        },
      },
      // Chat message styles
      '.chat-message': {
        animation: 'fadeInUp 0.3s ease-out',
      },
      '@keyframes fadeInUp': {
        '0%': {
          opacity: 0,
          transform: 'translateY(20px)',
        },
        '100%': {
          opacity: 1,
          transform: 'translateY(0)',
        },
      },
      // Loading animation
      '.loading-dots': {
        display: 'inline-block',
        position: 'relative',
        width: '80px',
        height: '80px',
        '& div': {
          position: 'absolute',
          top: '33px',
          width: '13px',
          height: '13px',
          borderRadius: '50%',
          background: '#1976d2',
          animationTimingFunction: 'cubic-bezier(0, 1, 1, 0)',
        },
        '& div:nth-child(1)': {
          left: '8px',
          animation: 'loading-dots1 0.6s infinite',
        },
        '& div:nth-child(2)': {
          left: '8px',
          animation: 'loading-dots2 0.6s infinite',
        },
        '& div:nth-child(3)': {
          left: '32px',
          animation: 'loading-dots2 0.6s infinite',
        },
        '& div:nth-child(4)': {
          left: '56px',
          animation: 'loading-dots3 0.6s infinite',
        },
      },
      '@keyframes loading-dots1': {
        '0%': {
          transform: 'scale(0)',
        },
        '100%': {
          transform: 'scale(1)',
        },
      },
      '@keyframes loading-dots3': {
        '0%': {
          transform: 'scale(1)',
        },
        '100%': {
          transform: 'scale(0)',
        },
      },
      '@keyframes loading-dots2': {
        '0%': {
          transform: 'translate(0, 0)',
        },
        '100%': {
          transform: 'translate(24px, 0)',
        },
      },
    }}
  />
);

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {globalStyles}
      
      <AuthProvider>
        <LoadingProvider>
          <ChatProvider>
            <RouterProvider router={router} />
            
            {/* Toast notifications */}
            <ToastContainer
              position="top-right"
              autoClose={5000}
              hideProgressBar={false}
              newestOnTop
              closeOnClick
              rtl={false}
              pauseOnFocusLoss
              draggable
              pauseOnHover
              theme="colored"
              toastStyle={{
                fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
              }}
            />
          </ChatProvider>
        </LoadingProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
