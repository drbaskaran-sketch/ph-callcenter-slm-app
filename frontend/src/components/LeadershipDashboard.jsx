import React, { useState, useEffect } from 'react';
import { PRASHANTH_BRANCHES } from '../data/mockData';
import { Activity, Clock, CheckCircle2, TrendingUp, AlertTriangle, Building2, UserCheck, ShieldCheck, RefreshCw, Award } from 'lucide-react';

const API_BASE = '/api/v1';

export default function LeadershipDashboard() {
  const [metrics, setMetrics] = useState({
    totalInquiriesToday: 401,
    avgFirstResponseTatMins: 9.2,
    surgeriesAndSlotsFixed: 128,
    conversionRate: '68%',
    slaBreachAlerts: 2,
    branchesCount: 7,
    activeSlmsCount: 5
  });
  
  const [slms, setSlms] = useState([
    { id: 'slm-101', name: 'Vijay Kumar', department: 'Cardiology', branchCode: 'KOL', phone: '+91 98400 11111', activeLeads: 8, avgTatMins: 8.4, status: 'ON_DUTY', score: 96.5 },
    { id: 'slm-102', name: 'Anitha Ramesh', department: 'IVF & Fertility', branchCode: 'CHP', phone: '+91 94440 22222', activeLeads: 6, avgTatMins: 6.2, status: 'ON_DUTY', score: 98.0 },
    { id: 'slm-103', name: 'Suresh Babu', department: 'Orthopedics', branchCode: 'VEL', phone: '+91 98840 33333', activeLeads: 11, avgTatMins: 11.1, status: 'ON_DUTY', score: 91.2 },
    { id: 'slm-104', name: 'Priya Dharshini', department: 'Obstetrics & Gynecology', branchCode: 'GUM', phone: '+91 97900 44444', activeLeads: 4, avgTatMins: 7.5, status: 'ON_DUTY', score: 94.8 },
    { id: 'slm-105', name: 'Rajesh Kannan', department: 'Nephrology & Urology', branchCode: 'KOL', phone: '+91 98410 55555', activeLeads: 7, avgTatMins: 14.2, status: 'ON_DUTY', score: 88.0 }
  ]);

  const [branches, setBranches] = useState(PRASHANTH_BRANCHES);
  const [loading, setLoading] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [resMetrics, resSlms, resBranches] = await Promise.all([
        fetch(`${API_BASE}/analytics/overview`),
        fetch(`${API_BASE}/slms`),
        fetch(`${API_BASE}/branches`)
      ]);

      if (resMetrics.ok) {
        const d = await resMetrics.json();
        setMetrics(d);
      }
      if (resSlms.ok) {
        const d = await resSlms.json();
        if (d.slms) setSlms(d.slms);
      }
      if (resBranches.ok) {
        const d = await resBranches.json();
        if (d.branches) setBranches(d.branches);
      }
    } catch (e) {
      console.log('Using local dashboard state fallback');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000);
    return () => clearInterval(interval);
  }, []);

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
          <button
            onClick={fetchDashboardData}
            className="text-slate-400 hover:text-teal-400 flex items-center gap-1 font-semibold"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Now</span>
          </button>

          <span className="bg-emerald-950 text-emerald-300 font-bold px-3 py-1.5 rounded-lg border border-emerald-800 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            XTEND DB2 Live Syncing (Every 5s)
          </span>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Total Inquiries Today</span>
            <Building2 className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{metrics.totalInquiriesToday}</p>
          <span className="text-[11px] text-emerald-400 font-semibold mt-1 block">
            +14% vs yesterday
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Avg First Response TAT</span>
            <Clock className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-2xl font-extrabold text-teal-400">{metrics.avgFirstResponseTatMins} Mins</p>
          <span className="text-[11px] text-teal-300 font-semibold mt-1 block">
            Target: &lt; 15 Mins (SLA Met)
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Surgeries & Slots Fixed</span>
            <UserCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-extrabold text-emerald-400">{metrics.surgeriesAndSlotsFixed}</p>
          <span className="text-[11px] text-emerald-400 font-semibold mt-1 block">
            {metrics.conversionRate} Conversion Rate
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">SLA Breach Alerts</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-extrabold text-amber-400">{metrics.slaBreachAlerts}</p>
          <span className="text-[11px] text-amber-300 font-semibold mt-1 block">
            Auto-Escalated to Branch Head
          </span>
        </div>

      </div>

      {/* SLM Performance Roster */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-md">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-teal-400" />
            Service Line Manager (SLM) Response SLA & Scorecard
          </h3>
          <span className="text-xs text-slate-400">5 Active SLMs on Duty</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">SLM Name</th>
                <th className="py-3 px-4">Specialty Department</th>
                <th className="py-3 px-4">Branch Code</th>
                <th className="py-3 px-4 text-center">Active Leads</th>
                <th className="py-3 px-4 text-center">Avg Response TAT</th>
                <th className="py-3 px-4 text-right">SLA Scorecard</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {slms.map((slm) => (
                <tr key={slm.id} className="hover:bg-slate-950/50 transition-colors">
                  <td className="py-3 px-4 font-bold text-white flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-teal-950 border border-teal-800 text-teal-300 font-extrabold flex items-center justify-center text-[10px]">
                      {slm.name.charAt(0)}
                    </div>
                    <span>{slm.name}</span>
                  </td>
                  <td className="py-3 px-4 font-semibold text-teal-300">{slm.department}</td>
                  <td className="py-3 px-4 font-bold text-slate-400">{slm.branchCode}</td>
                  <td className="py-3 px-4 text-center font-bold text-white">{slm.activeLeads}</td>
                  <td className="py-3 px-4 text-center font-bold text-teal-400">{slm.avgTatMins} Mins</td>
                  <td className="py-3 px-4 text-right">
                    <span className="bg-emerald-950 text-emerald-300 font-extrabold text-[11px] px-2.5 py-0.5 rounded-full border border-emerald-800">
                      {slm.score}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Branch Breakdown Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-md">
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
              {branches.map((b) => (
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
