import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Navigation() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const location = useLocation();

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    // 这里可以添加主题切换逻辑
    document.documentElement.classList.toggle('light-mode');
  };

  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      height: '3.5rem',
      background: 'var(--bg-color)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 1rem',
      zIndex: 1000,
      fontFamily: 'var(--font-mono)',
      fontSize: '0.875rem',
    }}>
      {/* 左侧 Logo */}
      <Link 
        to="/" 
        style={{
          color: 'var(--text-color)',
          textDecoration: 'none',
          fontWeight: '600',
          fontSize: '1rem',
          letterSpacing: '0.05em',
        }}
      >
        ONEMINEWS
      </Link>

      {/* 中间空白 */}
      <div style={{ flex: 1 }}></div>

      {/* 右侧导航按钮 */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1.5rem',
      }}>
        <Link 
          to="/" 
          style={{
            color: location.pathname === '/' ? 'var(--highlight-color)' : 'var(--text-color)',
            textDecoration: 'none',
            padding: '0.5rem 0.75rem',
            borderRadius: '0.25rem',
            transition: 'all 0.2s ease',
            minHeight: '2.75rem',
            display: 'flex',
            alignItems: 'center',
          }}
          onMouseEnter={(e) => {
            if (location.pathname !== '/') {
              e.target.style.color = 'var(--link-color)';
              e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
            }
          }}
          onMouseLeave={(e) => {
            if (location.pathname !== '/') {
              e.target.style.color = 'var(--text-color)';
              e.target.style.backgroundColor = 'transparent';
            }
          }}
        >
          Home
        </Link>

        <Link 
          to="/saved" 
          style={{
            color: location.pathname === '/saved' ? 'var(--highlight-color)' : 'var(--text-color)',
            textDecoration: 'none',
            padding: '0.5rem 0.75rem',
            borderRadius: '0.25rem',
            transition: 'all 0.2s ease',
            minHeight: '2.75rem',
            display: 'flex',
            alignItems: 'center',
          }}
          onMouseEnter={(e) => {
            if (location.pathname !== '/saved') {
              e.target.style.color = 'var(--link-color)';
              e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
            }
          }}
          onMouseLeave={(e) => {
            if (location.pathname !== '/saved') {
              e.target.style.color = 'var(--text-color)';
              e.target.style.backgroundColor = 'transparent';
            }
          }}
        >
          Saved
        </Link>

        <Link 
          to="/settings" 
          style={{
            color: location.pathname === '/settings' ? 'var(--highlight-color)' : 'var(--text-color)',
            textDecoration: 'none',
            padding: '0.5rem 0.75rem',
            borderRadius: '0.25rem',
            transition: 'all 0.2s ease',
            minHeight: '2.75rem',
            display: 'flex',
            alignItems: 'center',
          }}
          onMouseEnter={(e) => {
            if (location.pathname !== '/settings') {
              e.target.style.color = 'var(--link-color)';
              e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
            }
          }}
          onMouseLeave={(e) => {
            if (location.pathname !== '/settings') {
              e.target.style.color = 'var(--text-color)';
              e.target.style.backgroundColor = 'transparent';
            }
          }}
        >
          Settings
        </Link>

        <button
          onClick={toggleDarkMode}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-color)',
            fontSize: '1rem',
            cursor: 'pointer',
            padding: '0.5rem 0.75rem',
            borderRadius: '0.25rem',
            transition: 'all 0.2s ease',
            minHeight: '2.75rem',
            minWidth: '2.75rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onMouseEnter={(e) => {
            e.target.style.color = 'var(--link-color)';
            e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
          }}
          onMouseLeave={(e) => {
            e.target.style.color = 'var(--text-color)';
            e.target.style.backgroundColor = 'transparent';
          }}
        >
          🌓
        </button>
      </div>
    </nav>
  );
} 