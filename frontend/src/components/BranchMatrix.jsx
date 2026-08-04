import React, { useState, useEffect } from 'react';
import { PRASHANTH_BRANCHES } from '../data/mockData';
import { Building2, MapPin, Clock, Activity, PlusCircle, X, CheckCircle2 } from 'lucide-react';

const API_BASE = '/api/v1';

export default function BranchMatrix() {
  const [branches, setBranches] = useState(PRASHANTH_BRANCHES);
  const [showModal, setShowModal] = useState(false);
  const [newCode, setNewCode] = useState('');
  const [newName, setNewName] = useState('');
  const [newCity, setNewCity] = useState('');
  const [newType, setNewType] = useState('HOSPITAL');
  const [newStatus, setNewStatus] = useState('ACTIVE');
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const fetchBranches = async () => {
    try {
      const res = await fetch(`${API_BASE}/branches`);
      if (res.ok) {
        const data = await res.json();
        if (data.branches) setBranches(data.branches);
      }
    } catch (e) {
      console.log('Using local branch data fallback');
    }
  };

  useEffect(() => {
    fetchBranches();
  }, []);

  const handleAddBranch = async (e) => {
    e.preventDefault();
    if (!newCode || !newName || !newCity) {
      setErrorMsg('Please fill in all required branch fields.');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/branches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: newCode.toUpperCase(),
          name: newName,
          city: newCity,
          type: newType,
          status: newStatus
        })
      });

      if (res.ok) {
        const data = await res.json();
        setBranches(prev => [...prev, data.branch]);
        setSuccessMsg(`Branch ${data.branch.name} added successfully!`);
        setTimeout(() => {
          setShowModal(false);
          setSuccessMsg('');
          setNewCode('');
          setNewName('');
          setNewCity('');
        }, 1500);
      } else {
        const err = await res.json();
        setErrorMsg(err.detail || 'Failed to add branch');
      }
    } catch (err) {
      // Local fallback addition
      const b = {
        id: `b${branches.length + 1}`,
        code: newCode.toUpperCase(),
        name: newName,
        city: newCity,
        type: newType,
        status: newStatus,
        leadsToday: 0
      };
      setBranches(prev => [...prev, b]);
      setSuccessMsg(`Branch ${b.name} added locally!`);
      setTimeout(() => {
        setShowModal(false);
        setSuccessMsg('');
        setNewCode('');
        setNewName('');
        setNewCity('');
      }, 1500);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      
      {/* Banner */}
      <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-teal-400" />
            Prashanth Hospitals Multi-Branch Infrastructure & Expansion Matrix
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Dynamic tenant architecture supporting Kolathur Call Center Hub, active hospital branches, upcoming branches, and IVF clinics network.
          </p>
        </div>
        <button
          onClick={() => {
            setShowModal(true);
            setErrorMsg('');
            setSuccessMsg('');
          }}
          className="bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all shadow-md flex items-center gap-1.5"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Add New Branch</span>
        </button>
      </div>

      {/* Grid of Branches */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {branches.map((branch) => (
          <div
            key={branch.id}
            className={`p-5 rounded-2xl border transition-all ${
              branch.status === 'ACTIVE'
                ? 'bg-slate-900/80 border-slate-800 hover:border-teal-500/50 shadow-md'
                : 'bg-slate-950/60 border-slate-800/80 opacity-90'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-teal-400 bg-teal-950 px-2.5 py-1 rounded-lg border border-teal-800">
                {branch.code}
              </span>
              <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                branch.status === 'ACTIVE'
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  : 'bg-amber-950 text-amber-300 border border-amber-800'
              }`}>
                {branch.status === 'ACTIVE' ? 'Active Branch' : 'Upcoming Branch'}
              </span>
            </div>

            <h3 className="text-base font-extrabold text-white">{branch.name}</h3>
            <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              {branch.city}
            </p>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-slate-400">Type: <b className="text-slate-200">{branch.type}</b></span>
              {branch.status === 'ACTIVE' ? (
                <span className="text-teal-300 font-bold flex items-center gap-1">
                  <Activity className="w-3 h-3 text-teal-400" />
                  Live XTEND Routing
                </span>
              ) : (
                <span className="text-amber-400 font-semibold flex items-center gap-1">
                  <Clock className="w-3 h-3 text-amber-400" />
                  Opening Shortly
                </span>
              )}
            </div>

          </div>
        ))}
      </div>

      {/* Add Branch Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 w-full max-w-md space-y-4 shadow-2xl relative">
            
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-extrabold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-teal-400" />
              Add Expansion Branch
            </h3>
            <p className="text-xs text-slate-400">
              Register a new hospital branch or IVF clinic unit into the Prashanth Hospitals routing matrix.
            </p>

            {errorMsg && (
              <div className="bg-red-950/80 border border-red-800 text-red-300 text-xs p-2.5 rounded-xl font-semibold">
                {errorMsg}
              </div>
            )}

            {successMsg && (
              <div className="bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-xs p-2.5 rounded-xl font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>{successMsg}</span>
              </div>
            )}

            <form onSubmit={handleAddBranch} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Branch Code (3 Letters)</label>
                <input
                  type="text"
                  maxLength={4}
                  placeholder="e.g. GUD"
                  value={newCode}
                  onChange={(e) => setNewCode(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-teal-500 uppercase font-bold"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Branch Name</label>
                <input
                  type="text"
                  placeholder="e.g. Guduvanchery Branch"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">City / Region</label>
                <input
                  type="text"
                  placeholder="e.g. Chennai South Suburbs"
                  value={newCity}
                  onChange={(e) => setNewCity(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-teal-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Facility Type</label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-teal-500"
                  >
                    <option value="HOSPITAL">HOSPITAL</option>
                    <option value="FERTILITY">FERTILITY</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Status</label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-teal-500"
                  >
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="UPCOMING">UPCOMING</option>
                  </select>
                </div>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  className="w-full bg-teal-600 hover:bg-teal-500 text-white font-bold py-2.5 rounded-xl transition-all shadow-md"
                >
                  Save Branch
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

    </div>
  );
}
