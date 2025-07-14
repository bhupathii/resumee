import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LogIn, LogOut, User, Shield } from 'lucide-react';

declare global {
  interface Window {
    google: any;
  }
}

interface GoogleAuthProps {
  user: any;
  onLogin: (user: any) => void;
  onLogout: () => void;
}

const GoogleAuth: React.FC<GoogleAuthProps> = ({ user, onLogin, onLogout }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleAuth = async (response: any) => {
    setIsLoading(true);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || '';
      
      const authResponse = await fetch(`${apiUrl}/api/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: response.credential
        }),
      });

      const data = await authResponse.json();

      if (data.success) {
        // Store session token
        localStorage.setItem('session_token', data.session_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        onLogin(data.user);
      } else {
        console.error('Authentication failed:', data.error);
        alert('Authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('Google Auth error:', error);
      alert('Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    setIsLoading(true);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || '';
      const sessionToken = localStorage.getItem('session_token');

      if (sessionToken) {
        await fetch(`${apiUrl}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${sessionToken}`,
          },
        });
      }

      // Clear local storage
      localStorage.removeItem('session_token');
      localStorage.removeItem('user');
      onLogout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    // Load Google Sign-In script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    document.body.appendChild(script);

    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
          callback: handleGoogleAuth,
        });
      }
    };

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const renderGoogleButton = () => {
    if (window.google) {
      window.google.accounts.id.renderButton(
        document.getElementById('google-signin-button'),
        {
          theme: 'outline',
          size: 'large',
          width: 250,
          text: 'signin_with',
        }
      );
    }
  };

  React.useEffect(() => {
    if (!user && window.google) {
      const timer = setTimeout(renderGoogleButton, 100);
      return () => clearTimeout(timer);
    }
  }, [user]);

  if (user) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-4"
      >
        <div className="flex items-center space-x-3">
          <img
            src={user.profile_picture}
            alt={user.name}
            className="w-8 h-8 rounded-full"
          />
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-gray-700">{user.name}</p>
            <div className="flex items-center space-x-1">
              {user.is_premium ? (
                <div className="flex items-center space-x-1">
                  <Shield className="w-3 h-3 text-yellow-500" />
                  <span className="text-xs text-yellow-600">Premium</span>
                </div>
              ) : (
                <span className="text-xs text-gray-500">Free Plan</span>
              )}
            </div>
          </div>
        </div>
        <button
          onClick={handleLogout}
          disabled={isLoading}
          className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center space-x-4"
    >
      <div id="google-signin-button" className="google-signin-button"></div>
      {isLoading && (
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
          <span>Signing in...</span>
        </div>
      )}
    </motion.div>
  );
};

export default GoogleAuth; 