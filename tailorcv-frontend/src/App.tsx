import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import ResumeGenerator from './pages/ResumeGenerator';
import PaymentPage from './pages/PaymentPage';
import UserDashboard from './pages/UserDashboard';
import SignInPage from './pages/SignInPage';
import GoogleAuth from './components/GoogleAuth';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const checkExistingSession = async () => {
      const sessionToken = localStorage.getItem('session_token');
      const storedUser = localStorage.getItem('user');

      if (sessionToken && storedUser) {
        try {
          const apiUrl = process.env.REACT_APP_API_URL || '';
          const response = await fetch(`${apiUrl}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${sessionToken}`,
            },
          });

          const data = await response.json();
          if (data.success) {
            setUser(data.user);
            // Update stored user data
            localStorage.setItem('user', JSON.stringify(data.user));
          } else {
            // Invalid session, clear storage
            localStorage.removeItem('session_token');
            localStorage.removeItem('user');
          }
        } catch (error) {
          console.error('Session verification failed:', error);
          localStorage.removeItem('session_token');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    };

    checkExistingSession();
  }, []);

  const handleLogin = (userData: any) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        {/* Navigation Bar - Only show for authenticated users */}
        {user && (
          <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-4">
                <div className="flex items-center space-x-8">
                  <a href="/dashboard" className="text-2xl font-bold text-primary-600">
                    TailorCV
                  </a>
                  <div className="hidden md:flex space-x-6">
                    <a href="/generate" className="text-gray-600 hover:text-primary-600 transition-colors">
                      Generate Resume
                    </a>
                    {!user?.is_premium && (
                      <a href="/payment" className="text-gray-600 hover:text-primary-600 transition-colors">
                        Upgrade
                      </a>
                    )}
                    <a href="/dashboard" className="text-gray-600 hover:text-primary-600 transition-colors">
                      Dashboard
                    </a>
                  </div>
                </div>
                <GoogleAuth user={user} onLogin={handleLogin} onLogout={handleLogout} />
              </div>
            </div>
          </nav>
        )}

        <Routes>
          {/* Public route - Sign in page */}
          <Route 
            path="/signin" 
            element={
              user ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <SignInPage user={user} onLogin={handleLogin} onLogout={handleLogout} />
              )
            } 
          />
          
          {/* Protected routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute user={user}>
                <UserDashboard user={user} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/generate" 
            element={
              <ProtectedRoute user={user}>
                <ResumeGenerator user={user} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/payment" 
            element={
              <ProtectedRoute user={user}>
                <PaymentPage user={user} />
              </ProtectedRoute>
            } 
          />
          
          {/* Redirect root to appropriate page */}
          <Route 
            path="/" 
            element={
              user ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Navigate to="/signin" replace />
              )
            } 
          />
          
          {/* Catch all route */}
          <Route 
            path="*" 
            element={
              user ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Navigate to="/signin" replace />
              )
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
