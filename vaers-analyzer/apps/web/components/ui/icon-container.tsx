import { ReactNode } from 'react';

interface IconContainerProps {
  icon: ReactNode;
  variant?: 'default' | 'blue' | 'green' | 'amber' | 'red' | 'muted';
  size?: 'default' | 'lg';
  className?: string;
}

export function IconContainer({ 
  icon, 
  variant = 'default', 
  size = 'default', 
  className = '' 
}: IconContainerProps) {
  const variantClasses = {
    default: 'bg-stone-100 dark:bg-stone-700 text-stone-600 dark:text-stone-300',
    blue: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    green: 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-300',
    amber: 'bg-amber-100 dark:bg-amber-900 text-amber-600 dark:text-amber-300',
    red: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300',
    muted: 'bg-stone-50 dark:bg-stone-800 text-stone-400 dark:text-stone-500'
  };

  const sizeClasses = {
    default: 'w-10 h-10',
    lg: 'w-16 h-16'
  };

  return (
    <div className={`${sizeClasses[size]} ${variantClasses[variant]} rounded-xl flex items-center justify-center ${className}`}>
      <div className={size === 'lg' ? 'w-8 h-8' : 'w-5 h-5'}>
        {icon}
      </div>
    </div>
  );
}