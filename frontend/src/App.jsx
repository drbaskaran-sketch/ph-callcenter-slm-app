import React, { useState } from 'react';
import Header from './components/Header';
import SLMMobileSimulator from './components/SLMMobileSimulator';
import LeadershipDashboard from './components/LeadershipDashboard';
import BranchMatrix from './components/BranchMatrix';

export default function App() {
  const [activeTab, setActiveTab] = useState('simulator');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between">
      <div>
        <Header activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <main className="pb-12">
          {activeTab === 'simulator' && <SLMMobileSimulator />}
          {activeTab === 'dashboard' && <LeadershipDashboard />}
          {activeTab === 'branches' && <BranchMatrix />}
        </main>
      </div>

      <footer className="bg-slate-900 border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-400">
        <p>© 2026 Prashanth Hospitals • Call Center & SLM Mobile Platform (`ph-callcenter-slm-app`). All rights reserved.</p>
      </footer>
    </div>
  );
}
