import { ReactNode } from 'react';
import { IconContainer } from './icon-container';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  description?: string;
  icon?: ReactNode;
  iconVariant?: 'default' | 'blue' | 'green' | 'amber' | 'red' | 'muted';
  actions?: ReactNode;
}

export function PageHeader({ 
  title, 
  subtitle, 
  description, 
  icon, 
  iconVariant = 'default',
  actions 
}: PageHeaderProps) {
  return (
    <div className="text-center mb-12">
      {icon && (
        <div className="mb-6 flex justify-center">
          <IconContainer variant={iconVariant} size="lg" icon={icon} />
        </div>
      )}
      <h1 className="text-4xl font-semibold tracking-tight text-stone-900 dark:text-stone-100 mb-4">
        {title}
      </h1>
      {subtitle && (
        <p className="text-lg text-stone-600 dark:text-stone-400 mb-4">
          {subtitle}
        </p>
      )}
      {description && (
        <p className="text-stone-600 dark:text-stone-400 max-w-3xl mx-auto mb-6">
          {description}
        </p>
      )}
      {actions && (
        <div className="flex justify-center">
          {actions}
        </div>
      )}
    </div>
  );
}