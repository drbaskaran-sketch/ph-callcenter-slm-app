import React from 'react';
import { PRASHANTH_BRANCHES } from '../data/mockData';
import { Building2, MapPin, CheckCircle2, Clock, Activity, PlusCircle } from 'lucide-react';

export default function BranchMatrix() {
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
        <button className="bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all shadow-md flex items-center gap-1.5">
          <PlusCircle className="w-4 h-4" />
          <span>Add New Branch</span>
        </button>
      </div>

      {/* Grid of Branches */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {PRASHANTH_BRANCHES.map((branch) => (
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

    </div>
  );
}
