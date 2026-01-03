import React, { createContext, useState, useEffect } from 'react';

export const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [userSession, setUserSession] = useState(null);
  const [showGoogleLogin, setShowGoogleLogin] = useState(false);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const token = localStorage.getItem("id_token");
    const userId = localStorage.getItem("user_id");
    if (token && userId) {
      try {
        // Parse JWT token to get user info
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        const userInfo = JSON.parse(jsonPayload);
        // Ensure user information includes ID
        userInfo.id = userId;
        setUserSession({ user: userInfo, token });
      } catch (error) {
        console.error('Error parsing JWT token:', error);
        localStorage.removeItem("id_token");
        localStorage.removeItem("user_id");
      }
    }
  }, []);

  const login = (userInfo, token) => {
    setUserSession({ user: userInfo, token });
    localStorage.setItem("id_token", token);
    localStorage.setItem("user_id", userInfo.id);
  };

  const logout = () => {
    setUserSession(null);
    localStorage.removeItem("id_token");
    localStorage.removeItem("user_id");
  };

  const triggerGoogleLogin = () => {
    setShowGoogleLogin(true);
  };

  const closeGoogleLogin = () => {
    setShowGoogleLogin(false);
  };

  return (
    <UserContext.Provider value={{ 
      userSession, 
      login, 
      logout, 
      showGoogleLogin, 
      triggerGoogleLogin, 
      closeGoogleLogin 
    }}>
      {children}
    </UserContext.Provider>
  );
}; 