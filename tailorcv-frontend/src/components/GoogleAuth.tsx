import React, { useState, useEffect, useRef } from 'react';
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
  const [error, setError] = useState<string | null>(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const googleButtonRef = useRef<HTMLDivElement>(null);
  const scriptRef = useRef<HTMLScriptElement | null>(null);

  const handleGoogleAuth = async (response: any) => {
    setIsLoading(true);
    setError(null);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || '';
      
      if (!apiUrl) {
        throw new Error('API URL not configured. Please set REACT_APP_API_URL environment variable.');
      }
      
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
        setError(null);
      } else {
        const errorMsg = data.error || 'An unknown authentication error occurred.';
        console.error('Authentication failed:', errorMsg);
        // Make the error message more prominent and clear
        setError(`Authentication Failed: ${errorMsg}`);
      }
    } catch (error: any) {
      const errorMsg = error.message || 'A network or server error occurred. Please try again.';
      console.error('Google Auth error:', error);
      setError(`Error: ${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || '';
      const sessionToken = localStorage.getItem('session_token');

      if (sessionToken && apiUrl) {
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
      // Still proceed with local logout even if server request fails
      localStorage.removeItem('session_token');
      localStorage.removeItem('user');
      onLogout();
    } finally {
      setIsLoading(false);
    }
  };

  const loadGoogleScript = () => {
    // Don't load if already loaded or loading
    if (scriptRef.current || window.google?.accounts?.id) {
      setScriptLoaded(true);
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    scriptRef.current = script;

    script.onload = () => {
      setScriptLoaded(true);
      if (window.google?.accounts?.id) {
        initializeGoogleAuth();
      }
    };

    script.onerror = () => {
      setError('Failed to load Google Sign-In. Please check your internet connection.');
      setScriptLoaded(false);
    };

    document.body.appendChild(script);
  };

  const initializeGoogleAuth = () => {
    const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
    
    if (!clientId) {
      setError('Google Client ID not configured. Please set REACT_APP_GOOGLE_CLIENT_ID environment variable.');
      return;
    }

    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleGoogleAuth,
        auto_select: false,
      });
      
      renderGoogleButton();
    } catch (error) {
      console.error('Failed to initialize Google Auth:', error);
      setError('Failed to initialize Google Sign-In.');
    }
  };

  const renderGoogleButton = () => {
    if (window.google?.accounts?.id && googleButtonRef.current && !user) {
      try {
        // Clear existing button
        googleButtonRef.current.innerHTML = '';
        
        window.google.accounts.id.renderButton(
          googleButtonRef.current,
          {
            theme: 'outline',
            size: 'large',
            width: 250,
            text: 'signin_with',
            shape: 'rectangular',
          }
        );
      } catch (error) {
        console.error('Failed to render Google button:', error);
        setError('Failed to render Google Sign-In button.');
      }
    }
  };

  useEffect(() => {
    loadGoogleScript();
    
    return () => {
      // Cleanup script on unmount
      if (scriptRef.current && document.body.contains(scriptRef.current)) {
        document.body.removeChild(scriptRef.current);
        scriptRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (scriptLoaded && window.google?.accounts?.id && !user) {
      initializeGoogleAuth();
    }
  }, [scriptLoaded, user]);

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  if (user) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-4"
      >
        <div className="flex items-center space-x-3">
          <img
            src={user.profile_picture || '/default-avatar.png'}
            alt={user.name || 'User'}
            className="w-8 h-8 rounded-full"
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/default-avatar.png';
            }}
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
          className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">
            {isLoading ? 'Logging out...' : 'Logout'}
          </span>
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center space-y-2"
    >
      <div className="flex items-center space-x-4">
        <div ref={googleButtonRef} className="google-signin-button"></div>
        {isLoading && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
            <span>Signing in...</span>
          </div>
        )}
      </div>
      
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xs text-red-600 bg-red-100 border border-red-200 px-3 py-2 rounded-md max-w-sm text-center shadow-md"
        >
          {error}
        </motion.div>
      )}
      
      {!scriptLoaded && !error && (
        <div className="text-xs text-gray-500">Loading Google Sign-In...</div>
      )}
    </motion.div>
  );
};

export default GoogleAuth; 