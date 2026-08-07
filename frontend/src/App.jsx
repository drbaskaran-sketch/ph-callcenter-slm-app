import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Login from './components/Login';
import SLMMobileSimulator from './components/SLMMobileSimulator';
import LeadershipDashboard from './components/LeadershipDashboard';
import BranchMatrix from './components/BranchMatrix';
import UserManagement from './components/UserManagement';
import SLAGovernanceDashboard from './components/SLAGovernanceDashboard';
import NotificationsAndReports from './components/NotificationsAndReports';
import { getToken, getStoredUser, clearSession } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('simulator');
  const [user, setUser] = useState(() => (getToken() ? getStoredUser() : null));

  const handleLogout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  // apiFetch() dispatches this if the backend ever responds 401 (expired or
  // invalid token), so an expired session drops straight back to Login
  // instead of leaving the dashboard silently broken.
  useEffect(() => {
    window.addEventListener('ph-auth-expired', handleLogout);
    return () => window.removeEventListener('ph-auth-expired', handleLogout);
  }, [handleLogout]);

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  const isAdmin = user.role === 'ADMIN';
  const isLeadership = isAdmin || user.role === 'SUPERVISOR';

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between">
      <div>
        <Header activeTab={activeTab} setActiveTab={setActiveTab} user={user} onLogout={handleLogout} />

        <main className="pb-12 pt-4">
          {activeTab === 'simulator' && <SLMMobileSimulator />}
          {activeTab === 'dashboard' && isLeadership && <LeadershipDashboard />}
          {activeTab === 'branches' && isAdmin && <BranchMatrix />}
          {activeTab === 'users' && isAdmin && <UserManagement />}
          {activeTab === 'sla' && isLeadership && <SLAGovernanceDashboard />}
          {activeTab === 'reports' && isLeadership && <NotificationsAndReports />}
        </main>
      </div>

      <footer className="bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-500 font-semibold shadow-xs">
        <p>© 2026 Prashanth Hospitals • Call Center & SLM Mobile Platform (`ph-callcenter-slm-app`). All rights reserved.</p>
      </footer>
    </div>
  );
}
