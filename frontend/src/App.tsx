import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './features/auth/hooks/useAuth';

// Placeholders for views
const Login = () => <div className="p-8"><h1>Login</h1></div>;
const Dashboard = () => <div className="p-8"><h1>Dashboard</h1><p>Welcome to the Document Intelligence Platform.</p></div>;
const DocumentUpload = () => <div className="p-8"><h1>Upload Document</h1></div>;
const Chat = () => <div className="p-8"><h1>RAG Chat</h1></div>;

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  return <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          <header style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)' }}>
            <strong>Document Intelligence</strong>
          </header>
          <main style={{ flex: 1, backgroundColor: 'var(--bg-primary)' }}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/upload" element={
                <ProtectedRoute>
                  <DocumentUpload />
                </ProtectedRoute>
              } />
              <Route path="/chat/:id" element={
                <ProtectedRoute>
                  <Chat />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
