import { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'death' | 'lifeThreat' | 'hospital' | 'emergency' | 'disability';
  className?: string;
}

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  const variantClasses = {
    default: 'bg-stone-100 text-stone-800 dark:bg-stone-700 dark:text-stone-200',
    death: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    lifeThreat: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    hospital: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    emergency: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    disability: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
}