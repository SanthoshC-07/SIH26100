import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Flag, Shield, UserCheck, Lock, User, AlertCircle } from 'lucide-react';
import { authService } from '../services/authService';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [loginMode, setLoginMode] = useState<'OFFICER' | 'BIDDER'>('OFFICER');
  const [username, setUsername] = useState('procurement_officer');
  const [password, setPassword] = useState('officer123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const performLogin = async (userToAuth: string, passToAuth: string) => {
    setLoading(true);
    setError('');

    try {
      const res = await authService.login(userToAuth, passToAuth);

      if (res && res.access_token) {
        const serverUser = res.user;
        const role = serverUser?.role || 'BIDDER';

        localStorage.removeItem('active_role'); // Clear any legacy role overrides

        if (role === 'ADMIN') {
          navigate('/admin/dashboard');
        } else if (role === 'PROCUREMENT_OFFICER') {
          navigate('/officer/dashboard');
        } else {
          navigate('/bidder/dashboard');
        }
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Invalid credentials. Please verify your authentication details.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    await performLogin(username, password);
  };

  return (
    <div className="min-h-screen w-full flex flex-col justify-between items-center relative overflow-hidden select-none bg-[#0D0807]">
      
      {/* ── Real Sunset Sky & Oil Rig Landscape (matches PDF Pages 1 & 2) ── */}
      <div 
        className="absolute inset-0 pointer-events-none z-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: 'url(/images/oil_sunset_login.jpg)',
        }}
      >
        {/* Subtle dark vignette overlay to ensure pristine card contrast */}
        <div className="absolute inset-0 bg-black/25 backdrop-brightness-90" />
      </div>

      {/* ── Top Left Brand Header (from PDF Page 1 & 2) ── */}
      <div className="w-full max-w-7xl mx-auto px-6 sm:px-10 pt-8 z-10 flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          {/* Square Logo Badge */}
          <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center p-1.5 shadow-md shrink-0 aspect-square overflow-hidden">
            <img 
              src="/images/petrobid_emblem_square.png" 
              alt="PetroBid" 
              className="w-full h-full object-contain"
            />
          </div>
          <div>
            <div className="font-serif font-bold text-xl text-white tracking-tight leading-tight">
              PetroBid
            </div>
            <div className="text-[11px] text-[#BAC7D5] tracking-normal mt-0.5">
              Government Procurement &amp; Role-Based Compliance System
            </div>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-[11px] font-sans text-[#E2E8F0] bg-black/40 px-3 py-1 rounded-full border border-white/10 backdrop-blur-sm">
          <span className="w-2 h-2 rounded-full bg-[#198754] inline-block animate-pulse" />
          <span>MoPNG Pipeline Procurement RBAC Server Online</span>
        </div>
      </div>

      {/* ── Center Login Card (from PDF Pages 1 & 2) ── */}
      <div className="w-full max-w-md mx-4 my-8 z-10 relative">
        
        {/* Floating Top Badge */}
        <div className="absolute -top-6 left-1/2 -translate-x-1/2 z-20">
          {loginMode === 'OFFICER' ? (
            <div className="w-12 h-12 rounded-full bg-[#10283A] text-[#D98A16] flex items-center justify-center shadow-lg border-[3px] border-white">
              <Flag className="w-5 h-5 fill-[#D98A16]" />
            </div>
          ) : (
            <div className="w-12 h-12 rounded-full bg-[#D98A16] text-white flex items-center justify-center font-serif font-bold text-xl shadow-lg border-[3px] border-white">
              B
            </div>
          )}
        </div>

        {/* White Rectangular Card */}
        <div className="bg-white rounded-xl pt-10 pb-8 px-8 sm:px-10 shadow-2xl border border-white/50 text-[#17212B]">
          
          <div className="text-center mb-6">
            <h1 className="font-serif text-2xl font-bold text-[#10283A]">
              {loginMode === 'OFFICER' ? 'Authority & Officer Login' : 'Bidder Portal Login'}
            </h1>
            <p className="text-xs text-[#66717C] mt-1.5 font-sans">
              {loginMode === 'OFFICER' 
                ? 'For Admins & Procurement Selecting Officers' 
                : 'For registered bidders & contractors applying with documents'}
            </p>
          </div>

          {error && (
            <div className="mb-4 p-2.5 bg-[#FDF2F2] text-[#C83B32] border border-[#F7BEBE] text-xs rounded flex items-center gap-2 font-sans">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-[#66717C] uppercase tracking-[0.08em] mb-1.5 font-sans">
                {loginMode === 'OFFICER' ? 'OFFICER / ADMIN USERNAME' : 'BIDDER USERNAME / EMAIL'}
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={loginMode === 'OFFICER' ? 'procurement_officer or admin' : 'bidder'}
                className="w-full px-3.5 py-2.5 bg-white border border-[#D9DEE3] rounded-md text-sm text-[#17212B] placeholder-[#8C9BA5] focus:outline-none focus:border-[#10283A] transition-colors"
              />
            </div>

            <div>
              <label className="block text-[10px] font-bold text-[#66717C] uppercase tracking-[0.08em] mb-1.5 font-sans">
                PASSWORD
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••"
                className="w-full px-3.5 py-2.5 bg-white border border-[#D9DEE3] rounded-md text-sm text-[#17212B] placeholder-[#8C9BA5] focus:outline-none focus:border-[#10283A] transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 mt-2 bg-[#10283A] hover:bg-[#18374D] text-white text-sm font-semibold rounded-md shadow transition-colors flex items-center justify-center gap-2 font-sans disabled:opacity-60"
            >
              {loading 
                ? 'Authenticating...' 
                : loginMode === 'OFFICER' 
                ? 'Sign In to Official Console' 
                : 'Sign In to Bidder Portal'}
            </button>
          </form>

          <div className="text-center text-[11px] text-[#8C9BA5] mt-4 pt-2">
            {loginMode === 'OFFICER' 
              ? 'Role-based access enforced · Activity is logged for GFR 2017 audit trail' 
              : 'Registered EPC bidders can apply and upload required documents'}
          </div>

          {/* Quick Demo Access Buttons for 3 Personas */}
          <div className="mt-6 pt-4 border-t border-[#D9DEE3] text-left">
            <div className="text-[10px] text-[#66717C] uppercase font-bold tracking-wider mb-2">
              Instant Role Sign-In Credentials:
            </div>
            <div className="grid grid-cols-3 gap-1.5">
              <button
                type="button"
                onClick={() => {
                  setLoginMode('BIDDER');
                  setUsername('bidder');
                  setPassword('bidder123');
                }}
                className="p-2 bg-[#F4F5F7] hover:bg-[#FEF7EC] border border-[#D9DEE3] hover:border-[#D98A16] rounded text-left transition-colors"
              >
                <div className="font-semibold text-[11px] text-[#10283A] leading-tight">1. Bidder</div>
                <div className="text-[9px] text-[#D98A16] font-semibold mt-0.5">Applies & Uploads</div>
                <div className="text-[9px] text-[#66717C] font-mono mt-0.5">bidder</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setLoginMode('OFFICER');
                  setUsername('procurement_officer');
                  setPassword('officer123');
                }}
                className="p-2 bg-[#F4F5F7] hover:bg-[#EAF5F0] border border-[#D9DEE3] hover:border-[#198754] rounded text-left transition-colors"
              >
                <div className="font-semibold text-[11px] text-[#10283A] leading-tight">2. Officer</div>
                <div className="text-[9px] text-[#198754] font-semibold mt-0.5">Selecting Authority</div>
                <div className="text-[9px] text-[#66717C] font-mono mt-0.5">procurement_officer</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setLoginMode('OFFICER');
                  setUsername('admin');
                  setPassword('admin123');
                }}
                className="p-2 bg-[#F4F5F7] hover:bg-[#EBF2F7] border border-[#D9DEE3] hover:border-[#10283A] rounded text-left transition-colors"
              >
                <div className="font-semibold text-[11px] text-[#10283A] leading-tight">3. Admin</div>
                <div className="text-[9px] text-[#10283A] font-semibold mt-0.5">Creates Tenders</div>
                <div className="text-[9px] text-[#66717C] font-mono mt-0.5">admin</div>
              </button>
            </div>
          </div>

        </div>
      </div>

      {/* ── Bottom Switch Link (from PDF Page 1 & 2) ── */}
      <div className="pb-8 z-10 text-center">
        {loginMode === 'OFFICER' ? (
          <button
            type="button"
            onClick={() => {
              setLoginMode('BIDDER');
              setUsername('vendor@company.com');
              setPassword('bidder123');
            }}
            className="text-sm text-white/90 hover:text-white font-sans transition-colors cursor-pointer hover:underline"
          >
            Are you a bidder? Use the App User login &rarr;
          </button>
        ) : (
          <button
            type="button"
            onClick={() => {
              setLoginMode('OFFICER');
              setUsername('procurement_officer');
              setPassword('officer123');
            }}
            className="text-sm text-white/90 hover:text-white font-sans transition-colors cursor-pointer hover:underline"
          >
            Are you an officer? Use the Officer login &rarr;
          </button>
        )}
      </div>

    </div>
  );
};
