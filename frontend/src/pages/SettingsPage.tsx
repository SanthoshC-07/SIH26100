import React, { useEffect, useState } from 'react';
import { settingsService } from '../services';

export const SettingsPage: React.FC = () => {
  const [weights, setWeights] = useState({
    STATUTORY: 0.30,
    FINANCIAL: 0.25,
    TENDER_SPECIFIC: 0.20,
    DOCUMENTATION: 0.15,
    OTHER_ELIGIBILITY: 0.10
  });

  const [confidenceHigh, setConfidenceHigh] = useState(0.90);
  const [confidenceMedium, setConfidenceMedium] = useState(0.70);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    settingsService.getSettings().then((data) => {
      if (data.scoring_weights) setWeights(data.scoring_weights);
      if (data.confidence_high) setConfidenceHigh(data.confidence_high);
      if (data.confidence_medium) setConfidenceMedium(data.confidence_medium);
    }).finally(() => setLoading(false));
  }, []);

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (Math.abs(totalWeight - 1.0) > 0.01) {
      setMessage('Error: Total scoring weights must sum up exactly to 100% (1.0).');
      return;
    }

    setSaving(true);
    setMessage('');
    try {
      await settingsService.updateSettings({
        scoring_weights: weights,
        confidence_high: confidenceHigh,
        confidence_medium: confidenceMedium
      });
      setMessage('System compliance configuration successfully updated.');
    } catch (err: any) {
      setMessage('Failed to update settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 font-mono text-xs">
      
      {/* Header */}
      <div className="border border-[#D8DCD6] bg-white p-5">
        <div className="text-[10px] uppercase tracking-widest text-[#A7833B] font-bold">
          ENGINE CONFIGURATION & GATING PARAMETERS
        </div>
        <h1 className="text-base font-bold tracking-tight text-[#17201C] mt-0.5 uppercase">
          SYSTEM PARAMETERS & SCORING WEIGHTS
        </h1>
        <p className="text-xs text-[#59625D] font-sans mt-0.5">
          Centrally configure category evaluation weights and AI confidence abstention thresholds
        </p>
      </div>

      {message && (
        <div className={`p-3 border font-bold ${
          message.startsWith('Error') ? 'bg-[#FBEBEB] text-[#7A1C1C] border-[#F1B5B5]' : 'bg-[#E8F3EE] text-[#114B3A] border-[#B4DACB]'
        }`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        
        {/* Scoring Weights Box */}
        <div className="border border-[#D8DCD6] bg-white p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#D8DCD6]">
            <h3 className="text-xs font-bold text-[#17201C] uppercase tracking-wider">
              COMPLIANCE CATEGORY SCORING WEIGHTS (TOTAL: {(totalWeight * 100).toFixed(0)}%)
            </h3>
            <span className={`px-2 py-0.5 border text-[10px] font-bold ${
              Math.abs(totalWeight - 1.0) <= 0.01 ? 'bg-[#E8F3EE] text-[#114B3A] border-[#B4DACB]' : 'bg-[#FBEBEB] text-[#7A1C1C] border-[#F1B5B5]'
            }`}>
              {Math.abs(totalWeight - 1.0) <= 0.01 ? 'VALID 100%' : 'MUST EQUAL 100%'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="block text-[10px] font-bold uppercase text-[#59625D]">
                STATUTORY COMPLIANCE WEIGHT (GST, PAN, UDYAM, DEBARMENT)
              </label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={weights.STATUTORY}
                onChange={(e) => setWeights({ ...weights, STATUTORY: parseFloat(e.target.value) || 0 })}
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-[10px] font-bold uppercase text-[#59625D]">
                FINANCIAL ELIGIBILITY WEIGHT (TURNOVER, NET WORTH)
              </label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={weights.FINANCIAL}
                onChange={(e) => setWeights({ ...weights, FINANCIAL: parseFloat(e.target.value) || 0 })}
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-[10px] font-bold uppercase text-[#59625D]">
                TENDER SPECIFIC CRITERIA (OEM MAF, MAKE IN INDIA %)
              </label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={weights.TENDER_SPECIFIC}
                onChange={(e) => setWeights({ ...weights, TENDER_SPECIFIC: parseFloat(e.target.value) || 0 })}
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-[10px] font-bold uppercase text-[#59625D]">
                DOCUMENTATION & INTEGRITY PACT
              </label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={weights.DOCUMENTATION}
                onChange={(e) => setWeights({ ...weights, DOCUMENTATION: parseFloat(e.target.value) || 0 })}
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-[10px] font-bold uppercase text-[#59625D]">
                OTHER ELIGIBILITY / MSME PREFERENCE
              </label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={weights.OTHER_ELIGIBILITY}
                onChange={(e) => setWeights({ ...weights, OTHER_ELIGIBILITY: parseFloat(e.target.value) || 0 })}
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
            </div>
          </div>
        </div>

        {/* Confidence Gating Box */}
        <div className="border border-[#D8DCD6] bg-white p-6 space-y-4">
          <div className="pb-3 border-b border-[#D8DCD6]">
            <h3 className="text-xs font-bold text-[#17201C] uppercase tracking-wider">
              AI CONFIDENCE GATING & MODEL ABSTENTION POLICY
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="block text-[10px] font-bold uppercase text-[#59625D]">
                AUTOMATIC MATCH THRESHOLD (DEFAULT: 0.90)
              </label>
              <input
                type="number"
                step="0.05"
                min="0.5"
                max="1.0"
                value={confidenceHigh}
                onChange={(e) => setConfidenceHigh(parseFloat(e.target.value) || 0.9)}
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
              <span className="text-[10px] text-[#808B84] block">Inferences $\ge$ this threshold qualify for automatic PASS rule match.</span>
            </div>

            <div className="space-y-1">
              <label className="block text-[10px] font-bold uppercase text-[#59625D]">
                DISCRETIONARY REVIEW THRESHOLD (DEFAULT: 0.70)
              </label>
              <input
                type="number"
                step="0.05"
                min="0.4"
                max="0.9"
                value={confidenceMedium}
                onChange={(e) => setConfidenceMedium(parseFloat(e.target.value) || 0.7)}
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
              <span className="text-[10px] text-[#808B84] block">Inferences below this threshold enter the mandatory Officer Review Queue.</span>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-[#163C32] hover:bg-[#0E2922] text-white text-xs font-bold uppercase disabled:opacity-50"
          >
            {saving ? "SAVING..." : "COMMIT SYSTEM PARAMETERS"}
          </button>
        </div>

      </form>

    </div>
  );
};
