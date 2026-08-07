import React, { useState, useEffect } from 'react';
import { Phone, MessageSquare, UserCheck, Play, Pause, Clock, Search, Filter, RefreshCw, CheckCircle, ListOrdered, Calendar } from 'lucide-react';
import { MOCK_ENQUIRIES } from '../data/mockData';
import { apiFetch, API_BASE } from '../api';

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

  // Fetch live enquiries from FastAPI backend
  const fetchEnquiries = async () => {
    try {
      const res = await apiFetch(`${API_BASE}/enquiries`);
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

  // Format current time into HH:MM:SS string
  const getCurrentFormattedTime = () => {
    const now = new Date();
    return now.toTimeString().split(' ')[0];
  };

  // Register action with timestamp & persist to PostgreSQL
  const registerNewAction = async (actionText, performedByText = 'SLM Agent') => {
    const timeStr = getCurrentFormattedTime();
    const newAction = {
      timestamp: timeStr,
      action: actionText,
      performedBy: performedByText
    };

    setSelectedEnquiry(prev => {
      if (!prev) return prev;
      const currentActions = prev.registeredActions || [];
      const updated = {
        ...prev,
        registeredActions: [...currentActions, newAction]
      };
      setEnquiries(list => list.map(item => item.id === prev.id ? updated : item));
      return updated;
    });

    if (selectedEnquiry?.id) {
      try {
        const res = await apiFetch(`${API_BASE}/enquiries/${selectedEnquiry.id}/actions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: actionText, performedBy: performedByText })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.enquiry) {
            setSelectedEnquiry(data.enquiry);
            setEnquiries(list => list.map(item => item.id === data.enquiry.id ? data.enquiry : item));
          }
        }
      } catch (e) {
        console.log('Action registered in local state');
      }
    }
  };

  // Handle Update Disposition Status with Mandatory Remarks Validation
  const handleUpdateStatus = async (newStatus) => {
    if ((newStatus === 'CLOSED' || newStatus === 'CONVERTED') && (!remarks || !remarks.trim())) {
      setErrorMessage("⚠️ Mandatory remarks required before closing or converting an enquiry!");
      setTimeout(() => setErrorMessage(null), 4000);
      return;
    }

    setStatus(newStatus);
    setErrorMessage(null);

    // Register timestamped action
    registerNewAction(`Status updated to ${newStatus.replace('_', ' ')} with remarks: "${remarks || 'None'}"`, selectedEnquiry?.assignedSLM || 'SLM Agent');

    try {
      const res = await apiFetch(`${API_BASE}/enquiries/${selectedEnquiry.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          notes: notes,
          remarks: remarks
        })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.enquiry) {
          setSelectedEnquiry(data.enquiry);
          setEnquiries(list => list.map(item => item.id === data.enquiry.id ? data.enquiry : item));
        }
      }
    } catch (e) {
      console.log('Status updated in local state');
    }

    setToastMessage(`✓ Registered Disposition: ${newStatus.replace('_', ' ')}`);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Handle Dial / WhatsApp action registration
  const handleDialCall = () => {
    registerNewAction(`Outbound call initiated to ${selectedEnquiry?.phone}`, selectedEnquiry?.assignedSLM || 'SLM Agent');
    alert(`Dialing ${selectedEnquiry?.phone}...\nAction registered at ${getCurrentFormattedTime()}`);
  };

  const handleSendWhatsApp = () => {
    registerNewAction(`WhatsApp consultation message dispatched to ${selectedEnquiry?.phone}`, selectedEnquiry?.assignedSLM || 'SLM Agent');
    alert(`Opening WhatsApp chat with ${selectedEnquiry?.phone}...\nAction registered at ${getCurrentFormattedTime()}`);
  };

  // Handle HIS OPD Slot Booking
  const handleBookHisSlot = async () => {
    if (!selectedEnquiry) return;
    try {
      const res = await apiFetch(`${API_BASE}/his/book-appointment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          enquiryId: selectedEnquiry.id,
          doctorName: selectedEnquiry.doctorName || "Dr. S. Prashanth",
          appointmentDate: new Date().toISOString().split('T')[0],
          slotTime: "10:30 AM",
          remarks: remarks || "OPD Consultation slot booked via HIS API"
        })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.enquiry) {
          setSelectedEnquiry(data.enquiry);
          setEnquiries(list => list.map(item => item.id === data.enquiry.id ? data.enquiry : item));
        }
        setToastMessage(`✅ HIS OPD Slot Booked! (Ref: ${data.hisBookingId}, UHID: ${data.patientUhid})`);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 4000);
      }
    } catch (e) {
      console.log('Error booking HIS slot');
    }
  };

  // Handle HIS Surgery Pre-booking
  const handlePrebookHisSurgery = async () => {
    if (!selectedEnquiry) return;
    try {
      const res = await apiFetch(`${API_BASE}/his/prebook-surgery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          enquiryId: selectedEnquiry.id,
          doctorName: selectedEnquiry.doctorName || "Dr. S. Prashanth",
          procedureName: selectedEnquiry.enquiryType || "Surgical Procedure",
          proposedSurgeryDate: new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0],
          remarks: remarks || "OT Surgery pre-booked via HIS API"
        })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.enquiry) {
          setSelectedEnquiry(data.enquiry);
          setEnquiries(list => list.map(item => item.id === data.enquiry.id ? data.enquiry : item));
        }
        setToastMessage(`🏥 HIS OT Surgery Pre-Booked! (Ref: ${data.hisBookingId}, UHID: ${data.patientUhid})`);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 4000);
      }
    } catch (e) {
      console.log('Error prebooking HIS surgery');
    }
  };

  // Handle Audio Playback with live stream proxy
  const toggleAudioPlayback = async () => {
    if (!isPlaying) {
      registerNewAction(`Call recording stream played by SLM`, selectedEnquiry?.assignedSLM || 'SLM Agent');
      const audioFileName = selectedEnquiry?.recordingUrl || selectedEnquiry?.recording_path || 'wav_8801.wav';
      const audioUrl = `${API_BASE}/recordings/${encodeURIComponent(audioFileName)}`;
      
      try {
        const response = await apiFetch(audioUrl);
        if (!response.ok) throw new Error('Recording unavailable');
        const objectUrl = URL.createObjectURL(await response.blob());
        const audioObj = new Audio(objectUrl);
        audioObj.addEventListener('ended', () => URL.revokeObjectURL(objectUrl), { once: true });
        audioObj.play().catch(() => {
          // Fallback Web Audio API synth if browser blocks autoplay or format unsupported
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
        });
      } catch (e) {
        console.log('Audio stream playback initiated');
      }
      setIsPlaying(true);
      setTimeout(() => setIsPlaying(false), 3000);
    } else {
      setIsPlaying(false);
    }
  };

  // Simulate incoming call ingestion
  const handleSimulateCall = async () => {
    setLoadingSim(true);
    try {
      const res = await apiFetch(`${API_BASE}/xtend/simulate-call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selectedBranchCode: filterBranch !== 'ALL' ? filterBranch : undefined
        })
      });
      if (res.ok) {
        const data = await res.json();
        const newEnq = {
          ...data.enquiry,
          callStartTime: getCurrentFormattedTime(),
          callEndTime: 'In Progress',
          callDuration: '01m 20s',
          registeredActions: [
            { timestamp: getCurrentFormattedTime(), action: 'Inbound Call Connected at Kolathur Hub', performedBy: 'XTEND IVR' },
            { timestamp: getCurrentFormattedTime(), action: 'Lead Dispatched to SLM', performedBy: 'FCM Push' }
          ]
        };
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
      {/* Header Banner - White Mode */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-5 rounded-2xl shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-extrabold text-slate-900">SLM Mobile Application & Call Action Register</h2>
            <span className="bg-teal-50 text-teal-800 text-xs font-bold px-2.5 py-0.5 rounded-full border border-teal-200">
              Live DB2 Sync & Registered Action Audit Trail
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1 font-medium">
            Tracks call timing (start time, end time, duration) and logs registered timestamps for every SLM action on calls and patient queries.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSimulateCall}
            disabled={loadingSim}
            className="flex items-center gap-2 bg-teal-700 hover:bg-teal-800 text-white font-bold py-2.5 px-4 rounded-xl shadow-xs transition-all text-xs disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loadingSim ? 'animate-spin' : ''}`} />
            <span>{loadingSim ? 'Ingesting Call...' : 'Simulate Inbound XTEND Call'}</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search patient, phone, or department..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white border border-slate-200 text-xs font-medium text-slate-900 pl-10 pr-4 py-2.5 rounded-xl focus:outline-none focus:border-teal-600 shadow-xs"
          />
        </div>

        <div className="flex items-center gap-2 bg-white border border-slate-200 px-3.5 py-1.5 rounded-xl shadow-xs">
          <Filter className="w-4 h-4 text-teal-700 shrink-0" />
          <span className="text-xs text-slate-500 font-bold shrink-0">Branch:</span>
          <select
            value={filterBranch}
            onChange={(e) => setFilterBranch(e.target.value)}
            className="bg-transparent text-xs font-bold text-slate-800 focus:outline-none w-full"
          >
            <option value="ALL">All Branches (7)</option>
            <option value="KOL">Kolathur Hub (KOL)</option>
            <option value="CHP">Chetpet (CHP)</option>
            <option value="VEL">Velachery (VEL)</option>
            <option value="GUM">Gummidipoondi (GUM)</option>
            <option value="IVF">IVF Clinics (IVF)</option>
          </select>
        </div>

        <div className="bg-white border border-slate-200 px-4 py-2.5 rounded-xl flex items-center justify-between shadow-xs">
          <span className="text-xs text-slate-500 font-bold">Queue Status:</span>
          <span className="text-xs font-black text-teal-800 bg-teal-50 px-2.5 py-1 rounded-lg border border-teal-200">
            {filteredEnquiries.length} Active Call Leads
          </span>
        </div>
      </div>

      {/* Main Grid: Queue List + Mobile Phone Frame */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: Call Queue with Timing (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          <h3 className="text-xs font-extrabold text-slate-700 uppercase tracking-wider flex items-center justify-between">
            <span>Inbound XTEND Call Queue & Action Logs</span>
            <span className="text-xs text-slate-500 font-normal">Click a lead to view call timing & action register</span>
          </h3>

          <div className="space-y-3 max-h-[680px] overflow-y-auto pr-1">
            {filteredEnquiries.map((enq) => {
              const isSelected = selectedEnquiry && selectedEnquiry.id === enq.id;
              return (
                <div
                  key={enq.id}
                  onClick={() => setSelectedEnquiry(enq)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-teal-50/60 border-teal-500 shadow-md'
                      : 'bg-white border-slate-200 hover:border-slate-300 shadow-xs'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-slate-900 text-base">{enq.patientName}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          enq.priority === 'URGENT' ? 'bg-red-100 text-red-700 border border-red-200' :
                          enq.priority === 'HIGH' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                          'bg-blue-100 text-blue-700 border border-blue-200'
                        }`}>
                          {enq.priority}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1 flex items-center gap-2 font-medium">
                        <span>{enq.phone}</span>
                        <span>•</span>
                        <span className="text-teal-800 font-bold">{enq.department}</span>
                      </p>
                    </div>

                    <div className="text-right">
                      <span className="text-xs font-black text-slate-800 block">{enq.branchCode}</span>
                      <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1 mt-0.5 justify-end">
                        <Clock className="w-3 h-3 text-slate-400" /> {enq.timeAgo}
                      </span>
                    </div>
                  </div>

                  {/* Registered Call Timing Info */}
                  <div className="mt-3 pt-2.5 border-t border-slate-200/80 grid grid-cols-3 gap-2 text-[11px]">
                    <div className="bg-white p-1.5 rounded-lg border border-slate-200 text-center">
                      <span className="text-slate-400 block text-[9px] uppercase font-bold">Call Start</span>
                      <span className="font-bold text-slate-800">{enq.callStartTime || '17:25:10'}</span>
                    </div>
                    <div className="bg-white p-1.5 rounded-lg border border-slate-200 text-center">
                      <span className="text-slate-400 block text-[9px] uppercase font-bold">Call End</span>
                      <span className="font-bold text-slate-800">{enq.callEndTime || '17:27:24'}</span>
                    </div>
                    <div className="bg-teal-100/50 p-1.5 rounded-lg border border-teal-200 text-center">
                      <span className="text-teal-700 block text-[9px] uppercase font-bold">Duration</span>
                      <span className="font-extrabold text-teal-900">{enq.callDuration || '02m 14s'}</span>
                    </div>
                  </div>

                  <div className="mt-2.5 flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-600 flex items-center gap-1">
                      <UserCheck className="w-3.5 h-3.5 text-teal-700" /> {enq.assignedSLM}
                    </span>
                    <span className="bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-full text-[11px] border border-slate-200 font-bold">
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
          <div className="w-full max-w-[380px] bg-slate-900 border-[8px] border-slate-800 rounded-[44px] p-3 shadow-2xl relative">
            
            {/* Speaker Notch */}
            <div className="w-28 h-4 bg-slate-800 rounded-b-2xl mx-auto mb-2 flex items-center justify-center gap-2">
              <div className="w-2 h-2 rounded-full bg-slate-950"></div>
              <div className="w-7 h-1 rounded-full bg-slate-950"></div>
            </div>

            {/* Mobile App Screen Content - Clean Light Mode */}
            <div className="bg-slate-50 rounded-[32px] pt-4 pb-4 px-4 min-h-[640px] flex flex-col justify-between text-slate-800 relative">
              
              {/* Toast Notification Banner */}
              {showToast && (
                <div className="absolute top-4 left-4 right-4 bg-teal-700 text-white text-xs font-bold py-2 px-3 rounded-xl shadow-lg z-40 text-center border border-teal-500">
                  {toastMessage}
                </div>
              )}

              {/* Error Message Banner */}
              {errorMessage && (
                <div className="absolute top-4 left-4 right-4 bg-red-600 text-white text-xs font-bold py-2 px-3 rounded-xl shadow-lg z-40 text-center">
                  {errorMessage}
                </div>
              )}

              {/* Mobile Header Bar */}
              <div className="border-b border-slate-200 pb-2.5 mb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <div className="w-6 h-6 rounded-lg bg-teal-700 flex items-center justify-center font-black text-[10px] text-white">
                      PH
                    </div>
                    <span className="text-xs font-extrabold text-slate-900">Prashanth SLM App</span>
                  </div>
                  <span className="text-[10px] bg-teal-100 text-teal-800 font-bold px-2 py-0.5 rounded-full border border-teal-300">
                    LIVE FCM PUSH
                  </span>
                </div>
              </div>

              {/* Active Lead Details */}
              {selectedEnquiry && (
                <div className="space-y-3 flex-1 overflow-y-auto pr-1">
                  
                  {/* FCR Alert Badge if Agent Resolved */}
                  {selectedEnquiry.fcmBypassed && (
                    <div className="bg-purple-50 border border-purple-200 p-2 rounded-xl text-purple-900 text-[11px] flex items-center gap-2 font-medium">
                      <CheckCircle className="w-4 h-4 text-purple-600 shrink-0" />
                      <span><b>FCR Bypass:</b> Resolved on call by Agent. FCM suppressed.</span>
                    </div>
                  )}

                  {/* Patient Header Card */}
                  <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-black text-teal-800">{selectedEnquiry.id}</span>
                      <span className="text-[10px] font-bold text-slate-500">{selectedEnquiry.branch}</span>
                    </div>
                    <h3 className="text-sm font-black text-slate-900">{selectedEnquiry.patientName}</h3>
                    <p className="text-xs text-slate-600 font-medium mt-0.5">{selectedEnquiry.phone} • {selectedEnquiry.gender}, {selectedEnquiry.age}y</p>
                    <p className="text-xs font-bold text-teal-800 mt-1">{selectedEnquiry.enquiryType}</p>
                  </div>

                  {/* HIS Integration & Booking Card */}
                  <div className="bg-teal-900 text-white p-3 rounded-2xl border border-teal-800 shadow-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-extrabold uppercase text-teal-300">HIS EMR & Slot Booking</span>
                      <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${
                        selectedEnquiry.hisSyncStatus === 'SYNCED' ? 'bg-emerald-500 text-white' : 'bg-amber-500 text-slate-900'
                      }`}>
                        {selectedEnquiry.hisSyncStatus || 'PENDING'}
                      </span>
                    </div>

                    <div className="text-[10px] font-medium space-y-0.5">
                      <p><span className="text-slate-400 font-bold">UHID:</span> <span className="font-extrabold text-teal-200">{selectedEnquiry.patientUhid || 'Auto-Provision on Booking'}</span></p>
                      {selectedEnquiry.hisBookingId && (
                        <p><span className="text-slate-400 font-bold">HIS Ref:</span> <span className="font-extrabold text-emerald-300">{selectedEnquiry.hisBookingId}</span></p>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-1.5 pt-1">
                      <button
                        onClick={handleBookHisSlot}
                        className="bg-teal-700 hover:bg-teal-600 text-white font-extrabold py-1.5 px-2 rounded-lg text-[10px] border border-teal-500 transition-all text-center"
                      >
                        Book HIS OPD Slot
                      </button>
                      <button
                        onClick={handlePrebookHisSurgery}
                        className="bg-emerald-700 hover:bg-emerald-600 text-white font-extrabold py-1.5 px-2 rounded-lg text-[10px] border border-emerald-500 transition-all text-center"
                      >
                        Pre-Book Surgery OT
                      </button>
                    </div>
                  </div>

                  {/* Call Timing & Duration Card */}
                  <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-extrabold text-slate-800 flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-teal-700" />
                        Call Timing & Duration
                      </span>
                      <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full border border-emerald-300">
                        {selectedEnquiry.callDuration || '02m 14s'}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-[10px]">
                      <div className="bg-slate-50 p-1.5 rounded-lg border border-slate-200">
                        <span className="text-slate-400 block font-bold">START TIME</span>
                        <span className="font-extrabold text-slate-800">{selectedEnquiry.callStartTime || '17:25:10'}</span>
                      </div>
                      <div className="bg-slate-50 p-1.5 rounded-lg border border-slate-200">
                        <span className="text-slate-400 block font-bold">END TIME</span>
                        <span className="font-extrabold text-slate-800">{selectedEnquiry.callEndTime || '17:27:24'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Registered Action Timeline */}
                  <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-extrabold text-slate-800 flex items-center gap-1">
                        <ListOrdered className="w-3.5 h-3.5 text-teal-700" />
                        Registered Action Timestamps
                      </span>
                    </div>

                    <div className="space-y-1.5 max-h-36 overflow-y-auto text-[10px]">
                      {(selectedEnquiry.registeredActions || [
                        { timestamp: '17:25:10', action: 'Inbound Call Connected at Kolathur Hub', performedBy: 'XTEND IVR' },
                        { timestamp: '17:25:35', action: 'Angiogram inquiry registered', performedBy: 'Agent #104' },
                        { timestamp: '17:26:45', action: 'Dr. Consultation slot fixed', performedBy: selectedEnquiry.assignedSLM }
                      ]).map((act, idx) => (
                        <div key={idx} className="bg-slate-50 p-2 rounded-lg border border-slate-200 flex items-start gap-2">
                          <span className="font-black text-teal-800 bg-teal-100/70 px-1.5 py-0.5 rounded text-[9px] shrink-0">
                            {act.timestamp}
                          </span>
                          <div>
                            <p className="font-bold text-slate-800 leading-tight">{act.action}</p>
                            <span className="text-slate-400 text-[8px] font-medium">{act.performedBy}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Audio Recording Stream */}
                  <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-extrabold text-slate-800 flex items-center gap-1">
                        <Phone className="w-3 h-3 text-teal-700" />
                        XTEND Audio Recording
                      </span>
                      <span className="text-[10px] text-slate-500 font-bold">
                        {selectedEnquiry.recordingUrl || selectedEnquiry.recording_path ? (selectedEnquiry.audioDuration || "3.0s WAV") : "Audio Pending"}
                      </span>
                    </div>
                    
                    {selectedEnquiry.recordingUrl || selectedEnquiry.recording_path ? (
                      <div className="flex items-center gap-3">
                        <button
                          onClick={toggleAudioPlayback}
                          className="w-8 h-8 rounded-full bg-teal-700 hover:bg-teal-800 flex items-center justify-center text-white transition-all shadow-xs"
                        >
                          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                        </button>
                        <div className="flex-1 bg-slate-200 h-2 rounded-full overflow-hidden">
                          <div className={`h-full bg-teal-600 transition-all ${isPlaying ? 'w-3/4 animate-pulse' : 'w-1/4'}`}></div>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-amber-50 border border-amber-200 p-2 rounded-xl text-[10px] text-amber-800 font-bold flex items-center gap-2">
                        <span>Audio sync pending from DB2. Processing text payload.</span>
                      </div>
                    )}
                  </div>

                  {/* Doctor & Resolution Remarks Input */}
                  <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs space-y-2">
                    <span className="text-[11px] font-extrabold text-slate-800 flex items-center gap-1">
                      <UserCheck className="w-3 h-3 text-teal-700" />
                      Doctor & Mandatory Remarks
                    </span>
                    <p className="text-xs text-slate-900 font-extrabold">{selectedEnquiry.doctorName}</p>
                    
                    <textarea
                      value={remarks}
                      onChange={(e) => {
                        setRemarks(e.target.value);
                        setNotes(e.target.value);
                      }}
                      placeholder="Enter mandatory resolution remarks prior to closing..."
                      rows={2}
                      className="w-full bg-slate-50 border border-slate-200 text-xs text-slate-800 p-2 rounded-lg focus:outline-none focus:border-teal-600 resize-none font-medium"
                    />
                  </div>

                  {/* Status Picker Buttons */}
                  <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs space-y-2">
                    <label className="text-[11px] font-extrabold text-slate-800 block">
                      Register Disposition (Mandatory Remarks for Closed):
                    </label>
                    <div className="grid grid-cols-2 gap-1.5">
                      {['CONTACTED', 'DOCTOR_CONSULTED', 'CONVERTED', 'CLOSED'].map((st) => (
                        <button
                          key={st}
                          onClick={() => handleUpdateStatus(st)}
                          className={`text-[10px] font-extrabold py-1.5 px-2 rounded-lg border transition-all ${
                            status === st
                              ? 'bg-teal-700 border-teal-700 text-white shadow-xs'
                              : 'bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200'
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
              <div className="pt-3 border-t border-slate-200 grid grid-cols-2 gap-2">
                <button
                  onClick={handleDialCall}
                  className="bg-teal-700 hover:bg-teal-800 text-white font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all shadow-xs"
                >
                  <Phone className="w-3.5 h-3.5" />
                  <span>Call Patient</span>
                </button>
                <button
                  onClick={handleSendWhatsApp}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all shadow-xs"
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
