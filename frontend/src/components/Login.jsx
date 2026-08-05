import React, { useState } from 'react';
import { Lock, User, AlertCircle } from 'lucide-react';
import { login } from '../api';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(username, password);
      onLogin(user);
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-6">
          <div className="w-14 h-14 mx-auto rounded-xl bg-teal-700 p-0.5 shadow-md flex items-center justify-center">
            <div className="w-full h-full bg-teal-800 rounded-[10px] flex items-center justify-center text-white font-black text-2xl">
              PH
            </div>
          </div>
          <h1 className="text-xl font-extrabold text-slate-900 mt-3">
            PRASHANTH <span className="text-teal-700">HOSPITALS</span>
          </h1>
          <p className="text-xs text-slate-500 font-semibold mt-1">
            Call Center & SLM Mobile Platform — Sign In
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 space-y-4">
          {error && (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-xs font-bold px-3 py-2.5 rounded-xl">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1.5">Username</label>
            <div className="relative">
              <User className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
              <input
                type="text"
                autoFocus
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-900 pl-10 pr-4 py-2.5 rounded-xl focus:outline-none focus:border-teal-600 shadow-xs"
                placeholder="admin"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-900 pl-10 pr-4 py-2.5 rounded-xl focus:outline-none focus:border-teal-600 shadow-xs"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !username || !password}
            className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-2.5 rounded-xl shadow-xs transition-all text-sm disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="text-center text-[11px] text-slate-400 font-semibold mt-4">
          © 2026 Prashanth Hospitals — Internal Use Only
        </p>
      </div>
    </div>
  );
}
