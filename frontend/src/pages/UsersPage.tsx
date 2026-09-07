import React, { useState, useEffect } from 'react';
import {
  Users,
  UserPlus,
  Shield,
  Briefcase,
  CheckCircle2,
  XCircle,
  Search,
  Filter,
  Trash2,
  Edit2,
  AlertCircle,
  RefreshCw,
  Lock
} from 'lucide-react';
import { userService, CreateUserData } from '../services/userService';
import { User } from '../types';

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New user form state
  const [formData, setFormData] = useState<CreateUserData>({
    name: '',
    username: '',
    email: '',
    password: '',
    role: 'PROCUREMENT_OFFICER',
    department: 'Pipeline Operations'
  });

  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await userService.getUsers(roleFilter === 'ALL' ? undefined : roleFilter);
      setUsers(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch users.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [roleFilter]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    try {
      await userService.createUser(formData);
      setSuccessMsg(`User ${formData.username} created successfully.`);
      setShowCreateModal(false);
      setFormData({
        name: '',
        username: '',
        email: '',
        password: '',
        role: 'PROCUREMENT_OFFICER',
        department: 'Pipeline Operations'
      });
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create user.');
    }
  };

  const handleToggleActive = async (user: User) => {
    try {
      await userService.updateUser(user.id, { is_active: !user.is_active });
      setUsers(users.map(u => u.id === user.id ? { ...u, is_active: !u.is_active } : u));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update user status.');
    }
  };

  const handleDeleteUser = async (user: User) => {
    if (!window.confirm(`Are you sure you want to deactivate/delete user '${user.username}'?`)) {
      return;
    }
    try {
      await userService.deleteUser(user.id);
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete user.');
    }
  };

  const filteredUsers = users.filter(u => {
    const q = searchQuery.toLowerCase();
    return (
      u.name?.toLowerCase().includes(q) ||
      u.username?.toLowerCase().includes(q) ||
      u.email?.toLowerCase().includes(q) ||
      u.role?.toLowerCase().includes(q) ||
      u.department?.toLowerCase().includes(q)
    );
  });

  const adminCount = users.filter(u => u.role === 'ADMIN').length;
  const officerCount = users.filter(u => u.role === 'PROCUREMENT_OFFICER').length;
  const bidderCount = users.filter(u => u.role === 'BIDDER').length;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#D9DEE3] pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-[#10283A] text-white rounded-lg shadow-sm">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-serif font-bold text-[#10283A]">
                User Management &amp; Access Control
              </h1>
              <p className="text-xs text-[#66717C] mt-0.5">
                Centralized administration for system users, RBAC roles, and portal credentials
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#10283A] text-white text-xs font-semibold rounded-lg hover:bg-[#18374D] shadow transition-colors"
        >
          <UserPlus className="w-4 h-4" />
          Create New User
        </button>
      </div>

      {/* Notifications */}
      {error && (
        <div className="p-3 bg-[#FEF2F2] border border-[#FCA5A5] text-[#991B1B] text-xs rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-3 bg-[#ECFDF5] border border-[#6EE7B7] text-[#065F46] text-xs rounded-lg flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white border border-[#D9DEE3] rounded-xl p-4 shadow-sm">
          <div className="text-xs text-[#66717C] font-semibold uppercase">Total Users</div>
          <div className="text-2xl font-bold text-[#10283A] mt-1">{users.length}</div>
        </div>
        <div className="bg-white border border-[#D9DEE3] rounded-xl p-4 shadow-sm">
          <div className="text-xs text-[#66717C] font-semibold uppercase">Admins</div>
          <div className="text-2xl font-bold text-[#1E40AF] mt-1">{adminCount}</div>
        </div>
        <div className="bg-white border border-[#D9DEE3] rounded-xl p-4 shadow-sm">
          <div className="text-xs text-[#66717C] font-semibold uppercase">Procurement Officers</div>
          <div className="text-2xl font-bold text-[#065F46] mt-1">{officerCount}</div>
        </div>
        <div className="bg-white border border-[#D9DEE3] rounded-xl p-4 shadow-sm">
          <div className="text-xs text-[#66717C] font-semibold uppercase">Registered Bidders</div>
          <div className="text-2xl font-bold text-[#92400E] mt-1">{bidderCount}</div>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white border border-[#D9DEE3] rounded-xl p-3.5 flex flex-col sm:flex-row gap-3 items-center justify-between shadow-sm">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-[#8C9BA5] absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by name, username, email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 border border-[#D9DEE3] rounded-md text-xs text-[#17212B] focus:outline-none focus:border-[#10283A]"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-[#66717C]" />
          <span className="text-xs text-[#66717C] font-medium">Role:</span>
          {(['ALL', 'ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setRoleFilter(r)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                roleFilter === r
                  ? 'bg-[#10283A] text-white'
                  : 'bg-[#F4F5F7] text-[#4A5568] hover:bg-[#E2E8F0]'
              }`}
            >
              {r === 'ALL' ? 'All Roles' : r.replace('_', ' ')}
            </button>
          ))}
          <button
            onClick={fetchUsers}
            title="Refresh list"
            className="p-1.5 text-[#66717C] hover:text-[#10283A] rounded hover:bg-[#F4F5F7] transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white border border-[#D9DEE3] rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F8FAFC] border-b border-[#D9DEE3] text-[#66717C] uppercase font-semibold">
              <tr>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Department</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Joined</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-[#66717C]">
                    Loading user records...
                  </td>
                </tr>
              ) : filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-[#66717C]">
                    No users found matching the criteria.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u) => {
                  const roleBadge =
                    u.role === 'ADMIN'
                      ? 'bg-[#EFF6FF] text-[#1D4ED8] border-[#BFDBFE]'
                      : u.role === 'PROCUREMENT_OFFICER'
                      ? 'bg-[#ECFDF5] text-[#047857] border-[#A7F3D0]'
                      : 'bg-[#FFFBEB] text-[#B45309] border-[#FDE68A]';

                  return (
                    <tr key={u.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="px-4 py-3">
                        <div className="font-semibold text-[#10283A]">{u.name || u.username}</div>
                        <div className="text-[#66717C] text-[11px] font-mono">@{u.username} · {u.email}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${roleBadge}`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[#4B5563]">
                        {u.department || '—'}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => handleToggleActive(u)}
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                            u.is_active
                              ? 'bg-[#DCFCE7] text-[#15803D] hover:bg-[#BBF7D0]'
                              : 'bg-[#FEE2E2] text-[#B91C1C] hover:bg-[#FECACA]'
                          }`}
                        >
                          {u.is_active ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                          {u.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      <td className="px-4 py-3 text-[#66717C] text-[11px]">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => handleDeleteUser(u)}
                          title="Deactivate / Delete user"
                          className="p-1.5 text-[#DC2626] hover:bg-[#FEE2E2] rounded transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-[#D9DEE3] space-y-4">
            <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-3">
              <h3 className="font-serif font-bold text-[#10283A] text-lg">Create System User</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-[#66717C] hover:text-[#10283A] text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-3 text-xs">
              <div>
                <label className="block text-[#4B5563] font-semibold mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Ramesh Chandra"
                  className="w-full px-3 py-2 border border-[#D9DEE3] rounded-md focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div>
                <label className="block text-[#4B5563] font-semibold mb-1">Username</label>
                <input
                  type="text"
                  required
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="e.g. ramesh_procurement"
                  className="w-full px-3 py-2 border border-[#D9DEE3] rounded-md focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div>
                <label className="block text-[#4B5563] font-semibold mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="ramesh@mopng.gov.in"
                  className="w-full px-3 py-2 border border-[#D9DEE3] rounded-md focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div>
                <label className="block text-[#4B5563] font-semibold mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="••••••••••••"
                  className="w-full px-3 py-2 border border-[#D9DEE3] rounded-md focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#4B5563] font-semibold mb-1">Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                    className="w-full px-3 py-2 border border-[#D9DEE3] rounded-md focus:outline-none focus:border-[#10283A] bg-white"
                  >
                    <option value="ADMIN">ADMIN</option>
                    <option value="PROCUREMENT_OFFICER">PROCUREMENT_OFFICER</option>
                    <option value="BIDDER">BIDDER</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[#4B5563] font-semibold mb-1">Department</label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    placeholder="e.g. Pipelines & Infra"
                    className="w-full px-3 py-2 border border-[#D9DEE3] rounded-md focus:outline-none focus:border-[#10283A]"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-[#E2E8F0]">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-[#D9DEE3] text-[#4B5563] rounded-md hover:bg-[#F3F4F6]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#10283A] text-white rounded-md hover:bg-[#18374D] font-semibold"
                >
                  Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
