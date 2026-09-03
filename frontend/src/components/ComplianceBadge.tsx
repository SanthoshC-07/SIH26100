import React from 'react';
import { ComplianceStatus } from '../types';

interface ComplianceBadgeProps {
  status: ComplianceStatus | string;
  size?: 'sm' | 'md' | 'lg';
}

export const ComplianceBadge: React.FC<ComplianceBadgeProps> = ({ status, size = 'sm' }) => {
  const normStatus = (status || 'NOT_APPLICABLE').toUpperCase();

  const getStyle = () => {
    switch (normStatus) {
      case 'PASS':
        return 'bg-[#E8F3EE] text-[#114B3A] border-[#B4DACB]';
      case 'FAIL':
        return 'bg-[#FBEBEB] text-[#7A1C1C] border-[#F1B5B5]';
      case 'REVIEW':
        return 'bg-[#FDF5E6] text-[#875200] border-[#F6D59B]';
      default:
        return 'bg-[#ECEFEA] text-[#4E5853] border-[#D0D6CF]';
    }
  };

  const getSizeStyle = () => {
    switch (size) {
      case 'lg':
        return 'px-3 py-1 text-xs font-semibold tracking-wider';
      case 'md':
        return 'px-2.5 py-0.5 text-[11px] font-semibold tracking-wide';
      case 'sm':
      default:
        return 'px-2 py-0.5 text-[10px] font-semibold tracking-wide';
    }
  };

  const getLabel = () => {
    switch (normStatus) {
      case 'PASS':
        return 'PASS';
      case 'FAIL':
        return 'FAIL';
      case 'REVIEW':
        return 'REVIEW';
      case 'NOT_APPLICABLE':
        return 'NOT APPLICABLE';
      default:
        return normStatus;
    }
  };

  return (
    <span
      className={`inline-flex items-center justify-center border font-mono uppercase ${getStyle()} ${getSizeStyle()}`}
    >
      {getLabel()}
    </span>
  );
};
