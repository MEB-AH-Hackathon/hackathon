import { ReactNode } from 'react';

interface PageLayoutProps {
  children: ReactNode;
}

export function PageLayout({ children }: PageLayoutProps) {
  return (
    <div className="min-h-screen bg-stone-50 dark:bg-stone-900">
      {children}
    </div>
  );
}

interface PageContainerProps {
  children: ReactNode;
  size?: 'default' | 'wide' | 'narrow';
  className?: string;
}

export function PageContainer({ children, size = 'default', className = '' }: PageContainerProps) {
  const sizeClasses = {
    default: 'max-w-4xl',
    wide: 'max-w-7xl', 
    narrow: 'max-w-2xl'
  };

  return (
    <div className={`${sizeClasses[size]} mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
}