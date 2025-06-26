// frontend/src/App.jsx
import React, { useContext } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { GoogleLogin } from '@react-oauth/google';

import Navigation from "./components/Navigation";
import PageTitle from "./components/PageTitle";
import Home from "./pages/Home";
import Saved from "./pages/Saved";
import Settings from "./pages/Settings";
import Success from "./pages/Success";
import Cancel from "./pages/Cancel";
import Article from "./pages/Article";
import { UserContext } from "./context/UserContext";

// 生成UUID的函数
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function GoogleLoginModal() {
  const { showGoogleLogin, closeGoogleLogin, login } = useContext(UserContext);

  const handleLoginSuccess = (credentialResponse) => {
    try {
      // Parse JWT token to get user info
      const base64Url = credentialResponse.credential.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      const userInfo = JSON.parse(jsonPayload);
      
      // 使用Google的sub字段作为用户ID，确保是UUID格式
      const userId = userInfo.sub || generateUUID();
      
      // 先保存用户信息到数据库
      saveUserToDatabase(userInfo, userId).then(() => {
        // 然后更新前端状态
        login({...userInfo, id: userId}, credentialResponse.credential);
        closeGoogleLogin();
      }).catch(error => {
        console.error('Error saving user to database:', error);
        alert('Login failed. Please try again.');
      });
    } catch (error) {
      console.error('Error parsing JWT token:', error);
      alert('Login failed. Please try again.');
    }
  };

  const saveUserToDatabase = async (userInfo, userId) => {
    try {
      const response = await fetch('https://simplenews-production.up.railway.app/api/auth/save-user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: userId,
          email: userInfo.email,
          name: userInfo.name,
          picture: userInfo.picture
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to save user to database');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error saving user:', error);
      throw error;
    }
  };

  if (!showGoogleLogin) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
    }}>
      <div style={{
        background: '#fff',
        border: '1px solid #000',
        borderRadius: '8px',
        padding: '2rem',
        boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
        minWidth: '300px',
        maxWidth: '400px',
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
        }}>
          <h3 style={{
            fontFamily: 'monospace',
            fontSize: '1.1rem',
            color: '#000',
            margin: 0,
          }}>
            Sign in with Google
          </h3>
          <button
            onClick={closeGoogleLogin}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#666',
              padding: '0',
              width: '24px',
              height: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            ×
          </button>
        </div>
        <GoogleLogin
          onSuccess={handleLoginSuccess}
          onError={() => {
            alert("Google login failed");
          }}
          theme="outline"
          size="large"
          width="100%"
          text="signin_with"
          shape="rectangular"
        />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <PageTitle />
      <Navigation />
      <div style={{ paddingTop: '3.5rem' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/saved" element={<Saved />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/success" element={<Success />} />
          <Route path="/cancel" element={<Cancel />} />
          <Route path="/article/:id" element={<Article />} />
          <Route path="/summary/:slug" element={<Article />} />
        </Routes>
      </div>
      <GoogleLoginModal />
      <ToastContainer 
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </Router>
  );
}