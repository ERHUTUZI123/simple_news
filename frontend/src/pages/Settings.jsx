import React from "react";

export default function Settings() {
  return (
    <div className="news-container">
      <h1 style={{
        fontSize: "2rem",
        marginBottom: "2rem",
        textAlign: "center",
        color: "var(--text-color)",
        fontFamily: "var(--font-mono)",
      }}>
        Settings
      </h1>
      <div style={{
        maxWidth: "600px",
        margin: "0 auto",
        padding: "2rem",
        background: "rgba(255, 255, 255, 0.05)",
        borderRadius: "0.5rem",
        border: "1px solid var(--border-color)",
      }}>
        <h2 style={{
          fontSize: "1.5rem",
          marginBottom: "1rem",
          color: "var(--text-color)",
          fontFamily: "var(--font-mono)",
        }}>
          Preferences
        </h2>
        <p style={{
          color: "var(--secondary-color)",
          fontSize: "1rem",
          fontFamily: "var(--font-mono)",
          lineHeight: "1.6",
        }}>
          Settings and preferences will be available here.
        </p>
      </div>
    </div>
  );
} 