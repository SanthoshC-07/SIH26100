import React, { useState } from 'react';
import {
  Sliders,
  ShieldCheck,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Info,
  Layers,
  Settings,
  Flame,
  Check,
  Plus
} from 'lucide-react';

interface EngineRuleItem {
  id: string;
  name: string;
  description: string;
  status: 'ACTIVE' | 'PAUSED';
  category: string;
}

export const EngineRulesPage: React.FC = () => {
  // Rules from PDF Page 8
  const [rules, setRules] = useState<EngineRuleItem[]>([
    {
      id: 'rule-1',
      name: 'Duplicate Bid Detection',
      description: 'Flags bidders submitting more than one proposal per tender.',
      status: 'ACTIVE',
      category: 'Integrity'
    },
    {
      id: 'rule-2',
      name: 'Registration Expiry Check',
      description: 'Blocks selection if vendor registration has lapsed.',
      status: 'ACTIVE',
      category: 'Statutory'
    },
    {
      id: 'rule-3',
      name: 'Minimum Document Set',
      description: 'Requires financial statement + company license before file can be selected.',
      status: 'ACTIVE',
      category: 'Prerequisite'
    },
    {
      id: 'rule-4',
      name: 'Price Variance Alert',
      description: 'Flags bids more than 30% below the estimated tender value.',
      status: 'PAUSED',
      category: 'Financial'
    },
    {
      id: 'rule-5',
      name: 'Blacklist Screening',
      description: 'Cross-checks bidder against the debarred vendor list.',
      status: 'ACTIVE',
      category: 'Compliance'
    }
  ]);

  // Quantitative Thresholds (preserves existing backend/ML engine capabilities)
  const [minTurnover, setMinTurnover] = useState<number>(25);
  const [minPipelineLength, setMinPipelineLength] = useState<number>(100);
  const [minPipelineDiameter, setMinPipelineDiameter] = useState<number>(24);
  const [minOilGasExperience, setMinOilGasExperience] = useState<number>(7);
  const [minEngineersCount, setMinEngineersCount] = useState<number>(5);
  const [minEngineerExpYears, setMinEngineerExpYears] = useState<number>(8);
  const [confidenceGateThreshold, setConfidenceGateThreshold] = useState<number>(90);
  const [enableOcrFallback, setEnableOcrFallback] = useState<boolean>(true);
  const [gstMatchThreshold, setGstMatchThreshold] = useState<number>(90);

  const [savedSuccess, setSavedSuccess] = useState(false);
  const [showNewRuleModal, setShowNewRuleModal] = useState(false);
  const [newRuleName, setNewRuleName] = useState('');
  const [newRuleDesc, setNewRuleDesc] = useState('');

  const toggleRuleStatus = (id: string) => {
    setRules(prev => prev.map(r => {
      if (r.id === id) {
        return {
          ...r,
          status: r.status === 'ACTIVE' ? 'PAUSED' : 'ACTIVE'
        };
      }
      return r;
    }));
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 4000);
  };

  const handleReset = () => {
    setMinTurnover(25);
    setMinPipelineLength(100);
    setMinPipelineDiameter(24);
    setMinOilGasExperience(7);
    setMinEngineersCount(5);
    setMinEngineerExpYears(8);
    setConfidenceGateThreshold(90);
    setEnableOcrFallback(true);
    setGstMatchThreshold(90);
  };

  const handleAddRule = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRuleName.trim()) return;
    const newRule: EngineRuleItem = {
      id: 'rule-' + (rules.length + 1),
      name: newRuleName.trim(),
      description: newRuleDesc.trim() || 'Custom automated compliance rule for pipeline tenders.',
      status: 'ACTIVE',
      category: 'Custom'
    };
    setRules([...rules, newRule]);
    setNewRuleName('');
    setNewRuleDesc('');
    setShowNewRuleModal(false);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 font-sans">
      
      {/* ── Top Header Section (from PDF Page 8) ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#66717C] uppercase font-bold">
            ENGINE RULES
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#10283A] tracking-tight mt-0.5">
            Engine Rules
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowNewRuleModal(true)}
            className="px-5 py-2.5 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded-md transition-colors shadow-sm inline-flex items-center gap-1.5"
            title="Create New Compliance Rule"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>+ New Rule</span>
          </button>

          <button
            type="button"
            onClick={handleReset}
            className="p-2.5 bg-[#FFFFFF] hover:bg-[#F4F5F7] border border-[#D9DEE3] text-[#66717C] hover:text-[#10283A] rounded-md transition-colors shadow-sm"
            title="Reset Default Thresholds"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {savedSuccess && (
        <div className="p-3.5 bg-[#EAF5F0] border border-[#A8D9C5] text-[#198754] text-xs font-semibold rounded-md flex items-center gap-2">
          <Check className="w-4 h-4" />
          <span>Compliance engine rules and thresholds successfully synchronized with active evaluation pipeline.</span>
        </div>
      )}

      {/* ── Section: Compliance Rule Engine (from PDF Page 8) ── */}
      <div className="space-y-3">
        <h2 className="text-base font-serif font-bold text-[#10283A]">
          Compliance Rule Engine
        </h2>

        {/* Stack of Clean White Bordered Cards (from PDF Page 8) */}
        <div className="space-y-3">
          {rules.map((rule) => {
            const isActive = rule.status === 'ACTIVE';
            return (
              <div
                key={rule.id}
                className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-5 shadow-sm flex items-center justify-between gap-4 transition-all hover:border-[#10283A]/40"
              >
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold text-[#17212B]">
                    {rule.name}
                  </div>
                  <div className="text-xs text-[#66717C] mt-1 leading-relaxed">
                    {rule.description}
                  </div>
                </div>

                {/* Pill Button (ACTIVE = Green #198754, PAUSED = Gray #B0B8C1) */}
                <button
                  onClick={() => toggleRuleStatus(rule.id)}
                  className={`px-5 py-2 rounded-full text-xs font-bold tracking-wider uppercase transition-all shrink-0 cursor-pointer ${
                    isActive
                      ? 'bg-[#198754] text-white hover:bg-[#157347] shadow-sm'
                      : 'bg-[#B0B8C1] text-white hover:bg-[#9EA7B1]'
                  }`}
                  title={`Click to ${isActive ? 'Pause' : 'Activate'} Rule`}
                >
                  {rule.status}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Section 2: Quantitative Thresholds & NLP Confidence Gates ── */}
      <div className="pt-4 space-y-4">
        <h2 className="text-base font-serif font-bold text-[#10283A]">
          Quantitative Thresholds &amp; NLP Model Configuration
        </h2>

        <form onSubmit={handleSave} className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-6 shadow-sm space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
              
              {/* Turnover Rule */}
              <div className="space-y-2 bg-[#F9FAFB] p-4 border border-[#D9DEE3] rounded-md">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-[#17212B] uppercase text-[11px]">
                    Turnover Threshold
                  </label>
                  <span className="font-mono font-bold text-[#10283A]">₹{minTurnover} Cr</span>
                </div>
                <p className="text-[11px] text-[#66717C]">
                  3-year average annual audited turnover for EPC bidders.
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="number"
                    min="5"
                    max="500"
                    value={minTurnover}
                    onChange={(e) => setMinTurnover(Number(e.target.value))}
                    className="w-full px-3 py-1.5 bg-white border border-[#D9DEE3] rounded text-xs font-mono font-bold text-[#17212B] focus:outline-none focus:border-[#10283A]"
                  />
                  <span className="font-mono text-xs text-[#66717C] font-semibold">Cr</span>
                </div>
              </div>

              {/* Pipeline Length */}
              <div className="space-y-2 bg-[#F9FAFB] p-4 border border-[#D9DEE3] rounded-md">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-[#17212B] uppercase text-[11px]">
                    Pipeline Length
                  </label>
                  <span className="font-mono font-bold text-[#10283A]">{minPipelineLength} KM</span>
                </div>
                <p className="text-[11px] text-[#66717C]">
                  Minimum cross-country transmission pipeline constructed.
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="number"
                    min="10"
                    max="1000"
                    value={minPipelineLength}
                    onChange={(e) => setMinPipelineLength(Number(e.target.value))}
                    className="w-full px-3 py-1.5 bg-white border border-[#D9DEE3] rounded text-xs font-mono font-bold text-[#17212B] focus:outline-none focus:border-[#10283A]"
                  />
                  <span className="font-mono text-xs text-[#66717C] font-semibold">KM</span>
                </div>
              </div>

              {/* Pipeline Diameter */}
              <div className="space-y-2 bg-[#F9FAFB] p-4 border border-[#D9DEE3] rounded-md">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-[#17212B] uppercase text-[11px]">
                    Pipe Outside Diameter
                  </label>
                  <span className="font-mono font-bold text-[#10283A]">{minPipelineDiameter}"</span>
                </div>
                <p className="text-[11px] text-[#66717C]">
                  Nominal bore diameter requirement for gas transmission line.
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="number"
                    min="6"
                    max="48"
                    value={minPipelineDiameter}
                    onChange={(e) => setMinPipelineDiameter(Number(e.target.value))}
                    className="w-full px-3 py-1.5 bg-white border border-[#D9DEE3] rounded text-xs font-mono font-bold text-[#17212B] focus:outline-none focus:border-[#10283A]"
                  />
                  <span className="font-mono text-xs text-[#66717C] font-semibold">Inch</span>
                </div>
              </div>

              {/* Oil & Gas Experience */}
              <div className="space-y-2 bg-[#F9FAFB] p-4 border border-[#D9DEE3] rounded-md">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-[#17212B] uppercase text-[11px]">
                    Sector Experience
                  </label>
                  <span className="font-mono font-bold text-[#10283A]">{minOilGasExperience} Yrs</span>
                </div>
                <p className="text-[11px] text-[#66717C]">
                  Minimum track record in petroleum &amp; natural gas sector.
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={minOilGasExperience}
                    onChange={(e) => setMinOilGasExperience(Number(e.target.value))}
                    className="w-full px-3 py-1.5 bg-white border border-[#D9DEE3] rounded text-xs font-mono font-bold text-[#17212B] focus:outline-none focus:border-[#10283A]"
                  />
                  <span className="font-mono text-xs text-[#66717C] font-semibold">Yrs</span>
                </div>
              </div>

              {/* Confidence Gate Threshold */}
              <div className="space-y-2 bg-[#F9FAFB] p-4 border border-[#D9DEE3] rounded-md">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-[#17212B] uppercase text-[11px]">
                    AI Confidence Gate
                  </label>
                  <span className="font-mono font-bold text-[#198754]">{confidenceGateThreshold}%</span>
                </div>
                <p className="text-[11px] text-[#66717C]">
                  Threshold below which checks route to Human-in-the-Loop review.
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="range"
                    min="70"
                    max="99"
                    value={confidenceGateThreshold}
                    onChange={(e) => setConfidenceGateThreshold(Number(e.target.value))}
                    className="w-full accent-[#10283A]"
                  />
                </div>
              </div>

              {/* GST Match Gate */}
              <div className="space-y-2 bg-[#F9FAFB] p-4 border border-[#D9DEE3] rounded-md">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-[#17212B] uppercase text-[11px]">
                    GST Name Fuzzy Match
                  </label>
                  <span className="font-mono font-bold text-[#10283A]">{gstMatchThreshold}%</span>
                </div>
                <p className="text-[11px] text-[#66717C]">
                  Levenshtein distance threshold for GSTIN corporate name match.
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="range"
                    min="75"
                    max="100"
                    value={gstMatchThreshold}
                    onChange={(e) => setGstMatchThreshold(Number(e.target.value))}
                    className="w-full accent-[#10283A]"
                  />
                </div>
              </div>

            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#D9DEE3]">
              <button
                type="submit"
                className="px-6 py-2.5 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded-md transition-colors shadow-sm flex items-center gap-1.5"
              >
                <Save className="w-3.5 h-3.5" />
                <span>Save All Thresholds</span>
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* ── New Rule Modal ── */}
      {showNewRuleModal && (
        <div className="fixed inset-0 bg-[#10283A]/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-[#D9DEE3] rounded-md shadow-lg max-w-lg w-full p-6 space-y-4 font-sans">
            <h3 className="text-base font-serif font-bold text-[#10283A]">
              Create Compliance Engine Rule
            </h3>
            <p className="text-xs text-[#66717C]">
              Define an automated verification rule for tender bid qualification.
            </p>

            <form onSubmit={handleAddRule} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-[#17212B] block mb-1">Rule Name</label>
                <input
                  type="text"
                  value={newRuleName}
                  onChange={(e) => setNewRuleName(e.target.value)}
                  placeholder="e.g., EMD Bank Guarantee Validity Check"
                  required
                  className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div>
                <label className="font-semibold text-[#17212B] block mb-1">Description</label>
                <textarea
                  rows={3}
                  value={newRuleDesc}
                  onChange={(e) => setNewRuleDesc(e.target.value)}
                  placeholder="Specify verification behavior and flag condition..."
                  required
                  className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewRuleModal(false)}
                  className="px-4 py-2 border border-[#D9DEE3] text-[#66717C] hover:text-[#17212B] rounded text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-[#10283A] text-white hover:bg-[#18374D] rounded text-xs font-semibold shadow-sm"
                >
                  Add Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default EngineRulesPage;
