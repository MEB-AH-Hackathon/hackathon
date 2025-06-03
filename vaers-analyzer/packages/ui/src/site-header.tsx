"use client";

import Link from "next/link";
import React from "react";
import { cn } from "./utils";

interface SiteHeaderProps {
  className?: string;
}

export function SiteHeader({ className }: SiteHeaderProps) {
  return (
    <header
      className={cn(
        "border-b bg-white/80 dark:bg-stone-900/80 backdrop-blur",
        className
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between px-4 sm:px-6 lg:px-8 py-4">
        <Link href="/" className="font-semibold text-stone-800 dark:text-stone-100">
          VAERS Analyzer
        </Link>
        <nav className="flex items-center space-x-6 text-sm">
          <Link href="/" className="text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100">
            Home
          </Link>
          <Link href="/reports" className="text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100">
            Reports
          </Link>
        </nav>
      </div>
    </header>
  );
}
