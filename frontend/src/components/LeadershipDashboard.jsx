import React, { useState, useEffect } from 'react';
import { PRASHANTH_BRANCHES, MOCK_ENQUIRIES } from '../data/mockData';
import { Activity, Clock, Building2, UserCheck, AlertTriangle, RefreshCw, Award, PhoneCall, Stethoscope, Users, PieChart, ChevronRight } from 'lucide-react';
import { apiFetch, API_BASE } from '../api';

export default function LeadershipDashboard() {
  const [activeSubTab, setActiveSubTab] = useState('overview'); // 'overview' | 'specialities' | 'doctors' | 'agents'
  
  const [metrics, setMetrics] = useState({
    totalInquiriesToday: 401,
    avgFirstResponseTatMins: 9.2,
    surgeriesAndSlotsFixed: 128,
    conversionRate: '68%',
    slaBreachAlerts: 2,
    branchesCount: 7,
    activeSlmsCount: 5
  });

  const [specialities, setSpecialities] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [agents, setAgents] = useState([]);
  const [branches, setBranches] = useState(PRASHANTH_BRANCHES);
  const [enquiries, setEnquiries] = useState(MOCK_ENQUIRIES);
  const [loading, setLoading] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [resMetrics, resSpec, resDocs, resAgents, resBranches, resEnq] = await Promise.all([
        apiFetch(`${API_BASE}/analytics/overview`),
        apiFetch(`${API_BASE}/analytics/specialities`),
        apiFetch(`${API_BASE}/analytics/doctors`),
        apiFetch(`${API_BASE}/analytics/agents`),
        apiFetch(`${API_BASE}/branches`),
        apiFetch(`${API_BASE}/enquiries`)
      ]);

      if (resMetrics.ok) setMetrics(await resMetrics.json());
      if (resSpec.ok) {
        const d = await resSpec.json();
        if (d.specialities) setSpecialities(d.specialities);
      }
      if (resDocs.ok) {
        const d = await resDocs.json();
        if (d.doctors) setDoctors(d.doctors);
      }
      if (resAgents.ok) {
        const d = await resAgents.json();
        if (d.agents) setAgents(d.agents);
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
            Leadership Analytics & Operations Governance Dashboard
          </h2>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Real-time monitoring of XTEND Call Ingestion (Kolathur Hub), Speciality Drill-downs, Doctor Conversions & SLM Performance.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <button
            onClick={fetchDashboardData}
            className="text-slate-600 hover:text-teal-700 flex items-center gap-1 font-bold bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Analytics</span>
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

      {/* Analytics Sub Navigation */}
      <div className="flex border-b border-slate-200 gap-6 text-sm font-bold">
        <button
          onClick={() => setActiveSubTab('overview')}
          className={`pb-3 flex items-center gap-2 border-b-2 transition-colors ${
            activeSubTab === 'overview' ? 'border-teal-700 text-teal-800' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <PhoneCall className="w-4 h-4" />
          <span>Call Audit Trail</span>
        </button>

        <button
          onClick={() => setActiveSubTab('specialities')}
          className={`pb-3 flex items-center gap-2 border-b-2 transition-colors ${
            activeSubTab === 'specialities' ? 'border-teal-700 text-teal-800' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <PieChart className="w-4 h-4" />
          <span>Speciality-wise Drill-down ({specialities.length})</span>
        </button>

        <button
          onClick={() => setActiveSubTab('doctors')}
          className={`pb-3 flex items-center gap-2 border-b-2 transition-colors ${
            activeSubTab === 'doctors' ? 'border-teal-700 text-teal-800' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Stethoscope className="w-4 h-4" />
          <span>Doctor-wise Analytics ({doctors.length})</span>
        </button>

        <button
          onClick={() => setActiveSubTab('agents')}
          className={`pb-3 flex items-center gap-2 border-b-2 transition-colors ${
            activeSubTab === 'agents' ? 'border-teal-700 text-teal-800' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Agent Performance ({agents.length})</span>
        </button>
      </div>

      {/* SUB-TAB 1: OVERVIEW CALL AUDIT TRAIL */}
      {activeSubTab === 'overview' && (
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
      )}

      {/* SUB-TAB 2: SPECIALITY DRILL-DOWN */}
      {activeSubTab === 'specialities' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <PieChart className="w-4 h-4 text-teal-700" />
              Speciality / Department-wise Inquiry & Conversion Matrix
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Medical Speciality</th>
                  <th className="py-3 px-4">Total Inquiries</th>
                  <th className="py-3 px-4">Surgeries / Slots Fixed</th>
                  <th className="py-3 px-4">Pending Leads</th>
                  <th className="py-3 px-4">Conversion Rate</th>
                  <th className="py-3 px-4">Avg Response TAT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {specialities.map((sp) => (
                  <tr key={sp.speciality} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-extrabold text-slate-900 flex items-center gap-2">
                      <ChevronRight className="w-3.5 h-3.5 text-teal-700" />
                      <span>{sp.speciality}</span>
                    </td>
                    <td className="py-3 px-4 font-extrabold text-slate-800">{sp.totalInquiries}</td>
                    <td className="py-3 px-4 font-extrabold text-emerald-800">{sp.surgeriesAndAppointmentsFixed}</td>
                    <td className="py-3 px-4 font-bold text-amber-700">{sp.pendingLeads}</td>
                    <td className="py-3 px-4 font-black text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 inline-block my-2">
                      {sp.conversionRate}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-700">{sp.avgTatMins} Mins</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* SUB-TAB 3: DOCTOR-WISE ANALYTICS */}
      {activeSubTab === 'doctors' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Stethoscope className="w-4 h-4 text-teal-700" />
              Doctor-wise Consultations & Surgical Booking Analytics
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Doctor Name</th>
                  <th className="py-3 px-4">Speciality Department</th>
                  <th className="py-3 px-4">Patient Consultations</th>
                  <th className="py-3 px-4">Surgeries / Slots Booked</th>
                  <th className="py-3 px-4">Conversion Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {doctors.map((d) => (
                  <tr key={d.doctorName} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-extrabold text-slate-900">{d.doctorName}</td>
                    <td className="py-3 px-4 font-bold text-teal-800">{d.department}</td>
                    <td className="py-3 px-4 font-extrabold text-slate-800">{d.consultations}</td>
                    <td className="py-3 px-4 font-extrabold text-emerald-800">{d.surgeriesFixed}</td>
                    <td className="py-3 px-4">
                      <span className="font-black text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        {d.conversionRate}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* SUB-TAB 4: AGENT PERFORMANCE SCORECARDS */}
      {activeSubTab === 'agents' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Users className="w-4 h-4 text-teal-700" />
              SLM Agent Performance & Governance Scorecards
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">SLM Agent Name</th>
                  <th className="py-3 px-4">Department & Branch</th>
                  <th className="py-3 px-4">Calls Handled</th>
                  <th className="py-3 px-4">Conversions</th>
                  <th className="py-3 px-4">Avg Response TAT</th>
                  <th className="py-3 px-4">SLA Breaches</th>
                  <th className="py-3 px-4 text-right">Monthly Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {agents.map((ag) => (
                  <tr key={ag.slmId} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-extrabold text-slate-900 block">{ag.name}</span>
                      <span className="text-[10px] text-teal-800 font-bold">{ag.slmId}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-800 block">{ag.department}</span>
                      <span className="text-[10px] font-black text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200 mt-0.5 inline-block">{ag.branchCode}</span>
                    </td>
                    <td className="py-3 px-4 font-extrabold text-slate-800">{ag.callsHandled}</td>
                    <td className="py-3 px-4 font-extrabold text-emerald-800">{ag.conversions}</td>
                    <td className="py-3 px-4 font-bold text-teal-800">{ag.avgTatMins} Mins</td>
                    <td className="py-3 px-4">
                      <span className={`font-bold px-2 py-0.5 rounded ${ag.slaBreaches > 0 ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'text-slate-500'}`}>
                        {ag.slaBreaches}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="font-black text-teal-900 bg-teal-50 px-2.5 py-1 rounded-full border border-teal-200">
                        {ag.score}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
}
