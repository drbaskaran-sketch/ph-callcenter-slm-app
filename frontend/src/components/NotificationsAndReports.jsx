import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, FileSpreadsheet, Download, FileText, CheckCircle, Smartphone, Mail, Building2, RefreshCw } from 'lucide-react';
import { apiFetch, API_BASE, getToken } from '../api';

export default function NotificationsAndReports() {
  const [enquiries, setEnquiries] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [summary, setSummary] = useState(null);

  const [selectedEnquiryId, setSelectedEnquiryId] = useState('');
  const [channel, setChannel] = useState('WHATSAPP');
  const [templateType, setTemplateType] = useState('APPOINTMENT_CONFIRMATION');
  const [customMsg, setCustomMsg] = useState('');

  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [dispatchResult, setDispatchResult] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resEnq, resTpl, resSum] = await Promise.all([
        apiFetch(`${API_BASE}/enquiries`),
        apiFetch(`${API_BASE}/notifications/templates`),
        apiFetch(`${API_BASE}/reports/export/summary`)
      ]);

      if (resEnq.ok) {
        const d = await resEnq.json();
        if (d.enquiries && d.enquiries.length > 0) {
          setEnquiries(d.enquiries);
          setSelectedEnquiryId(d.enquiries[0].id);
        }
      }
      if (resTpl.ok) {
        const d = await resTpl.json();
        setTemplates(d.templates || []);
      }
      if (resSum.ok) {
        setSummary(await resSum.json());
      }
    } catch (err) {
      console.log('Error fetching notification & report data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const selectedEnquiry = enquiries.find(e => e.id === selectedEnquiryId) || enquiries[0];

  const handleSendNotification = async (e) => {
    e.preventDefault();
    if (!selectedEnquiry) return;

    setSending(true);
    try {
      const res = await apiFetch(`${API_BASE}/notifications/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          enquiryId: selectedEnquiry.id,
          channel: channel,
          templateType: templateType,
          recipientPhone: selectedEnquiry.phone,
          customMessage: customMsg || undefined
        })
      });

      if (res.ok) {
        setDispatchResult(await res.json());
      }
    } catch (err) {
      console.log('Notification dispatch error');
    } finally {
      setSending(false);
    }
  };

  const handleDownloadCsv = () => {
    const token = getToken();
    const url = `${API_BASE}/reports/export/csv`;
    
    fetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.blob())
      .then(blob => {
        const a = document.createElement('a');
        a.href = window.URL.createObjectURL(blob);
        a.download = 'prashanth_hosp_callcenter_report.csv';
        a.click();
      });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">

      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-5 rounded-2xl shadow-sm">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-teal-700" />
            Notifications & Executive Report Exports
          </h2>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Automated WhatsApp / SMS patient notification gateway & 1-click CSV/Summary executive report generator.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="text-slate-600 hover:text-teal-700 flex items-center gap-1 font-bold bg-slate-100 px-3 py-2 rounded-xl border border-slate-200 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          
          <button
            onClick={handleDownloadCsv}
            className="bg-emerald-700 hover:bg-emerald-800 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Export Full CSV Report</span>
          </button>
        </div>
      </div>

      {/* Main Grid: WhatsApp/SMS Dispatch Tester + Executive Summary Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left Side: Notification Dispatch Tester (7 cols) */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Send className="w-4 h-4 text-teal-700" />
            Outbound WhatsApp & SMS Dispatch Gateway
          </h3>

          <form onSubmit={handleSendNotification} className="space-y-4 text-xs font-medium">
            <div>
              <label className="font-bold text-slate-700 block mb-1">Select Patient Lead / Enquiry *</label>
              <select
                value={selectedEnquiryId}
                onChange={e => setSelectedEnquiryId(e.target.value)}
                className="w-full p-2.5 border border-slate-300 rounded-xl font-bold text-slate-900"
              >
                {enquiries.map(enq => (
                  <option key={enq.id} value={enq.id}>
                    {enq.id} - {enq.patientName} ({enq.phone}) • {enq.branchCode}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Dispatch Channel *</label>
                <select
                  value={channel}
                  onChange={e => setChannel(e.target.value)}
                  className="w-full p-2.5 border border-slate-300 rounded-xl font-bold text-slate-900"
                >
                  <option value="WHATSAPP">WhatsApp Business API</option>
                  <option value="SMS">High-Priority SMS Gateway</option>
                  <option value="EMAIL">Patient Portal Email</option>
                </select>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Template Type *</label>
                <select
                  value={templateType}
                  onChange={e => setTemplateType(e.target.value)}
                  className="w-full p-2.5 border border-slate-300 rounded-xl font-bold text-slate-900"
                >
                  <option value="APPOINTMENT_CONFIRMATION">OPD Appointment Confirmation</option>
                  <option value="SURGERY_PREBOOK">OT Surgery Pre-booking Alert</option>
                  <option value="FOLLOWUP_REMINDER">Follow-Up Consultation Reminder</option>
                  <option value="GENERAL_INFO">General Enquiry Response</option>
                </select>
              </div>
            </div>

            <div>
              <label className="font-bold text-slate-700 block mb-1">Custom Message / Override Notes (Optional)</label>
              <textarea
                value={customMsg}
                onChange={e => setCustomMsg(e.target.value)}
                placeholder="Leave empty to use official Prashanth Hospitals verified template..."
                rows={3}
                className="w-full p-2.5 border border-slate-300 rounded-xl text-slate-900 font-normal resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={sending}
              className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-2.5 rounded-xl shadow-xs text-xs flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>{sending ? 'Dispatching Message...' : `Dispatch ${channel} Message`}</span>
            </button>
          </form>

          {/* Dispatch Result Card */}
          {dispatchResult && (
            <div className="bg-teal-900 text-white p-4 rounded-xl border border-teal-800 space-y-2 text-xs">
              <div className="flex items-center justify-between font-bold">
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" />
                  Dispatch Confirmed ({dispatchResult.dispatchId})
                </span>
                <span className="bg-teal-800 px-2 py-0.5 rounded text-[10px]">{dispatchResult.channel}</span>
              </div>
              <p className="text-slate-300 font-medium">{dispatchResult.message}</p>
              <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-[11px] font-mono text-emerald-300">
                "{dispatchResult.renderedBody}"
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Executive Summary & Template Library (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          
          {/* Executive Summary Card */}
          {summary && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
              <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                <FileText className="w-4 h-4 text-teal-700" />
                Executive Summary Snapshot
              </h3>

              <div className="space-y-2 text-xs font-medium text-slate-700">
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Total Enquiries Captured:</span>
                  <span className="font-extrabold text-slate-900">{summary.totalEnquiriesCaptured}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Active Hospital Branches:</span>
                  <span className="font-bold text-slate-800">{summary.activeBranches}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">SLA Breach Incidents:</span>
                  <span className="font-bold text-amber-700">{summary.slaBreaches}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">HIS Synced Bookings:</span>
                  <span className="font-bold text-emerald-700">{summary.hisSyncedBookings}</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-500">Overall Lead Conversion:</span>
                  <span className="font-black text-teal-800">{summary.overallConversionRate}</span>
                </div>
              </div>

              <button
                onClick={handleDownloadCsv}
                className="w-full mt-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold py-2 rounded-xl border border-slate-200 text-xs flex items-center justify-center gap-1.5"
              >
                <FileSpreadsheet className="w-4 h-4 text-emerald-700" />
                <span>Download .CSV Spreadsheet</span>
              </button>
            </div>
          )}

          {/* Template Library List */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-teal-700" />
              Verified WhatsApp / SMS Templates
            </h3>

            <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1 text-xs">
              {templates.map((t, idx) => (
                <div key={idx} className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1">
                  <div className="flex items-center justify-between font-bold">
                    <span className="text-slate-900">{t.title}</span>
                    <span className="bg-teal-100 text-teal-800 px-1.5 py-0.5 rounded text-[9px]">{t.channel}</span>
                  </div>
                  <p className="text-[10px] text-slate-600 font-mono leading-relaxed">{t.bodyTemplate}</p>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
