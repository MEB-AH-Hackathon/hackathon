import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  variant?: 'default' | 'muted' | 'elevated' | 'interactive';
  size?: 'default' | 'large' | 'xlarge';
  className?: string;
  hoverOverlay?: boolean;
}

export function Card({ 
  children, 
  variant = 'default', 
  size = 'default', 
  className = '',
  hoverOverlay = false 
}: CardProps) {
  const variantClasses = {
    default: 'bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700',
    muted: 'bg-stone-100 dark:bg-stone-800 border border-stone-200 dark:border-stone-700',
    elevated: 'bg-white dark:bg-stone-800 shadow-lg border border-stone-200 dark:border-stone-700',
    interactive: 'bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 hover:shadow-lg transition-shadow duration-200 cursor-pointer'
  };

  const sizeClasses = {
    default: 'p-6',
    large: 'p-8', 
    xlarge: 'p-12'
  };

  const hoverClasses = hoverOverlay ? 'group relative overflow-hidden' : '';

  return (
    <div className={`rounded-xl ${variantClasses[variant]} ${sizeClasses[size]} ${hoverClasses} ${className}`}>
      {hoverOverlay && (
        <div className="absolute inset-0 bg-gradient-to-r from-stone-50 to-transparent dark:from-stone-700 dark:to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
      )}
      <div className="relative">
        {children}
      </div>
    </div>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return <div className={className}>{children}</div>;
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export function CardTitle({ children, className = '' }: CardTitleProps) {
  return (
    <h3 className={`text-xl font-semibold text-stone-900 dark:text-stone-100 ${className}`}>
      {children}
    </h3>
  );
}

interface CardDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function CardDescription({ children, className = '' }: CardDescriptionProps) {
  return (
    <p className={`text-stone-600 dark:text-stone-400 ${className}`}>
      {children}
    </p>
  );
}

interface CardFooterProps {
  children: ReactNode;
  className?: string;
}

export function CardFooter({ children, className = '' }: CardFooterProps) {
  return <div className={className}>{children}</div>;
}