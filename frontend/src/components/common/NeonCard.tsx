import React from 'react';

interface NeonCardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  as?: React.ElementType;
  animated?: boolean; // New prop for motion control
}

const NeonCard: React.FC<NeonCardProps> = ({
  children,
  className = '',
  onClick,
  as: Component = 'div',
  animated = false,
}) => {
  const baseClasses = `
    relative p-6 rounded-lg overflow-hidden
    bg-bg-secondary/80 backdrop-blur-cyber
    border border-border
    motion-safe:transition-transform motion-safe:duration-200
    motion-safe:hover:-translate-y-px
    [box-shadow:var(--shadow-card)]
    hover:[box-shadow:var(--shadow-card-hover)]
    focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-bg-primary
  `;

  return (
    <Component
      className={`${baseClasses} ${className}`}
      onClick={onClick}
      {...(Component === 'button' ? { type: 'button' } : {})}
    >
      {animated && (
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-r from-primary/20 to-secondary/20 motion-safe:animate-spin-slow" />
      )}
      <div className="relative z-10">
        {children}
      </div>
    </Component>
  );
};

export default NeonCard;