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
      case 'PASSED':
      case 'VERIFIED':
        return 'bg-[#EAF5F0] text-[#237A57] border-[#A8D9C5]';
      case 'FAIL':
      case 'FAILED':
      case 'DISQUALIFIED':
        return 'bg-[#FDF2F2] text-[#B44747] border-[#F7BEBE]';
      case 'REVIEW':
      case 'UNDER_REVIEW':
      case 'UNDER_EVALUATION':
        return 'bg-[#FEF7EC] text-[#B7791F] border-[#F6D8A8]';
      case 'INSUFFICIENT':
        return 'bg-[#FFF9E6] text-[#A66A16] border-[#F4DC96]';
      default:
        return 'bg-[#F5F6F3] text-[#66736D] border-[#D9DEDA]';
    }
  };

  const getSizeStyle = () => {
    switch (size) {
      case 'lg':
        return 'px-3 py-1 text-xs font-bold tracking-wider';
      case 'md':
        return 'px-2.5 py-0.5 text-[11px] font-bold tracking-wide';
      case 'sm':
      default:
        return 'px-2 py-0.5 text-[10px] font-bold tracking-wide';
    }
  };

  const getLabel = () => {
    switch (normStatus) {
      case 'PASS':
      case 'PASSED':
      case 'VERIFIED':
        return 'PASS';
      case 'FAIL':
      case 'FAILED':
      case 'DISQUALIFIED':
        return 'FAIL';
      case 'REVIEW':
      case 'UNDER_REVIEW':
      case 'UNDER_EVALUATION':
        return 'REVIEW';
      case 'INSUFFICIENT':
        return 'INSUFFICIENT';
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
