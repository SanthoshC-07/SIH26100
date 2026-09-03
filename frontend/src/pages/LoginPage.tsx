import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, ArrowRight, Eye, EyeOff, KeyRound } from 'lucide-react';
import api from '../services/api';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('procurement_officer');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 2FA Screen state (matching Page 2)
  const [show2FA, setShow2FA] = useState(false);
  const [otp, setOtp] = useState(['4', '8', '2', '1', '', '']);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      if (res.data && res.data.access_token) {
        localStorage.setItem('token', res.data.access_token);
        localStorage.setItem('user', JSON.stringify({
          username: username,
          role: username === 'admin' ? 'ADMIN' : 'PROCUREMENT_OFFICER',
          name: username === 'admin' ? 'Alex Rivera (Admin)' : 'Alex Rivera, Chief Auditor',
        }));
        navigate('/dashboard');
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
  };

  return (
    <div className="min-h-screen relative flex flex-col justify-between items-center p-6 bg-[#0B132B] overflow-hidden">
      
      {/* Background Ambience / Subtle Grid */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(37,99,235,0.25),rgba(255,255,255,0))]"></div>
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1E293B15_1px,transparent_1px),linear-gradient(to_bottom,#1E293B15_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>

      {/* Top Header Logo */}
      <div className="relative z-10 pt-8 text-center space-y-2">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600 shadow-glow mb-2">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          BidVerify AI Portal
        </h1>
        <p className="text-xs text-slate-400 max-w-sm mx-auto font-medium">
          Secure MoPNG Compliance & Petroleum Pipeline Procurement Integrity Verification System
        </p>
      </div>

      {/* Main Login Card (Matching Page 1 from PDF) */}
      <div className="relative z-10 w-full max-w-md my-8">
        {!show2FA ? (
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-100 p-8 space-y-6">
            
            <div className="space-y-1">
              <h2 className="text-lg font-bold text-slate-900">
                System Access
              </h2>
              <p className="text-xs text-slate-500">
                Authorized personnel only. Sessions are monitored and logged.
              </p>
            </div>

            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg font-medium">
                {error}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              
              {/* Username Input */}
              <div className="space-y-1.5">
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600">
                  GOVERNMENT EMAIL / USER ID
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="alex.rivera@procurement.gov"
                    className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:bg-white transition-all font-mono"
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600">
                    ACCESS CREDENTIAL
                  </label>
                  <span className="text-[11px] text-blue-600 hover:underline cursor-pointer font-medium">
                    Forgot Password?
                  </span>
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full pl-9 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:bg-white transition-all font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Remember Me Checkbox */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="remember"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="remember" className="text-xs text-slate-600 cursor-pointer select-none">
                  Trust this device for 30 days
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? 'Authenticating...' : 'Sign In to Dashboard'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            {/* Quick Demo Credentials */}
            <div className="pt-2 border-t border-slate-100">
              <div className="text-[10px] uppercase font-bold text-slate-400 mb-2 tracking-wider">
                Quick Demo Accounts
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => handleQuickLogin('procurement_officer', 'password123')}
                  className="p-2 text-left bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-200 rounded-lg transition-all"
                >
                  <div className="font-bold text-[11px] text-slate-800">Procurement Officer</div>
                  <div className="text-[10px] text-slate-500 font-mono">officer / pass123</div>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickLogin('admin', 'admin123')}
                  className="p-2 text-left bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-200 rounded-lg transition-all"
                >
                  <div className="font-bold text-[11px] text-slate-800">Admin Auditor</div>
                  <div className="text-[10px] text-slate-500 font-mono">admin / admin123</div>
                </button>
              </div>
            </div>

            {/* Encryption Badge */}
            <div className="text-center pt-2 flex items-center justify-center gap-1.5 text-[10px] font-mono text-slate-400">
              <KeyRound className="w-3.5 h-3.5 text-emerald-600" />
              <span>FIPS 140-2 COMPLIANT ENCRYPTION ACTIVE</span>
            </div>

          </div>
        ) : (
          /* 2FA Identity Verification (Matching Page 2 from PDF) */
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-100 p-8 space-y-6">
            <div className="space-y-1 text-center">
              <div className="inline-flex p-2.5 rounded-full bg-blue-50 text-blue-600 mb-2">
                <Shield className="w-6 h-6" />
              </div>
              <div className="text-[11px] uppercase font-bold tracking-wider text-blue-600">
                Two-Factor Authentication
              </div>
              <h2 className="text-lg font-bold text-slate-900">
                Verify Your Identity
              </h2>
              <p className="text-xs text-slate-500">
                We've sent a 6-digit verification code to your registered device ending in •••• 4821.
              </p>
            </div>

            {/* 6 Digit OTP Inputs */}
            <div className="flex justify-center gap-2">
              {otp.map((digit, idx) => (
                <input
                  key={idx}
                  type="text"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => {
                    const newOtp = [...otp];
                    newOtp[idx] = e.target.value;
                    setOtp(newOtp);
                  }}
                  className="w-11 h-12 text-center text-lg font-bold font-mono bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-600 focus:bg-white transition-all"
                />
              ))}
            </div>

            <button
              onClick={() => navigate('/dashboard')}
              className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm"
            >
              Verify & Continue →
            </button>

            <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
              <span>Code expires in: <strong className="font-mono text-slate-800">0:58</strong></span>
              <span className="text-blue-600 hover:underline cursor-pointer">Resend Code</span>
            </div>

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => setShow2FA(false)}
                className="text-xs text-slate-500 hover:text-slate-800 font-medium"
              >
                ← Back to Login
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Institutional Legal Footer */}
      <div className="relative z-10 text-center text-[11px] text-slate-500 space-y-2">
        <div className="flex items-center justify-center gap-4 text-slate-400">
          <span className="hover:text-slate-200 cursor-pointer">Privacy Policy</span>
          <span>•</span>
          <span className="hover:text-slate-200 cursor-pointer">Terms of Use</span>
          <span>•</span>
          <span className="hover:text-slate-200 cursor-pointer">Security Desk</span>
        </div>
        <p className="text-[10px] text-slate-600 max-w-lg mx-auto">
          Warning: Unauthorized access to this system is forbidden and will be prosecuted by law. By signing in, you agree to the Terms of Service.
        </p>
      </div>

    </div>
  );
};
