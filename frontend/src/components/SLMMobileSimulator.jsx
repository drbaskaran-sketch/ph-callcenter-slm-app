import React, { useState, useEffect, useRef } from 'react';
import { Phone, MessageSquare, Calendar, UserCheck, Play, Pause, Bell, Clock, Building, Shield, Filter, Search, AlertTriangle, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import { MOCK_ENQUIRIES } from '../data/mockData';

const API_BASE = '/api/v1';

export default function SLMMobileSimulator() {
  const [enquiries, setEnquiries] = useState(MOCK_ENQUIRIES);
  const [selectedEnquiry, setSelectedEnquiry] = useState(MOCK_ENQUIRIES[0]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [status, setStatus] = useState(MOCK_ENQUIRIES[0].status);
  const [notes, setNotes] = useState(MOCK_ENQUIRIES[0].notes || '');
  const [remarks, setRemarks] = useState(MOCK_ENQUIRIES[0].remarks || '');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);
  const [filterBranch, setFilterBranch] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingSim, setLoadingSim] = useState(false);
  
  const audioRef = useRef(null);

  // Fetch live enquiries from FastAPI backend
  const fetchEnquiries = async () => {
    try {
      const res = await fetch(`${API_BASE}/enquiries`);
      if (res.ok) {
        const data = await res.json();
        if (data.enquiries && data.enquiries.length > 0) {
          setEnquiries(data.enquiries);
          if (!selectedEnquiry || !data.enquiries.find(e => e.id === selectedEnquiry.id)) {
            setSelectedEnquiry(data.enquiries[0]);
            setStatus(data.enquiries[0].status);
            setNotes(data.enquiries[0].notes || '');
            setRemarks(data.enquiries[0].remarks || '');
          }
        }
      }
    } catch (err) {
      console.log('Using local mock enquiries fallback');
    }
  };

  useEffect(() => {
    fetchEnquiries();
  }, []);

  useEffect(() => {
    if (selectedEnquiry) {
      setStatus(selectedEnquiry.status);
      setNotes(selectedEnquiry.notes || '');
      setRemarks(selectedEnquiry.remarks || selectedEnquiry.notes || '');
      setIsPlaying(false);
    }
  }, [selectedEnquiry]);

  // Handle Update Disposition Status with Mandatory Remarks Validation
  const handleUpdateStatus = async (newStatus) => {
    // Mandatory Remarks Check for CLOSED or CONVERTED
    if ((newStatus === 'CLOSED' || newStatus === 'CONVERTED') && (!remarks || !remarks.trim())) {
      setErrorMessage("⚠️ Mandatory remarks required before closing or converting an enquiry!");
      setTimeout(() => setErrorMessage(null), 4000);
      return;
    }

    setStatus(newStatus);
    setErrorMessage(null);

    // Call backend API if connected
    try {
      await fetch(`${API_BASE}/enquiries/${selectedEnquiry.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          notes: notes,
          remarks: remarks
        })
      });
    } catch (e) {
      console.log('Status updated in local state');
    }

    setToastMessage(`✓ Status Updated: ${newStatus.replace('_', ' ')}`);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Handle Play / Pause Call Recording Audio Stream
  const toggleAudioPlayback = () => {
    if (!isPlaying) {
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 3);
      } catch (e) {
        console.log('Audio synth playback started');
      }
      setIsPlaying(true);
      setTimeout(() => setIsPlaying(false), 3000);
    } else {
      setIsPlaying(false);
    }
  };

  // Simulate incoming XTEND DB2 call ingestion
  const handleSimulateCall = async () => {
    setLoadingSim(true);
    try {
      const res = await fetch(`${API_BASE}/xtend/simulate-call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selectedBranchCode: filterBranch !== 'ALL' ? filterBranch : undefined
        })
      });
      if (res.ok) {
        const data = await res.json();
        const newEnq = data.enquiry;
        setEnquiries(prev => [newEnq, ...prev]);
        setSelectedEnquiry(newEnq);
        setStatus(newEnq.status);
        setNotes(newEnq.notes);
        setRemarks(newEnq.remarks || '');
        setToastMessage(`🚨 NEW CALL INGESTED: ${newEnq.patientName} (${newEnq.department})`);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 4000);
      }
    } catch (err) {
      console.log('Simulation fallback error', err);
    } finally {
      setLoadingSim(false);
    }
  };

  // Filter enquiries
  const filteredEnquiries = enquiries.filter(enq => {
    const matchesBranch = filterBranch === 'ALL' || enq.branchCode === filterBranch;
    const matchesSearch = !searchQuery || 
      enq.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      enq.phone.includes(searchQuery) ||
      enq.department.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesBranch && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 rounded-2xl">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white">SLM Mobile Application & Dispatch Simulator</h2>
            <span className="bg-teal-500/10 text-teal-400 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-teal-500/20">
              Live DB2 Sync
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Simulates Service Line Manager (SLM) Android & iOS app push notifications, patient triage, and OPD/Surgery slot fixing.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSimulateCall}
            disabled={loadingSim}
            className="flex items-center gap-2 bg-teal-600 hover:bg-teal-500 text-white font-bold py-2.5 px-4 rounded-xl shadow-lg transition-all text-xs border border-teal-400/30 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loadingSim ? 'animate-spin' : ''}`} />
            <span>{loadingSim ? 'Ingesting...' : 'Simulate XTEND DB2 Call'}</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search patient, phone, or department..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 text-sm text-slate-200 pl-10 pr-4 py-2.5 rounded-xl focus:outline-none focus:border-teal-500"
          />
        </div>

        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3.5 py-1.5 rounded-xl">
          <Filter className="w-4 h-4 text-teal-400 shrink-0" />
          <span className="text-xs text-slate-400 font-semibold shrink-0">Branch:</span>
          <select
            value={filterBranch}
            onChange={(e) => setFilterBranch(e.target.value)}
            className="bg-transparent text-sm font-semibold text-slate-200 focus:outline-none w-full"
          >
            <option value="ALL" className="bg-slate-900">All Branches (7)</option>
            <option value="KOL" className="bg-slate-900">Kolathur Hub (KOL)</option>
            <option value="CHP" className="bg-slate-900">Chetpet (CHP)</option>
            <option value="VEL" className="bg-slate-900">Velachery (VEL)</option>
            <option value="GUM" className="bg-slate-900">Gummidipoondi (GUM)</option>
            <option value="IVF" className="bg-slate-900">IVF Clinics (IVF)</option>
          </select>
        </div>

        <div className="bg-slate-900 border border-slate-800 px-4 py-2.5 rounded-xl flex items-center justify-between">
          <span className="text-xs text-slate-400 font-medium">Queue Status:</span>
          <span className="text-xs font-bold text-teal-400 bg-teal-500/10 px-2.5 py-1 rounded-lg border border-teal-500/20">
            {filteredEnquiries.length} Active Leads
          </span>
        </div>
      </div>

      {/* Main Grid: Queue List + Mobile Phone Frame */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: SLM Lead Dispatch Queue (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
            <span>Inbound XTEND DB2 Call Queue</span>
            <span className="text-xs text-slate-500 font-normal">Click a lead to inspect on mobile simulator</span>
          </h3>

          <div className="space-y-2.5 max-h-[640px] overflow-y-auto pr-1">
            {filteredEnquiries.map((enq) => {
              const isSelected = selectedEnquiry && selectedEnquiry.id === enq.id;
              return (
                <div
                  key={enq.id}
                  onClick={() => setSelectedEnquiry(enq)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-slate-800/90 border-teal-500 shadow-md shadow-teal-500/10'
                      : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-base">{enq.patientName}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          enq.priority === 'URGENT' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                          enq.priority === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                          'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                        }`}>
                          {enq.priority}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                        <span>{enq.phone}</span>
                        <span>•</span>
                        <span className="text-teal-300 font-semibold">{enq.department}</span>
                      </p>
                    </div>

                    <div className="text-right">
                      <span className="text-xs font-bold text-slate-300 block">{enq.branchCode}</span>
                      <span className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5 justify-end">
                        <Clock className="w-3 h-3" /> {enq.timeAgo}
                      </span>
                    </div>
                  </div>

                  <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    <span className="text-slate-400 flex items-center gap-1">
                      <UserCheck className="w-3.5 h-3.5 text-teal-400" /> {enq.assignedSLM}
                    </span>
                    <span className="bg-slate-950 text-slate-300 px-2.5 py-0.5 rounded-full text-[11px] border border-slate-800">
                      {enq.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Side: SLM Android/iOS Mobile Device Frame (5 cols) */}
        <div className="lg:col-span-5 flex justify-center">
          <div className="w-full max-w-[380px] bg-slate-950 border-[10px] border-slate-800 rounded-[48px] p-3 shadow-2xl relative">
            
            {/* Speaker & Camera Notch */}
            <div className="w-32 h-5 bg-slate-800 rounded-b-2xl mx-auto mb-2 flex items-center justify-center gap-2">
              <div className="w-2 h-2 rounded-full bg-slate-900"></div>
              <div className="w-8 h-1.5 rounded-full bg-slate-900"></div>
            </div>

            {/* Mobile App Screen Content */}
            <div className="bg-slate-900 rounded-[36px] pt-4 pb-4 px-4 min-h-[640px] flex flex-col justify-between text-slate-100 relative">
              
              {/* Toast Notification Banner */}
              {showToast && (
                <div className="absolute top-4 left-4 right-4 bg-teal-600 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-xl z-40 text-center animate-bounce border border-teal-400">
                  {toastMessage}
                </div>
              )}

              {/* Error Message Banner */}
              {errorMessage && (
                <div className="absolute top-4 left-4 right-4 bg-red-950 text-red-200 text-xs font-bold py-2.5 px-4 rounded-xl shadow-xl z-40 text-center border border-red-700">
                  {errorMessage}
                </div>
              )}

              {/* Mobile Header Bar */}
              <div className="border-b border-slate-800 pb-3 mb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <div className="w-6 h-6 rounded-lg bg-teal-600 flex items-center justify-center font-bold text-[10px] text-white">
                      PH
                    </div>
                    <span className="text-xs font-bold text-white">Prashanth SLM App</span>
                  </div>
                  <span className="text-[10px] bg-teal-950 text-teal-300 font-semibold px-2 py-0.5 rounded-full border border-teal-800">
                    LIVE FCM PUSH
                  </span>
                </div>
              </div>

              {/* Active Lead Details */}
              {selectedEnquiry && (
                <div className="space-y-3 flex-1 overflow-y-auto pr-1">
                  
                  {/* FCR Alert Badge if Agent Resolved */}
                  {selectedEnquiry.fcmBypassed && (
                    <div className="bg-purple-950/80 border border-purple-800/80 p-2.5 rounded-xl text-purple-200 text-[11px] flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-purple-400 shrink-0" />
                      <span><b>FCR Bypass:</b> Resolved on call by Agent. Suppressed FCM alert.</span>
                    </div>
                  )}

                  {/* Patient Header Card */}
                  <div className="bg-slate-950/80 p-3.5 rounded-2xl border border-slate-800">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-bold text-teal-400">{selectedEnquiry.id}</span>
                      <span className="text-[10px] font-semibold text-slate-400">{selectedEnquiry.branch}</span>
                    </div>
                    <h3 className="text-sm font-extrabold text-white">{selectedEnquiry.patientName}</h3>
                    <p className="text-xs text-slate-300 mt-0.5">{selectedEnquiry.phone} • {selectedEnquiry.gender}, {selectedEnquiry.age}y</p>
                    <p className="text-xs font-medium text-teal-300 mt-1">{selectedEnquiry.enquiryType}</p>
                  </div>

                  {/* Call Audio Recording Stream Player (Nullable Voice Path Support) */}
                  <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-bold text-slate-300 flex items-center gap-1">
                        <Phone className="w-3 h-3 text-teal-400" />
                        XTEND Call Recording Stream
                      </span>
                      <span className="text-[10px] text-slate-500">
                        {selectedEnquiry.recordingUrl || selectedEnquiry.recording_path ? (selectedEnquiry.audioDuration || "3.0s WAV") : "Audio Pending"}
                      </span>
                    </div>
                    
                    {selectedEnquiry.recordingUrl || selectedEnquiry.recording_path ? (
                      <div className="flex items-center gap-3">
                        <button
                          onClick={toggleAudioPlayback}
                          className="w-8 h-8 rounded-full bg-teal-600 hover:bg-teal-500 flex items-center justify-center text-white transition-all shadow-md"
                        >
                          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                        </button>
                        <div className="flex-1 bg-slate-800 h-2 rounded-full overflow-hidden">
                          <div className={`h-full bg-teal-400 transition-all ${isPlaying ? 'w-3/4 animate-pulse' : 'w-1/4'}`}></div>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-slate-900/90 border border-amber-900/40 p-2.5 rounded-xl text-[11px] text-amber-300 flex items-center gap-2">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                        <span>Audio sync pending from DB2. Processing text payload.</span>
                      </div>
                    )}
                  </div>

                  {/* Doctor & Mandatory Remarks Input */}
                  <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800 space-y-2">
                    <span className="text-[11px] font-bold text-slate-300 flex items-center gap-1">
                      <UserCheck className="w-3 h-3 text-teal-400" />
                      Doctor & Resolution Remarks
                    </span>
                    <p className="text-xs text-white font-semibold">{selectedEnquiry.doctorName}</p>
                    
                    <textarea
                      value={remarks}
                      onChange={(e) => {
                        setRemarks(e.target.value);
                        setNotes(e.target.value);
                      }}
                      placeholder="Enter mandatory resolution remarks prior to closing..."
                      rows={2}
                      className="w-full bg-slate-900 border border-slate-800 text-xs text-slate-200 p-2 rounded-lg focus:outline-none focus:border-teal-500 resize-none"
                    />
                  </div>

                  {/* Status Picker Buttons */}
                  <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800 space-y-2">
                    <label className="text-[11px] font-bold text-slate-300 block">
                      Update Disposition (Mandatory Remarks for Closed):
                    </label>
                    <div className="grid grid-cols-2 gap-1.5">
                      {['CONTACTED', 'DOCTOR_CONSULTED', 'CONVERTED', 'CLOSED'].map((st) => (
                        <button
                          key={st}
                          onClick={() => handleUpdateStatus(st)}
                          className={`text-[10px] font-bold py-1.5 px-2 rounded-lg border transition-all ${
                            status === st
                              ? 'bg-teal-600 border-teal-400 text-white'
                              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {st.replace('_', ' ')}
                        </button>
                      ))}
                    </div>
                  </div>

                </div>
              )}

              {/* Action Toolbar */}
              <div className="pt-3 border-t border-slate-800 grid grid-cols-2 gap-2">
                <button
                  onClick={() => alert(`Dialing ${selectedEnquiry?.phone}...`)}
                  className="bg-teal-600 hover:bg-teal-500 text-white font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all shadow-md"
                >
                  <Phone className="w-3.5 h-3.5" />
                  <span>Call Patient</span>
                </button>
                <button
                  onClick={() => alert(`Opening WhatsApp chat with ${selectedEnquiry?.phone}...`)}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all shadow-md"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>WhatsApp</span>
                </button>
              </div>

            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
