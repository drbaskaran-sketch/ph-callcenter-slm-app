import React, { useState } from 'react';
import Header from './components/Header';
import SLMMobileSimulator from './components/SLMMobileSimulator';
import LeadershipDashboard from './components/LeadershipDashboard';
import BranchMatrix from './components/BranchMatrix';

export default function App() {
  const [activeTab, setActiveTab] = useState('simulator');

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between">
      <div>
        <Header activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <main className="pb-12 pt-4">
          {activeTab === 'simulator' && <SLMMobileSimulator />}
          {activeTab === 'dashboard' && <LeadershipDashboard />}
          {activeTab === 'branches' && <BranchMatrix />}
        </main>
      </div>

      <footer className="bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-500 font-semibold shadow-xs">
        <p>© 2026 Prashanth Hospitals • Call Center & SLM Mobile Platform (`ph-callcenter-slm-app`). All rights reserved.</p>
      </footer>
    </div>
  );
}
