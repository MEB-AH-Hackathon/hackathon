"use client";

import React from "react";
import { cn } from "./utils";

interface PageLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function PageLayout({ children, className }: PageLayoutProps) {
  return (
    <div className={cn(
      "min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-50 dark:from-stone-900 dark:via-stone-800 dark:to-stone-900",
      className
    )}>
      {children}
    </div>
  );
}

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
  size?: "default" | "wide" | "narrow";
}

export function PageContainer({ children, className, size = "default" }: PageContainerProps) {
  const sizeClasses = {
    default: "max-w-6xl",
    wide: "max-w-7xl", 
    narrow: "max-w-4xl"
  };

  return (
    <div className={cn(
      sizeClasses[size],
      "mx-auto px-4 py-12 sm:px-6 lg:px-8",
      className
    )}>
      {children}
    </div>
  );
}

interface SectionProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "muted";
}

export function Section({ children, className, variant = "default" }: SectionProps) {
  const variantClasses = {
    default: "bg-white/60 dark:bg-stone-800/40",
    muted: "bg-stone-50/50 dark:bg-stone-800/30"
  };

  return (
    <div className={cn(
      variantClasses[variant],
      "rounded-2xl border border-stone-200/50 dark:border-stone-700/50",
      className
    )}>
      {children}
    </div>
  );
}