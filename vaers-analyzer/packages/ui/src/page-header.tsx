"use client";

import React from "react";
import { cn } from "./utils";
import { IconContainer } from "./icon-container";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  description?: string;
  icon?: React.ReactNode;
  iconVariant?: "default" | "blue" | "green" | "amber" | "red" | "muted";
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({ 
  title, 
  subtitle, 
  description, 
  icon, 
  iconVariant = "default", 
  actions, 
  className 
}: PageHeaderProps) {
  return (
    <div className={cn("mb-12", className)}>
      <div className="sm:flex sm:items-end sm:justify-between">
        <div className="mb-6 sm:mb-0">
          <div className="flex items-center space-x-3 mb-4">
            {icon && (
              <IconContainer 
                variant={iconVariant}
                size="lg"
                icon={icon}
              />
            )}
            <div>
              <h1 className="text-4xl font-semibold text-stone-900 dark:text-stone-100">
                {title}
              </h1>
              {subtitle && (
                <div className="flex items-center space-x-2 mt-1">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                  <p className="text-stone-600 dark:text-stone-400">
                    {subtitle}
                  </p>
                </div>
              )}
            </div>
          </div>
          {description && (
            <p className="text-lg text-stone-600 dark:text-stone-400 max-w-2xl">
              {description}
            </p>
          )}
        </div>
        {actions && (
          <div className="flex-shrink-0">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}