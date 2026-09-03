import React from 'react';
import { RiskLevel } from '../types';

interface RiskBadgeProps {
  level: RiskLevel | string;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'sm' }) => {
  const normLevel = (level || 'MEDIUM').toUpperCase();

  const getStyle = () => {
    switch (normLevel) {
      case 'LOW':
        return 'bg-[#E8F3EE] text-[#114B3A] border-[#B4DACB]';
      case 'MEDIUM':
        return 'bg-[#FDF5E6] text-[#875200] border-[#F6D59B]';
      case 'HIGH':
        return 'bg-[#FBEBEB] text-[#7A1C1C] border-[#F1B5B5]';
      case 'CRITICAL':
        return 'bg-[#5C1111] text-[#FFFFFF] border-[#3D0B0B]';
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

  return (
    <span
      className={`inline-flex items-center justify-center border font-mono uppercase ${getStyle()} ${getSizeStyle()}`}
    >
      {normLevel} RISK
    </span>
  );
};
