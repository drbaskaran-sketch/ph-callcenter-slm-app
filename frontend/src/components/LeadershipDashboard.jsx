import React, { useState, useEffect } from 'react';
import { PRASHANTH_BRANCHES, MOCK_ENQUIRIES } from '../data/mockData';
import { Activity, Clock, Building2, UserCheck, AlertTriangle, RefreshCw, Award, PhoneCall, ListOrdered, FileText } from 'lucide-react';
import { apiFetch, API_BASE } from '../api';

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
  const [enquiries, setEnquiries] = useState(MOCK_ENQUIRIES);
  const [loading, setLoading] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [resMetrics, resSlms, resBranches, resEnq] = await Promise.all([
        apiFetch(`${API_BASE}/analytics/overview`),
        apiFetch(`${API_BASE}/slms`),
        apiFetch(`${API_BASE}/branches`),
        apiFetch(`${API_BASE}/enquiries`)
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
      if (resEnq.ok) {
        const d = await resEnq.json();
        if (d.enquiries) setEnquiries(d.enquiries);
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
      
      {/* Top Banner - White Mode */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-5 rounded-2xl shadow-sm">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-teal-700" />
            Leadership & SLM Call Query Performance Dashboard
          </h2>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Real-time monitoring of XTEND Call Center Ingestion (Kolathur Hub), SLM First Response TAT, Doctor Appointments & Surgery Conversions.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <button
            onClick={fetchDashboardData}
            className="text-slate-600 hover:text-teal-700 flex items-center gap-1 font-bold bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Now</span>
          </button>

          <span className="bg-emerald-50 text-emerald-800 font-bold px-3 py-1.5 rounded-lg border border-emerald-200 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-ping"></span>
            XTEND DB2 Live Syncing
          </span>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Total Inquiries Today</span>
            <Building2 className="w-4 h-4 text-teal-700" />
          </div>
          <p className="text-2xl font-black text-slate-900">{metrics.totalInquiriesToday}</p>
          <span className="text-[11px] text-emerald-700 font-bold mt-1 block">
            +14% vs yesterday
          </span>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Avg First Response TAT</span>
            <Clock className="w-4 h-4 text-teal-700" />
          </div>
          <p className="text-2xl font-black text-teal-700">{metrics.avgFirstResponseTatMins} Mins</p>
          <span className="text-[11px] text-teal-800 font-bold mt-1 block">
            Target: &lt; 15 Mins (SLA Met)
          </span>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Surgeries & Slots Fixed</span>
            <UserCheck className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-black text-emerald-700">{metrics.surgeriesAndSlotsFixed}</p>
          <span className="text-[11px] text-emerald-800 font-bold mt-1 block">
            {metrics.conversionRate} Conversion Rate
          </span>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">SLA Breach Alerts</span>
            <AlertTriangle className="w-4 h-4 text-amber-600" />
          </div>
          <p className="text-2xl font-black text-amber-700">{metrics.slaBreachAlerts}</p>
          <span className="text-[11px] text-amber-800 font-bold mt-1 block">
            Auto-Escalated to Branch Head
          </span>
        </div>

      </div>

      {/* SLM Action on Call and Patient Queries Detailed Table */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <PhoneCall className="w-4 h-4 text-teal-700" />
            SLM Action Details on Calls & Patient Queries Audit Log
          </h3>
          <span className="text-xs text-slate-500 font-bold bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
            {enquiries.length} Registered Queries
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Call Ref & Time</th>
                <th className="py-3 px-4">Patient & Phone</th>
                <th className="py-3 px-4">Branch & Dept</th>
                <th className="py-3 px-4">Query Type</th>
                <th className="py-3 px-4">Assigned SLM & Duration</th>
                <th className="py-3 px-4">SLM Action / Remarks</th>
                <th className="py-3 px-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {enquiries.map((enq) => (
                <tr key={enq.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4">
                    <span className="font-extrabold text-teal-800 block text-[11px]">{enq.id}</span>
                    <span className="text-[10px] text-slate-400 font-bold">{enq.callStartTime || '17:25:10'} ({enq.timeAgo})</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-extrabold text-slate-900 block">{enq.patientName}</span>
                    <span className="text-[10px] text-slate-500">{enq.phone}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-black text-slate-800 bg-slate-100 px-2 py-0.5 rounded text-[10px] border border-slate-200">{enq.branchCode}</span>
                    <span className="text-[11px] text-teal-800 font-bold block mt-0.5">{enq.department}</span>
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-800">{enq.enquiryType}</td>
                  <td className="py-3 px-4">
                    <span className="font-bold text-slate-900 block">{enq.assignedSLM}</span>
                    <span className="text-[10px] font-bold text-emerald-800 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 mt-0.5 inline-block">
                      ⏱ {enq.callDuration || '02m 14s'}
                    </span>
                  </td>
                  <td className="py-3 px-4 max-w-xs text-[11px] text-slate-600 font-normal">
                    {enq.remarks || enq.notes}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className="bg-teal-50 text-teal-800 font-black text-[10px] px-2.5 py-1 rounded-full border border-teal-200">
                      {enq.status.replace('_', ' ')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* SLM Performance Roster */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Award className="w-4 h-4 text-teal-700" />
            Service Line Manager (SLM) Response SLA & Scorecard
          </h3>
          <span className="text-xs text-slate-500 font-bold">5 Active SLMs on Duty</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">SLM Name</th>
                <th className="py-3 px-4">Specialty Department</th>
                <th className="py-3 px-4">Branch Code</th>
                <th className="py-3 px-4 text-center">Active Leads</th>
                <th className="py-3 px-4 text-center">Avg Response TAT</th>
                <th className="py-3 px-4 text-right">SLA Scorecard</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {slms.map((slm) => (
                <tr key={slm.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-teal-100 text-teal-800 border border-teal-300 font-black flex items-center justify-center text-[10px]">
                      {slm.name.charAt(0)}
                    </div>
                    <span>{slm.name}</span>
                  </td>
                  <td className="py-3 px-4 font-bold text-teal-800">{slm.department}</td>
                  <td className="py-3 px-4 font-black text-slate-600">{slm.branchCode}</td>
                  <td className="py-3 px-4 text-center font-extrabold text-slate-900">{slm.activeLeads}</td>
                  <td className="py-3 px-4 text-center font-extrabold text-teal-700">{slm.avgTatMins} Mins</td>
                  <td className="py-3 px-4 text-right">
                    <span className="bg-emerald-50 text-emerald-800 font-black text-[11px] px-2.5 py-0.5 rounded-full border border-emerald-200">
                      {slm.score}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
