import React from 'react';
import { PhoneCall, Building2, Smartphone, Activity, UserCircle, LogOut, Users, ShieldAlert, MessageSquare } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, user, onLogout }) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          
          {/* Logo & Brand Title */}
          <div className="flex items-center space-x-3.5">
            <div className="w-11 h-11 rounded-xl bg-teal-700 p-0.5 shadow-md flex items-center justify-center">
              <div className="w-full h-full bg-teal-800 rounded-[10px] flex items-center justify-center text-white font-black text-xl">
                PH
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
                  PRASHANTH <span className="text-teal-700">HOSPITALS</span>
                </h1>
                <span className="bg-red-50 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-red-200 uppercase">
                  WE CARE FOR U
                </span>
              </div>
              <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                <PhoneCall className="w-3.5 h-3.5 text-teal-600" />
                Kolathur Central Call Center Hub (XTEND Engine) & Multi-Branch SLM Platform
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center space-x-1 bg-slate-100 p-1.5 rounded-xl border border-slate-200">
            <button
              onClick={() => setActiveTab('simulator')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'simulator'
                  ? 'bg-teal-700 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
              }`}
            >
              <Smartphone className="w-4 h-4" />
              <span>SLM Mobile App</span>
            </button>

            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-teal-700 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Leadership Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab('branches')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'branches'
                  ? 'bg-teal-700 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
              }`}
            >
              <Building2 className="w-4 h-4" />
              <span>Branch Matrix</span>
            </button>

            <button
              onClick={() => setActiveTab('users')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'users'
                  ? 'bg-teal-700 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>User Master</span>
            </button>

            <button
              onClick={() => setActiveTab('sla')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'sla'
                  ? 'bg-teal-700 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
              }`}
            >
              <ShieldAlert className="w-4 h-4" />
              <span>SLA Governance</span>
            </button>

            <button
              onClick={() => setActiveTab('reports')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'reports'
                  ? 'bg-teal-700 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Notifications & Reports</span>
            </button>
          </div>

          {/* Logged-in user & logout */}
          {user && (
            <div className="flex items-center gap-3 bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
                <UserCircle className="w-4 h-4 text-teal-700" />
                <span>{user.username}</span>
                <span className="text-[10px] text-slate-400 font-semibold uppercase">({user.role})</span>
              </div>
              <button
                onClick={onLogout}
                title="Log out"
                className="flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-red-700 transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Logout</span>
              </button>
            </div>
          )}

        </div>
      </div>
    </header>
  );
}
