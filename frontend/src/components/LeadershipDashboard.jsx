import React from 'react';
import { PRASHANTH_BRANCHES } from '../data/mockData';
import { Activity, Clock, CheckCircle2, TrendingUp, AlertTriangle, Building2, UserCheck } from 'lucide-react';

export default function LeadershipDashboard() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-5 rounded-2xl">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-teal-400" />
            Leadership & Branch Performance Dashboard
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time monitoring of XTEND Call Center Ingestion (Kolathur Hub), SLM First Response TAT, Doctor Appointments & Surgery Conversions.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="bg-emerald-950 text-emerald-300 font-bold px-3 py-1.5 rounded-lg border border-emerald-800 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            XTEND DB2 Live Syncing (Every 5s)
          </span>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Total Inquiries Today</span>
            <Building2 className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">401</p>
          <span className="text-[11px] text-emerald-400 font-semibold mt-1 block">
            +14% vs yesterday
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Avg First Response TAT</span>
            <Clock className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-2xl font-extrabold text-teal-400">9.2 Mins</p>
          <span className="text-[11px] text-teal-300 font-semibold mt-1 block">
            Target: &lt; 15 Mins (SLA Met)
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Surgeries & Slots Fixed</span>
            <UserCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-extrabold text-emerald-400">128</p>
          <span className="text-[11px] text-emerald-400 font-semibold mt-1 block">
            68% Conversion Rate
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">SLA Breach Alerts</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-extrabold text-amber-400">2</p>
          <span className="text-[11px] text-amber-300 font-semibold mt-1 block">
            Auto-Escalated to Branch Head
          </span>
        </div>

      </div>

      {/* Branch Breakdown Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Building2 className="w-4 h-4 text-teal-400" />
          Prashanth Hospitals Branch Performance & Lead Routing Matrix
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Branch Code</th>
                <th className="py-3 px-4">Branch Name</th>
                <th className="py-3 px-4">City / Region</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Leads Ingested Today</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {PRASHANTH_BRANCHES.map((b) => (
                <tr key={b.id} className="hover:bg-slate-950/50 transition-colors">
                  <td className="py-3 px-4 font-bold text-teal-400">{b.code}</td>
                  <td className="py-3 px-4 font-semibold text-white">{b.name}</td>
                  <td className="py-3 px-4 text-slate-400">{b.city}</td>
                  <td className="py-3 px-4">
                    <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                      b.status === 'ACTIVE'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}>
                      {b.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-extrabold text-white">{b.leadsToday}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
