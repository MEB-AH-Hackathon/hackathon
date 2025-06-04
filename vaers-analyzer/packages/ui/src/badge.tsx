"use client";

import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "./utils";

const badgeVariants = cva(
  "inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold",
  {
    variants: {
      variant: {
        default: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
        secondary: "bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-gray-100",
        destructive: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
        outline: "text-foreground border border-gray-300 dark:border-gray-600",
        success: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
        warning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
        info: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
        // Medical outcome specific variants
        death: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
        lifeThreat: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
        hospital: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
        emergency: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
        disability: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };