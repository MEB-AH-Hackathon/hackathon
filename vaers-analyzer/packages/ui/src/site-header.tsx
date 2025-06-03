"use client";

import Link from "next/link";
import React from "react";
import { usePathname } from "next/navigation";
import { cn } from "./utils";

interface SiteHeaderProps {
  className?: string;
}

export function SiteHeader({ className }: SiteHeaderProps) {
  const pathname = usePathname();
  const isHomePage = pathname === "/";

  if (isHomePage) {
    return null;
  }

  return (
    <header
      className={cn(
        "border-b bg-white/80 dark:bg-stone-900/80 backdrop-blur",
        className
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between px-4 sm:px-6 lg:px-8 py-4">
        <Link href="/" className="font-semibold text-stone-800 dark:text-stone-100 hover:text-stone-600 dark:hover:text-stone-300 transition-colors">
          VAERS Analyzer
        </Link>
        <nav className="flex items-center space-x-8">
          <Link 
            href="/" 
            className={cn(
              "px-3 py-2 rounded-lg font-medium transition-all duration-200",
              pathname === "/" 
                ? "bg-stone-100 dark:bg-stone-800 text-stone-900 dark:text-stone-100"
                : "text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100 hover:bg-stone-50 dark:hover:bg-stone-800/50"
            )}
          >
            Home
          </Link>
          <Link 
            href="/reports" 
            className={cn(
              "px-3 py-2 rounded-lg font-medium transition-all duration-200",
              pathname.startsWith("/reports") 
                ? "bg-stone-100 dark:bg-stone-800 text-stone-900 dark:text-stone-100"
                : "text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100 hover:bg-stone-50 dark:hover:bg-stone-800/50"
            )}
          >
            Reports
          </Link>
        </nav>
      </div>
    </header>
  );
}
