import React, { useState, useEffect } from 'react';
import { ShieldAlert, Clock, AlertTriangle, CheckCircle, RefreshCw, Award, Zap, Building2, UserCheck, ChevronRight } from 'lucide-react';
import { apiFetch, API_BASE } from '../api';

export default function SLAGovernanceDashboard() {
  const [matrix, setMatrix] = useState({
    totalEnquiries: 457,
    tier1OnTime: 442,
    tier2BranchHead: 11,
    tier3Director: 4,
    slaComplianceRate: '96.7%',
    targetSlaMins: 15
  });

  const [scorecard, setScorecard] = useState([]);
  const [loading, setLoading] = useState(false);
  const [auditing, setAuditing] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const fetchSlaData = async () => {
    setLoading(true);
    try {
      const [resMatrix, resScorecard] = await Promise.all([
        apiFetch(`${API_BASE}/sla/matrix`),
        apiFetch(`${API_BASE}/sla/scorecard`)
      ]);

      if (resMatrix.ok) setMatrix(await resMatrix.json());
      if (resScorecard.ok) {
        const d = await resScorecard.json();
        if (d.scorecard) setScorecard(d.scorecard);
      }
    } catch (e) {
      console.log('Error fetching SLA governance data', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSlaData();
    const interval = setInterval(fetchSlaData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleRunSlaAudit = async () => {
    setAuditing(true);
    try {
      const res = await apiFetch(`${API_BASE}/sla/check-breaches`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setToastMessage(`⚡ SLA Audit Complete! ${data.message}`);
        setTimeout(() => setToastMessage(null), 4000);
        fetchSlaData();
      }
    } catch (e) {
      console.log('Error running SLA audit');
    } finally {
      setAuditing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">

      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-5 rounded-2xl shadow-sm">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-teal-700" />
            3-Tier SLA Escalation & SLM Performance Scorecards
          </h2>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Strict &lt;15 mins First Response TAT governance, automated Tier 2/3 leadership escalations, and weighted monthly SLM quality scorecards.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchSlaData}
            className="text-slate-600 hover:text-teal-700 flex items-center gap-1 font-bold bg-slate-100 px-3 py-2 rounded-xl border border-slate-200 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync SLA</span>
          </button>
          
          <button
            onClick={handleRunSlaAudit}
            disabled={auditing}
            className="bg-teal-700 hover:bg-teal-800 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition-all disabled:opacity-50"
          >
            <Zap className={`w-4 h-4 ${auditing ? 'animate-bounce' : ''}`} />
            <span>{auditing ? 'Auditing SLA...' : 'Run SLA Audit Now'}</span>
          </button>
        </div>
      </div>

      {/* Toast Alert */}
      {toastMessage && (
        <div className="bg-emerald-50 border border-emerald-300 text-emerald-900 px-4 py-3 rounded-xl text-xs font-extrabold flex items-center gap-2 shadow-xs">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 3-Tier SLA Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Overall Compliance */}
        <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Overall SLA Compliance</span>
            <CheckCircle className="w-4 h-4 text-teal-700" />
          </div>
          <p className="text-2xl font-black text-teal-800">{matrix.slaComplianceRate}</p>
          <span className="text-[11px] text-teal-800 font-bold mt-1 block">
            Target TAT: &lt; 15 Mins
          </span>
        </div>

        {/* Tier 1: On Time */}
        <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Tier 1 (&lt;15 Mins) On-Time</span>
            <Clock className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-black text-emerald-700">{matrix.tier1OnTime}</p>
          <span className="text-[11px] text-emerald-800 font-bold mt-1 block">
            Dispatched to On-Duty SLM
          </span>
        </div>

        {/* Tier 2: Branch Head Escalations */}
        <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Tier 2 (15-30 Mins) Escalated</span>
            <AlertTriangle className="w-4 h-4 text-amber-600" />
          </div>
          <p className="text-2xl font-black text-amber-700">{matrix.tier2BranchHead}</p>
          <span className="text-[11px] text-amber-800 font-bold mt-1 block">
            Escalated to Branch Head
          </span>
        </div>

        {/* Tier 3: Director Escalations */}
        <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Tier 3 (&gt;30 Mins) Critical</span>
            <ShieldAlert className="w-4 h-4 text-rose-600" />
          </div>
          <p className="text-2xl font-black text-rose-700">{matrix.tier3Director}</p>
          <span className="text-[11px] text-rose-800 font-bold mt-1 block">
            Escalated to Group COO & Ops Director
          </span>
        </div>

      </div>

      {/* 3-Tier Escalation Workflow Overview Banner */}
      <div className="bg-slate-900 text-white rounded-2xl p-5 shadow-sm space-y-3">
        <h3 className="text-sm font-extrabold flex items-center gap-2 text-teal-400">
          <Zap className="w-4 h-4" />
          Prashanth Hospitals Automated 3-Tier SLA Escalation Protocol
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-medium">
          <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
            <div className="font-extrabold text-emerald-400 mb-1">Tier 1: 0 — 15 Mins</div>
            <p className="text-slate-300">Call record ingested from XTEND DB2 Kolathur hub and dispatched via FCM Push to Department SLM mobile app.</p>
          </div>

          <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
            <div className="font-extrabold text-amber-400 mb-1">Tier 2: 15 — 30 Mins</div>
            <p className="text-slate-300">If first response unacknowledged &gt; 15 mins, SLA breach flag trips. Auto-escalated to Branch Head for intervention.</p>
          </div>

          <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
            <div className="font-extrabold text-rose-400 mb-1">Tier 3: &gt; 30 Mins</div>
            <p className="text-slate-300">Critical breach triggered. High-priority SMS/Email alert dispatched to Operations Director & Group COO.</p>
          </div>
        </div>
      </div>

      {/* Weighted SLM Monthly Scorecard Table */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Award className="w-4 h-4 text-teal-700" />
            Weighted SLM Monthly Performance Scorecard & Quality Audits
          </h3>
          <span className="text-[11px] text-slate-500 font-bold bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
            Weighted: 40% TAT + 35% Conv + 15% FCR + 10% Audit
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">SLM Rank & Name</th>
                <th className="py-3 px-4">Department & Branch</th>
                <th className="py-3 px-4">Calls Handled</th>
                <th className="py-3 px-4">Avg Response TAT</th>
                <th className="py-3 px-4">Conversion Rate</th>
                <th className="py-3 px-4">SLA Breaches</th>
                <th className="py-3 px-4">Overall Score</th>
                <th className="py-3 px-4 text-right">Performance Grade</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {scorecard.map((s, idx) => (
                <tr key={s.slmId} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 font-black text-[10px] flex items-center justify-center">
                        #{idx + 1}
                      </span>
                      <div>
                        <span className="font-extrabold text-slate-900 block">{s.name}</span>
                        <span className="text-[10px] text-teal-800 font-bold">{s.slmId}</span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-bold text-slate-800 block">{s.department}</span>
                    <span className="text-[10px] font-black text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200 mt-0.5 inline-block">{s.branchCode}</span>
                  </td>
                  <td className="py-3 px-4 font-extrabold text-slate-800">{s.totalHandled}</td>
                  <td className="py-3 px-4 font-bold text-teal-800">{s.avgTatMins} Mins</td>
                  <td className="py-3 px-4 font-extrabold text-emerald-800">{s.conversionRate}</td>
                  <td className="py-3 px-4">
                    <span className={`font-bold px-2 py-0.5 rounded ${s.slaBreaches > 0 ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'text-slate-500'}`}>
                      {s.slaBreaches}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-black text-teal-900 text-sm">
                    {s.score}%
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className={`font-black text-[10px] px-2.5 py-1 rounded-full border ${
                      s.grade.includes('A+') ? 'bg-emerald-50 text-emerald-800 border-emerald-300' :
                      s.grade.includes('A') ? 'bg-teal-50 text-teal-800 border-teal-300' :
                      'bg-slate-100 text-slate-700 border-slate-300'
                    }`}>
                      {s.grade}
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
