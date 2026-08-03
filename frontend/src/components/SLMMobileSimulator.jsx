import React, { useState } from 'react';
import { Phone, MessageSquare, UserCheck, Play, Pause, Bell, Clock, Building, AlertCircle, CheckCircle } from 'lucide-react';
import { MOCK_ENQUIRIES } from '../data/mockData';

export default function SLMMobileSimulator() {
  const [selectedEnquiry, setSelectedEnquiry] = useState(MOCK_ENQUIRIES[0]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [status, setStatus] = useState(selectedEnquiry.status);
  const [remarks, setRemarks] = useState(selectedEnquiry.remarks || '');
  const [toastMessage, setToastMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleUpdateStatus = (newStatus) => {
    // Mandatory Remarks Check for CLOSED or CONVERTED
    if ((newStatus === 'CLOSED' || newStatus === 'CONVERTED') && (!remarks || !remarks.trim())) {
      setErrorMessage("Mandatory remarks required before closing or converting an enquiry!");
      setTimeout(() => setErrorMessage(null), 4000);
      return;
    }

    setStatus(newStatus);
    setErrorMessage(null);
    setToastMessage(`✓ Status Updated: ${newStatus}`);
    setTimeout(() => setToastMessage(null), 3000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-teal-950/80 via-slate-900 to-slate-950 border border-teal-800/40 rounded-2xl p-5 mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-teal-500/20 text-teal-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-teal-500/30">
              Updated Workflow Simulator
            </span>
            <h2 className="text-lg font-bold text-white">Service Line Manager (SLM) Mobile App</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Handles broad queries (pricing, package, complaints), nullable audio sync, FCR push bypass, and mandatory remarks.
          </p>
        </div>
        <button className="bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all shadow-md shadow-teal-950 flex items-center gap-2">
          <Bell className="w-4 h-4" />
          <span>Simulate Push Alert</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Mobile App Queue Selection */}
        <div className="lg:col-span-5 space-y-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Clock className="w-4 h-4 text-teal-400" />
            Assigned Patient Lead Queue ({MOCK_ENQUIRIES.length})
          </h3>

          <div className="space-y-3">
            {MOCK_ENQUIRIES.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  setSelectedEnquiry(item);
                  setStatus(item.status);
                  setRemarks(item.remarks || '');
                  setErrorMessage(null);
                }}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  selectedEnquiry.id === item.id
                    ? 'bg-slate-900 border-teal-500/80 shadow-lg shadow-teal-950/40 ring-1 ring-teal-500/30'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-teal-400">{item.id}</span>
                  <div className="flex items-center gap-1.5">
                    {item.fcmBypassed && (
                      <span className="text-[9px] font-extrabold bg-purple-950 text-purple-300 border border-purple-800 px-2 py-0.5 rounded-full">
                        FCR (Agent Resolved)
                      </span>
                    )}
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      item.priority === 'URGENT' ? 'bg-red-950 text-red-300 border border-red-800' :
                      item.priority === 'HIGH' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                      'bg-blue-950 text-blue-300 border border-blue-800'
                    }`}>
                      {item.priority}
                    </span>
                  </div>
                </div>

                <h4 className="text-sm font-bold text-white">{item.patientName} ({item.age} yrs, {item.gender})</h4>
                <p className="text-xs text-teal-300/90 font-medium mt-0.5">{item.enquiryType}</p>
                
                <div className="flex items-center justify-between text-xs text-slate-400 mt-3 pt-2.5 border-t border-slate-800/80">
                  <span className="flex items-center gap-1 text-[11px]">
                    <Building className="w-3 h-3 text-slate-500" />
                    {item.branch}
                  </span>
                  <span className="text-[11px] text-slate-500">{item.timeAgo}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Smartphone UI Simulator Frame */}
        <div className="lg:col-span-7 flex justify-center">
          
          {/* Smartphone Hardware Shell */}
          <div className="w-full max-w-[380px] bg-slate-950 border-[10px] border-slate-800 rounded-[48px] shadow-2xl shadow-teal-950/60 p-3 relative overflow-hidden">
            
            {/* Camera Notch */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-5 bg-slate-800 rounded-b-xl z-30 flex items-center justify-center">
              <div className="w-3 h-3 bg-slate-900 rounded-full border border-slate-700"></div>
            </div>

            {/* Mobile App Screen Content */}
            <div className="bg-slate-900 rounded-[36px] pt-7 pb-4 px-4 min-h-[660px] flex flex-col justify-between text-slate-100 relative">
              
              {/* Toast & Error Banners */}
              {toastMessage && (
                <div className="absolute top-8 left-4 right-4 bg-teal-600 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-lg z-40 text-center animate-bounce">
                  {toastMessage}
                </div>
              )}
              {errorMessage && (
                <div className="absolute top-8 left-4 right-4 bg-red-900 text-red-100 text-[11px] font-bold py-2 px-3 rounded-xl shadow-lg z-40 text-center border border-red-700">
                  ⚠️ {errorMessage}
                </div>
              )}

              {/* Mobile App Header */}
              <div className="border-b border-slate-800 pb-3 mb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <div className="w-6 h-6 rounded-lg bg-teal-600 flex items-center justify-center font-bold text-[10px] text-white">
                      PH
                    </div>
                    <span className="text-xs font-bold text-white">Prashanth SLM App</span>
                  </div>
                  <span className="text-[10px] bg-teal-950 text-teal-300 font-semibold px-2 py-0.5 rounded-full border border-teal-800">
                    Broad Scope
                  </span>
                </div>
              </div>

              {/* Active Patient Card Detail */}
              <div className="space-y-3 flex-1 overflow-y-auto pr-1">
                
                {/* FCR Alert Badge if Agent Resolved */}
                {selectedEnquiry.fcmBypassed && (
                  <div className="bg-purple-950/80 border border-purple-800/80 p-2.5 rounded-xl text-purple-200 text-[11px] flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-purple-400 shrink-0" />
                    <span><b>FCR Bypass:</b> Resolved on call by Agent. Suppressed FCM alert.</span>
                  </div>
                )}

                {/* Patient Header */}
                <div className="bg-slate-950/80 p-3.5 rounded-2xl border border-slate-800">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-bold text-teal-400">{selectedEnquiry.id}</span>
                    <span className="text-[10px] font-semibold text-slate-400">{selectedEnquiry.branch}</span>
                  </div>
                  <h3 className="text-sm font-extrabold text-white">{selectedEnquiry.patientName}</h3>
                  <p className="text-xs text-slate-300 mt-0.5">{selectedEnquiry.phone} • {selectedEnquiry.gender}, {selectedEnquiry.age}y</p>
                  <p className="text-xs font-medium text-teal-300 mt-1">{selectedEnquiry.enquiryType}</p>
                </div>

                {/* Nullable Voice Path Audio Component */}
                <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold text-slate-300 flex items-center gap-1">
                      <Phone className="w-3 h-3 text-teal-400" />
                      XTEND Call Recording
                    </span>
                    <span className="text-[10px] text-slate-500">
                      {selectedEnquiry.recordingUrl ? selectedEnquiry.audioDuration : 'Audio Pending'}
                    </span>
                  </div>
                  
                  {selectedEnquiry.recordingUrl ? (
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="w-8 h-8 rounded-full bg-teal-600 hover:bg-teal-500 flex items-center justify-center text-white transition-all"
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

                {/* Doctor / Treatment & Mandatory Remarks Input */}
                <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800 space-y-2">
                  <span className="text-[11px] font-bold text-slate-300 flex items-center gap-1">
                    <UserCheck className="w-3 h-3 text-teal-400" />
                    Doctor & Mandatory Remarks
                  </span>
                  <p className="text-xs text-white font-semibold">{selectedEnquiry.doctorName}</p>
                  
                  <textarea
                    value={remarks}
                    onChange={(e) => setRemarks(e.target.value)}
                    placeholder="Enter mandatory resolution remarks prior to archiving..."
                    rows={2}
                    className="w-full bg-slate-900 border border-slate-800 text-xs text-slate-200 p-2 rounded-lg focus:outline-none focus:border-teal-500 resize-none"
                  />
                </div>

                {/* Status Picker */}
                <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800 space-y-2">
                  <label className="text-[11px] font-bold text-slate-300 block">
                    Update Status (Mandatory Remarks for Closed):
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

              {/* Action Toolbar */}
              <div className="pt-3 border-t border-slate-800 grid grid-cols-2 gap-2">
                <button className="bg-teal-600 hover:bg-teal-500 text-white font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all shadow-md">
                  <Phone className="w-3.5 h-3.5" />
                  <span>Call Patient</span>
                </button>
                <button className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all shadow-md">
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
