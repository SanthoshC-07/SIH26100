import React, { useEffect, useState } from 'react';
import { auditService } from '../services';
import { AuditLog } from '../types';

export const AuditTrailPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [actionFilter, setActionFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await auditService.getAuditLogs({ action: actionFilter || undefined, limit: 100 });
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="border border-[#D8DCD6] bg-white p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 font-mono">
        <div>
          <div className="text-[10px] uppercase tracking-widest text-[#A7833B] font-bold">
            STATUTORY COMPLIANCE & LEGAL TELEMETRY
          </div>
          <h1 className="text-base font-bold tracking-tight text-[#17201C] mt-0.5 uppercase">
            IMMUTABLE AUDIT TRAIL LOGS
          </h1>
          <p className="text-xs text-[#59625D] font-sans mt-0.5">
            Tamper-evident legal audit log of all automated inferences, portal validations, and officer overrides
          </p>
        </div>
        <div className="px-3 py-1 bg-[#E8F3EE] border border-[#B4DACB] text-[#114B3A] text-xs font-bold">
          SECTION 4 GFR COMPLIANT
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="border border-[#D8DCD6] bg-white p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 font-mono text-xs">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold text-[#59625D] uppercase">FILTER ACTION:</span>
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="border border-[#D8DCD6] p-1.5 px-2 bg-white text-[#17201C] outline-none text-xs"
          >
            <option value="">ALL ACTIONS</option>
            <option value="BIDDER_VERIFIED">BIDDER VERIFIED</option>
            <option value="OFFICER_OVERRIDE">OFFICER OVERRIDE</option>
            <option value="OFFICER_ACCEPT">OFFICER ACCEPT</option>
            <option value="DOCUMENT_UPLOADED">DOCUMENT UPLOADED</option>
            <option value="TENDER_CREATED">TENDER CREATED</option>
          </select>
        </div>

        <button
          onClick={fetchLogs}
          className="px-3 py-1.5 border border-[#D8DCD6] bg-white hover:bg-[#EDEFEA] text-[#17201C] font-bold text-[11px]"
        >
          REFRESH AUDIT LOGS
        </button>
      </div>

      {/* Audit Log Table */}
      <div className="border border-[#D8DCD6] bg-white">
        {loading ? (
          <div className="p-12 text-center text-[#59625D] font-mono text-xs">
            RETRIEVING REGULATED AUDIT TRAIL...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-[#D8DCD6] bg-[#EDEFEA] text-[#59625D] text-[10px] uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">TIMESTAMP (UTC)</th>
                  <th className="px-5 py-3">OFFICER / ACTOR</th>
                  <th className="px-5 py-3">ACTION</th>
                  <th className="px-5 py-3">TARGET ENTITY</th>
                  <th className="px-5 py-3">STATE TRANSITION & REASON</th>
                  <th className="px-5 py-3">VERSION METRICS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#D8DCD6] text-[#17201C]">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[#F4F5F2] transition-colors">
                    <td className="px-5 py-3.5 text-[11px] text-[#59625D] whitespace-nowrap">
                      {new Date(log.timestamp).toUTCString()}
                    </td>
                    <td className="px-5 py-3.5 font-bold whitespace-nowrap">
                      <div>{log.user_name}</div>
                      <div className="text-[10px] text-[#808B84] font-normal">IP: {log.ip_address}</div>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className={`inline-block px-2 py-0.5 border text-[10px] font-bold ${
                        log.action.includes('OVERRIDE') ? 'bg-[#FDF5E6] text-[#875200] border-[#F6D59B]' :
                        (log.action.includes('VERIFIED') ? 'bg-[#E8F3EE] text-[#114B3A] border-[#B4DACB]' : 'bg-[#ECEFEA] text-[#4E5853] border-[#D0D6CF]')
                      }`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <div className="font-bold">{log.entity_type}</div>
                      <div className="text-[10px] text-[#808B84]">{log.entity_id.slice(0, 14)}</div>
                    </td>
                    <td className="px-5 py-3.5 max-w-sm font-sans">
                      <div className="text-xs text-[#17201C] font-medium">{log.reason || "System state recorded."}</div>
                      {log.new_state && (
                        <div className="text-[10px] font-mono text-[#59625D] mt-1 bg-[#FCFCFA] p-1.5 border border-[#D8DCD6]">
                          {JSON.stringify(log.new_state)}
                        </div>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-[10px] text-[#59625D] whitespace-nowrap">
                      <div>{log.model_version}</div>
                      <div className="text-[#808B84]">RULES v{log.rule_version}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};
