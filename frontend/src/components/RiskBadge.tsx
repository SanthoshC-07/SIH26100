import React from 'react';
import { RiskLevel } from '../types';

interface RiskBadgeProps {
  level: RiskLevel | string;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'sm' }) => {
  const normLevel = (level || 'LOW').toUpperCase();

  const getStyle = () => {
    switch (normLevel) {
      case 'LOW':
        return 'bg-[#EAF5F0] text-[#237A57] border-[#A8D9C5]';
      case 'MEDIUM':
        return 'bg-[#FEF7EC] text-[#B7791F] border-[#F6D8A8]';
      case 'HIGH':
        return 'bg-[#FDF2F2] text-[#B44747] border-[#F7BEBE]';
      case 'CRITICAL':
        return 'bg-[#5C1111] text-[#FFFFFF] border-[#3D0B0B]';
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

  return (
    <span
      className={`inline-flex items-center justify-center border font-mono uppercase ${getStyle()} ${getSizeStyle()}`}
    >
      {normLevel} RISK
    </span>
  );
};
