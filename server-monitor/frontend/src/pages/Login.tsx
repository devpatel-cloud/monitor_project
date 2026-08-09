import React, { useState } from 'react';
import { Server, Lock, User as UserIcon } from 'lucide-react';
import api from '../api/client';

interface LoginProps {
  onLoginSuccess: (token: string, username: string) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const res = await api.post('/auth/login', formData);
      if (res.data?.access_token) {
        localStorage.setItem('server_monitor_token', res.data.access_token);
        onLoginSuccess(res.data.access_token, res.data.username);
      }
    } catch (err: any) {
      setError('Invalid username or password credentials.');
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
      <div className="card" style={{ width: 380, padding: '2.5rem 2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <Server size={42} style={{ color: 'var(--accent-primary)', marginBottom: '0.5rem' }} />
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Linux Server Monitor</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Rocky Linux 9 Host Authentication</p>
        </div>

        {error && (
          <div style={{ padding: '0.75rem', borderRadius: 8, backgroundColor: 'var(--color-critical-bg)', color: 'var(--color-critical)', fontSize: '0.85rem', marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Username
            </label>
            <div style={{ position: 'relative' }}>
              <UserIcon size={18} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.6rem 0.6rem 2.2rem',
                  borderRadius: 8,
                  border: '1px solid var(--border-color)',
                  backgroundColor: 'var(--bg-primary)',
                  color: 'var(--text-main)'
                }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.6rem 0.6rem 2.2rem',
                  borderRadius: 8,
                  border: '1px solid var(--border-color)',
                  backgroundColor: 'var(--bg-primary)',
                  color: 'var(--text-main)'
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            style={{
              width: '100%',
              padding: '0.75rem',
              borderRadius: 8,
              backgroundColor: 'var(--accent-primary)',
              color: '#FFFFFF',
              border: 'none',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Sign In to Dashboard
          </button>
        </form>
      </div>
    </div>
  );
};
