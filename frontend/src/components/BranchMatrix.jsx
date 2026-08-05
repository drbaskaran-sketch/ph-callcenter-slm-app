import React, { useState, useEffect } from 'react';
import { PRASHANTH_BRANCHES } from '../data/mockData';
import { Building2, MapPin, Clock, Activity, PlusCircle, Trash2, X, CheckCircle2, AlertTriangle } from 'lucide-react';
import { apiFetch, API_BASE } from '../api';

export default function BranchMatrix() {
  const [branches, setBranches] = useState(PRASHANTH_BRANCHES);
  const [showAddModal, setShowAddModal] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const [newCode, setNewCode] = useState('');
  const [newName, setNewName] = useState('');
  const [newCity, setNewCity] = useState('');
  const [newType, setNewType] = useState('HOSPITAL');
  const [newStatus, setNewStatus] = useState('ACTIVE');
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const fetchBranches = async () => {
    try {
      const res = await apiFetch(`${API_BASE}/branches`);
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
      const res = await apiFetch(`${API_BASE}/branches`, {
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
          setShowAddModal(false);
          setSuccessMsg('');
          setNewCode('');
          setNewName('');
          setNewCity('');
        }, 1200);
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
        setShowAddModal(false);
        setSuccessMsg('');
        setNewCode('');
        setNewName('');
        setNewCity('');
      }, 1200);
    }
  };

  const handleDeleteBranch = async (idToDelete, branchName) => {
    try {
      await apiFetch(`${API_BASE}/branches/${idToDelete}`, {
        method: 'DELETE'
      });
    } catch (e) {
      console.log('Local branch delete fallback');
    }

    setBranches(prev => prev.filter(b => b.id !== idToDelete));
    setDeleteConfirmId(null);
    setSuccessMsg(`Branch ${branchName} removed successfully.`);
    setTimeout(() => setSuccessMsg(''), 3000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      
      {/* Top Banner */}
      <div className="bg-white border border-slate-200 p-5 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 shadow-sm">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-teal-700" />
            Prashanth Hospitals Multi-Branch Infrastructure & Expansion Matrix
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Dynamic tenant architecture supporting Kolathur Call Center Hub, active hospital branches, upcoming locations, and IVF clinics.
          </p>
        </div>

        <button
          onClick={() => {
            setShowAddModal(true);
            setErrorMsg('');
            setSuccessMsg('');
          }}
          className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition-all shadow-sm flex items-center gap-1.5 shrink-0"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Add New Branch</span>
        </button>
      </div>

      {successMsg && !showAddModal && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-3 rounded-xl font-bold flex items-center gap-2 shadow-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Grid of Branches */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {branches.map((branch) => (
          <div
            key={branch.id}
            className={`p-5 rounded-2xl border transition-all relative ${
              branch.status === 'ACTIVE'
                ? 'bg-white border-slate-200 hover:border-teal-400 shadow-sm'
                : 'bg-slate-50/80 border-slate-200 opacity-90'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-black text-teal-800 bg-teal-50 px-2.5 py-1 rounded-lg border border-teal-200">
                {branch.code}
              </span>

              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                  branch.status === 'ACTIVE'
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : 'bg-amber-100 text-amber-800 border border-amber-300'
                }`}>
                  {branch.status === 'ACTIVE' ? 'Active Branch' : 'Upcoming Branch'}
                </span>

                <button
                  onClick={() => setDeleteConfirmId(branch.id)}
                  title="Delete Branch"
                  className="p-1 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <h3 className="text-base font-extrabold text-slate-900">{branch.name}</h3>
            <p className="text-xs text-slate-500 flex items-center gap-1 mt-1 font-medium">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {branch.city}
            </p>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold">
              <span className="text-slate-500">Type: <b className="text-slate-800">{branch.type}</b></span>
              {branch.status === 'ACTIVE' ? (
                <span className="text-teal-700 font-bold flex items-center gap-1">
                  <Activity className="w-3.5 h-3.5 text-teal-600" />
                  Live XTEND Routing ({branch.leadsToday || 0} leads)
                </span>
              ) : (
                <span className="text-amber-700 font-bold flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-amber-600" />
                  Opening Shortly
                </span>
              )}
            </div>

            {/* Confirm Delete Banner on Card */}
            {deleteConfirmId === branch.id && (
              <div className="absolute inset-0 bg-white/95 backdrop-blur-xs rounded-2xl p-4 flex flex-col justify-center items-center text-center space-y-3 z-10 border border-red-300 shadow-md">
                <AlertTriangle className="w-6 h-6 text-red-600 animate-bounce" />
                <p className="text-xs font-bold text-slate-900">Delete branch {branch.name}?</p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDeleteBranch(branch.id, branch.name)}
                    className="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition-all"
                  >
                    Yes, Delete
                  </button>
                  <button
                    onClick={() => setDeleteConfirmId(null)}
                    className="bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-lg transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

          </div>
        ))}
      </div>

      {/* Add Branch Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 w-full max-w-md space-y-4 shadow-xl relative">
            
            <button
              onClick={() => setShowAddModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-700"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <Building2 className="w-5 h-5 text-teal-700" />
              Add Expansion Branch
            </h3>
            <p className="text-xs text-slate-500">
              Register a new hospital branch or IVF clinic unit into the Prashanth Hospitals routing matrix.
            </p>

            {errorMsg && (
              <div className="bg-red-50 border border-red-200 text-red-800 text-xs p-2.5 rounded-xl font-bold">
                {errorMsg}
              </div>
            )}

            {successMsg && (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-2.5 rounded-xl font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>{successMsg}</span>
              </div>
            )}

            <form onSubmit={handleAddBranch} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-700 font-bold mb-1">Branch Code (3 Letters)</label>
                <input
                  type="text"
                  maxLength={4}
                  placeholder="e.g. GUD"
                  value={newCode}
                  onChange={(e) => setNewCode(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-slate-900 focus:outline-none focus:border-teal-600 uppercase font-bold"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold mb-1">Branch Name</label>
                <input
                  type="text"
                  placeholder="e.g. Guduvanchery Branch"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-slate-900 focus:outline-none focus:border-teal-600 font-medium"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold mb-1">City / Region</label>
                <input
                  type="text"
                  placeholder="e.g. Chennai South Suburbs"
                  value={newCity}
                  onChange={(e) => setNewCity(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-slate-900 focus:outline-none focus:border-teal-600 font-medium"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-bold mb-1">Facility Type</label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-slate-900 focus:outline-none focus:border-teal-600 font-bold"
                  >
                    <option value="HOSPITAL">HOSPITAL</option>
                    <option value="FERTILITY">FERTILITY</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-700 font-bold mb-1">Status</label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-slate-900 focus:outline-none focus:border-teal-600 font-bold"
                  >
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="UPCOMING">UPCOMING</option>
                  </select>
                </div>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-2.5 rounded-xl transition-all shadow-sm"
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
