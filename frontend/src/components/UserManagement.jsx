import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Key, Shield, Building2, Phone, CheckCircle, Trash2, Edit, AlertCircle, RefreshCw } from 'lucide-react';
import { apiFetch, API_BASE } from '../api';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [slms, setSlms] = useState([]);
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(false);

  const [activeTab, setActiveTab] = useState('users'); // 'users' | 'slms'
  const [toastMessage, setToastMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // User modal state
  const [showUserModal, setShowUserModal] = useState(false);
  const [userForm, setUserForm] = useState({
    username: '',
    password: '',
    fullName: '',
    email: '',
    role: 'SLM',
    branchCode: 'ALL',
    slmId: ''
  });

  // Password Reset modal state
  const [resetModalUser, setResetModalUser] = useState(null);
  const [newPassword, setNewPassword] = useState('');

  // SLM modal state
  const [showSlmModal, setShowSlmModal] = useState(false);
  const [slmForm, setSlmForm] = useState({
    name: '',
    department: 'Cardiology',
    branchCode: 'KOL',
    phone: '',
    status: 'ON_DUTY',
    createUserAccount: true,
    username: '',
    password: ''
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resUsers, resSlms, resBranches] = await Promise.all([
        apiFetch(`${API_BASE}/users`),
        apiFetch(`${API_BASE}/slms`),
        apiFetch(`${API_BASE}/branches`)
      ]);

      if (resUsers.ok) {
        const d = await resUsers.json();
        setUsers(d.users || []);
      }
      if (resSlms.ok) {
        const d = await resSlms.json();
        setSlms(d.slms || []);
      }
      if (resBranches.ok) {
        const d = await resBranches.json();
        setBranches(d.branches || []);
      }
    } catch (err) {
      console.log('Error fetching user management data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const triggerError = (msg) => {
    setErrorMessage(msg);
    setTimeout(() => setErrorMessage(null), 4500);
  };

  // User Account Submission
  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!userForm.username || !userForm.password) {
      triggerError("Username and password are required.");
      return;
    }

    try {
      const res = await apiFetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userForm)
      });
      if (res.ok) {
        triggerToast(`✅ User account '${userForm.username}' created successfully.`);
        setShowUserModal(false);
        setUserForm({ username: '', password: '', fullName: '', email: '', role: 'SLM', branchCode: 'ALL', slmId: '' });
        fetchData();
      } else {
        const d = await res.json();
        triggerError(d.detail || "Failed to create user account.");
      }
    } catch (err) {
      triggerError("Server error while creating user account.");
    }
  };

  // Password Reset Submission
  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!newPassword || newPassword.length < 6) {
      triggerError("Password must be at least 6 characters.");
      return;
    }

    try {
      const res = await apiFetch(`${API_BASE}/users/${resetModalUser.id}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ newPassword })
      });
      if (res.ok) {
        triggerToast(`🔑 Password reset for '${resetModalUser.username}'.`);
        setResetModalUser(null);
        setNewPassword('');
      } else {
        const d = await res.json();
        triggerError(d.detail || "Password reset failed.");
      }
    } catch (err) {
      triggerError("Server error while resetting password.");
    }
  };

  // Delete User
  const handleDeleteUser = async (user) => {
    if (!window.confirm(`Are you sure you want to delete user '${user.username}'?`)) return;

    try {
      const res = await apiFetch(`${API_BASE}/users/${user.id}`, { method: 'DELETE' });
      if (res.ok) {
        triggerToast(`🗑️ User '${user.username}' deleted.`);
        fetchData();
      } else {
        const d = await res.json();
        triggerError(d.detail || "Failed to delete user.");
      }
    } catch (err) {
      triggerError("Server error while deleting user.");
    }
  };

  // SLM Creation Submission
  const handleCreateSlm = async (e) => {
    e.preventDefault();
    if (!slmForm.name || !slmForm.phone) {
      triggerError("SLM Name and Phone are required.");
      return;
    }
    if (slmForm.createUserAccount && (!slmForm.username || !slmForm.password)) {
      triggerError("Username and Password are required when auto-provisioning a user account.");
      return;
    }

    try {
      const res = await apiFetch(`${API_BASE}/slms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(slmForm)
      });
      if (res.ok) {
        const data = await res.json();
        triggerToast(`✅ SLM '${slmForm.name}' created${data.userCreated ? ` with account '${data.userCreated}'` : ''}.`);
        setShowSlmModal(false);
        setSlmForm({
          name: '', department: 'Cardiology', branchCode: 'KOL', phone: '', status: 'ON_DUTY',
          createUserAccount: true, username: '', password: ''
        });
        fetchData();
      } else {
        const d = await res.json();
        triggerError(d.detail || "Failed to create SLM.");
      }
    } catch (err) {
      triggerError("Server error while creating SLM.");
    }
  };

  // Delete SLM
  const handleDeleteSlm = async (slm) => {
    if (!window.confirm(`Are you sure you want to delete SLM '${slm.name}'?`)) return;

    try {
      const res = await apiFetch(`${API_BASE}/slms/${slm.id}`, { method: 'DELETE' });
      if (res.ok) {
        triggerToast(`🗑️ SLM '${slm.name}' removed from roster.`);
        fetchData();
      } else {
        const d = await res.json();
        triggerError(d.detail || "Failed to delete SLM.");
      }
    } catch (err) {
      triggerError("Server error while deleting SLM.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">

      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-5 rounded-2xl shadow-sm">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <Users className="w-5 h-5 text-teal-700" />
            User Master, Roles & SLM Roster Management
          </h2>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Configure system user accounts, role permissions (ADMIN, SUPERVISOR, SLM, BRANCH_HEAD), and Service Line Manager rosters.
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
            onClick={() => activeTab === 'users' ? setShowUserModal(true) : setShowSlmModal(true)}
            className="bg-teal-700 hover:bg-teal-800 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition-all"
          >
            <UserPlus className="w-4 h-4" />
            <span>{activeTab === 'users' ? 'New User Account' : 'Provision SLM Roster'}</span>
          </button>
        </div>
      </div>

      {/* Toast & Error Alerts */}
      {toastMessage && (
        <div className="bg-emerald-50 border border-emerald-300 text-emerald-900 px-4 py-3 rounded-xl text-xs font-extrabold flex items-center gap-2 shadow-xs">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          <span>{toastMessage}</span>
        </div>
      )}
      {errorMessage && (
        <div className="bg-rose-50 border border-rose-300 text-rose-900 px-4 py-3 rounded-xl text-xs font-extrabold flex items-center gap-2 shadow-xs">
          <AlertCircle className="w-4 h-4 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Sub Tabs */}
      <div className="flex border-b border-slate-200 gap-6 text-sm font-bold">
        <button
          onClick={() => setActiveTab('users')}
          className={`pb-3 flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'users' ? 'border-teal-700 text-teal-800' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Shield className="w-4 h-4" />
          <span>System Users ({users.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('slms')}
          className={`pb-3 flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'slms' ? 'border-teal-700 text-teal-800' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>SLM Roster & Accounts ({slms.length})</span>
        </button>
      </div>

      {/* TAB 1: USERS TABLE */}
      {activeTab === 'users' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">User ID & Username</th>
                  <th className="py-3 px-4">Full Name & Email</th>
                  <th className="py-3 px-4">Role & Scope</th>
                  <th className="py-3 px-4">Branch Scope</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-extrabold text-teal-800 block text-xs">{u.username}</span>
                      <span className="text-[10px] text-slate-400 font-bold">UID #{u.id}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-extrabold text-slate-900 block">{u.fullName}</span>
                      <span className="text-[10px] text-slate-500">{u.email || 'No email registered'}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`font-black text-[10px] px-2 py-0.5 rounded border ${
                        u.role === 'ADMIN' ? 'bg-purple-50 text-purple-800 border-purple-200' :
                        u.role === 'SUPERVISOR' ? 'bg-blue-50 text-blue-800 border-blue-200' :
                        u.role === 'BRANCH_HEAD' ? 'bg-amber-50 text-amber-800 border-amber-200' :
                        'bg-teal-50 text-teal-800 border-teal-200'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 text-[10px]">
                        {u.branchCode || 'ALL'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`font-bold text-[10px] px-2 py-0.5 rounded-full ${
                        u.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-500'
                      }`}>
                        {u.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => setResetModalUser(u)}
                        className="text-teal-700 hover:text-teal-900 bg-teal-50 px-2.5 py-1 rounded-lg border border-teal-200 text-[11px] font-bold inline-flex items-center gap-1"
                      >
                        <Key className="w-3 h-3" />
                        <span>Reset PW</span>
                      </button>
                      <button
                        onClick={() => handleDeleteUser(u)}
                        className="text-rose-600 hover:text-rose-800 bg-rose-50 px-2 py-1 rounded-lg border border-rose-200 text-[11px] font-bold inline-flex items-center"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: SLM ROSTER TABLE */}
      {activeTab === 'slms' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">SLM ID & Name</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Branch</th>
                  <th className="py-3 px-4">Phone Number</th>
                  <th className="py-3 px-4">Active Duty Status</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {slms.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-extrabold text-slate-900 block">{s.name}</span>
                      <span className="text-[10px] text-teal-800 font-bold">{s.id}</span>
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-800">{s.department}</td>
                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 text-[10px]">{s.branchCode}</span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-600">{s.phone}</td>
                    <td className="py-3 px-4">
                      <span className={`font-bold text-[10px] px-2.5 py-1 rounded-full ${
                        s.status === 'ON_DUTY' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {s.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-extrabold text-teal-800">{s.score}%</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDeleteSlm(s)}
                        className="text-rose-600 hover:text-rose-800 bg-rose-50 px-2.5 py-1 rounded-lg border border-rose-200 text-[11px] font-bold inline-flex items-center gap-1"
                      >
                        <Trash2 className="w-3 h-3" />
                        <span>Remove</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CREATE USER MODAL */}
      {showUserModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <UserPlus className="w-5 h-5 text-teal-700" />
              Create New System User Account
            </h3>

            <form onSubmit={handleCreateUser} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Username *</label>
                <input
                  type="text"
                  required
                  value={userForm.username}
                  onChange={e => setUserForm({ ...userForm, username: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                  placeholder="e.g. slm_vijay"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Password *</label>
                <input
                  type="password"
                  required
                  value={userForm.password}
                  onChange={e => setUserForm({ ...userForm, password: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                  placeholder="Minimum 6 characters"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Full Name</label>
                  <input
                    type="text"
                    value={userForm.fullName}
                    onChange={e => setUserForm({ ...userForm, fullName: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                    placeholder="Vijay Kumar"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Role Permission</label>
                  <select
                    value={userForm.role}
                    onChange={e => setUserForm({ ...userForm, role: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg font-bold text-slate-900"
                  >
                    <option value="ADMIN">ADMIN</option>
                    <option value="SUPERVISOR">SUPERVISOR</option>
                    <option value="SLM">SLM</option>
                    <option value="BRANCH_HEAD">BRANCH_HEAD</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Branch Scope</label>
                  <select
                    value={userForm.branchCode}
                    onChange={e => setUserForm({ ...userForm, branchCode: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg font-bold text-slate-900"
                  >
                    <option value="ALL">All Branches</option>
                    {branches.map(b => (
                      <option key={b.code} value={b.code}>{b.code} - {b.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Link to SLM Profile</label>
                  <select
                    value={userForm.slmId}
                    onChange={e => setUserForm({ ...userForm, slmId: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                  >
                    <option value="">None (Stand-alone Account)</option>
                    {slms.map(s => (
                      <option key={s.id} value={s.id}>{s.name} ({s.department})</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowUserModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-xl font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white rounded-xl font-bold shadow-xs"
                >
                  Save User Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* RESET PASSWORD MODAL */}
      {resetModalUser && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-slate-200 rounded-2xl max-w-sm w-full p-6 shadow-xl space-y-4">
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Key className="w-5 h-5 text-teal-700" />
              Reset Password for '{resetModalUser.username}'
            </h3>

            <form onSubmit={handleResetPassword} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">New Password *</label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                  placeholder="Enter new password (min 6 chars)"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setResetModalUser(null)}
                  className="px-4 py-2 border border-slate-300 rounded-xl font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white rounded-xl font-bold shadow-xs"
                >
                  Update Password
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CREATE SLM MODAL */}
      {showSlmModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Users className="w-5 h-5 text-teal-700" />
              Provision Service Line Manager (SLM) Roster
            </h3>

            <form onSubmit={handleCreateSlm} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">SLM Full Name *</label>
                <input
                  type="text"
                  required
                  value={slmForm.name}
                  onChange={e => setSlmForm({ ...slmForm, name: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                  placeholder="Dr. / Mr. Name"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Department Specialty *</label>
                  <input
                    type="text"
                    required
                    value={slmForm.department}
                    onChange={e => setSlmForm({ ...slmForm, department: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                    placeholder="Cardiology / IVF / Ortho"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Assigned Branch *</label>
                  <select
                    value={slmForm.branchCode}
                    onChange={e => setSlmForm({ ...slmForm, branchCode: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg font-bold text-slate-900"
                  >
                    {branches.map(b => (
                      <option key={b.code} value={b.code}>{b.code} - {b.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Contact Phone Number *</label>
                <input
                  type="text"
                  required
                  value={slmForm.phone}
                  onChange={e => setSlmForm({ ...slmForm, phone: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                  placeholder="+91 98400 00000"
                />
              </div>

              <div className="border-t border-slate-200 pt-3 space-y-2">
                <label className="flex items-center gap-2 font-bold text-teal-900 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={slmForm.createUserAccount}
                    onChange={e => setSlmForm({ ...slmForm, createUserAccount: e.target.checked })}
                    className="w-4 h-4 text-teal-700 rounded border-slate-300"
                  />
                  <span>Auto-Provision User Login Account</span>
                </label>

                {slmForm.createUserAccount && (
                  <div className="grid grid-cols-2 gap-3 pl-6 pt-1">
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Login Username *</label>
                      <input
                        type="text"
                        required={slmForm.createUserAccount}
                        value={slmForm.username}
                        onChange={e => setSlmForm({ ...slmForm, username: e.target.value })}
                        className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                        placeholder="slm_username"
                      />
                    </div>
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Login Password *</label>
                      <input
                        type="password"
                        required={slmForm.createUserAccount}
                        value={slmForm.password}
                        onChange={e => setSlmForm({ ...slmForm, password: e.target.value })}
                        className="w-full p-2 border border-slate-300 rounded-lg font-medium text-slate-900"
                        placeholder="Password"
                      />
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowSlmModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-xl font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white rounded-xl font-bold shadow-xs"
                >
                  Provision SLM Roster
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
