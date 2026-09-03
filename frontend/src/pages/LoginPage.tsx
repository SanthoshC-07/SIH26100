import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('procurement_officer');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await authService.login(username, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication rejected. Verify officer credentials.');
    } finally {
      setLoading(false);
    }
  };

  const setDemoRole = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen bg-[#F4F5F2] flex items-center justify-center p-6">
      
      {/* Split-Screen Institutional Container */}
      <div className="max-w-4xl w-full border border-[#D8DCD6] bg-white grid grid-cols-1 md:grid-cols-2 shadow-xl">
        
        {/* Left Side: Dark Institutional Panel */}
        <div className="bg-[#101A17] p-8 md:p-10 text-white flex flex-col justify-between border-b md:border-b-0 md:border-r border-[#22322C]">
          <div className="space-y-6">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-[#163C32] border border-[#2D5A4E] flex items-center justify-center font-mono font-bold text-xs text-white">
                GeM
              </div>
              <div className="font-mono text-xs font-bold tracking-widest uppercase text-[#EDEFEA]">
                CPCL / INTEGRATED COMPLIANCE
              </div>
            </div>

            <div className="space-y-3 pt-4">
              <span className="text-[10px] font-mono tracking-widest uppercase text-[#A7833B]">
                GOVERNMENT DIGITAL INFRASTRUCTURE
              </span>
              <h1 className="text-xl font-bold tracking-tight text-white leading-snug">
                AI-Powered Integrated Bid Compliance Verification Platform
              </h1>
              <p className="text-xs text-[#9DAAA2] leading-relaxed">
                Deterministic statutory verification, multi-portal cross-referencing, and evidence-grounded decision support for public procurement.
              </p>
            </div>
          </div>

          <div className="pt-8 border-t border-[#22322C] text-[10px] font-mono text-[#5F6E66] space-y-1">
            <div>CENTRAL PROCUREMENT CONTROL LAYER</div>
            <div>COMPLIANT WITH GFR SECTION 4 AUDIT STANDARDS</div>
          </div>
        </div>

        {/* Right Side: Clean Sharp Login Form */}
        <div className="p-8 md:p-10 flex flex-col justify-between bg-[#FCFCFA]">
          <div>
            <div className="pb-4 border-b border-[#D8DCD6] mb-6">
              <h2 className="text-sm font-mono font-bold tracking-wider uppercase text-[#17201C]">
                OFFICER AUTHENTICATION
              </h2>
              <p className="text-[11px] text-[#59625D]">
                Enter authorized credentials to access compliance evaluations
              </p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4 text-xs font-mono">
              
              {error && (
                <div className="p-3 bg-[#FBEBEB] text-[#7A1C1C] border border-[#F1B5B5] text-xs">
                  {error}
                </div>
              )}

              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold uppercase tracking-wider text-[#59625D]">
                  OFFICER IDENTIFIER / EMAIL
                </label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. procurement_officer"
                  className="w-full border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] focus:border-[#163C32] outline-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold uppercase tracking-wider text-[#59625D]">
                  SECURITY PASSPHRASE
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] focus:border-[#163C32] outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-[#163C32] hover:bg-[#0E2922] text-white text-xs font-bold uppercase tracking-wider transition-colors disabled:opacity-50 mt-2"
              >
                {loading ? 'VERIFYING CREDENTIALS...' : 'ACCESS COMPLIANCE PORTAL'}
              </button>

            </form>
          </div>

          {/* Instant Demo Quick Access */}
          <div className="pt-6 border-t border-[#D8DCD6] mt-6 text-center space-y-2 font-mono">
            <span className="text-[10px] uppercase text-[#59625D] tracking-wider block font-bold">
              DEMONSTRATION ACCESS PRESETS
            </span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setDemoRole('procurement_officer', 'password123')}
                className="py-1.5 px-2 border border-[#D8DCD6] bg-white hover:bg-[#EDEFEA] text-[10px] font-semibold text-[#17201C] transition-colors"
              >
                PROCUREMENT OFFICER
              </button>
              <button
                type="button"
                onClick={() => setDemoRole('admin', 'admin123')}
                className="py-1.5 px-2 border border-[#D8DCD6] bg-white hover:bg-[#EDEFEA] text-[10px] font-semibold text-[#17201C] transition-colors"
              >
                ADMINISTRATOR
              </button>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
