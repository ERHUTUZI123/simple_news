import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export default function PageTitle() {
  const location = useLocation();

  useEffect(() => {
    const getPageTitle = () => {
      const path = location.pathname;
      
      if (path === '/') {
        return 'OneMinNews - Tech News Aggregator';
      } else if (path === '/saved') {
        return 'Saved Articles - OneMinNews';
      } else if (path === '/settings') {
        return 'Settings - OneMinNews';
      } else if (path.startsWith('/article/')) {
        return 'Article Summary - OneMinNews';
      } else if (path.startsWith('/summary/')) {
        return 'Article Summary - OneMinNews';
      } else if (path === '/success') {
        return 'Payment Success - OneMinNews';
      } else if (path === '/cancel') {
        return 'Payment Cancelled - OneMinNews';
      } else {
        return 'OneMinNews - Tech News Aggregator';
      }
    };

    document.title = getPageTitle();
  }, [location.pathname]);

  return null; // This component doesn't render any content
} 