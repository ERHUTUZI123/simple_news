// frontend/src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Navigation from "./components/Navigation";
import PageTitle from "./components/PageTitle";
import Home from "./pages/Home";
import Saved from "./pages/Saved";
import Settings from "./pages/Settings";
import Success from "./pages/Success";
import Cancel from "./pages/Cancel";
import Article from "./pages/Article";

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
    </Router>
  );
}