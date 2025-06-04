"use client";

import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "./utils";

const iconContainerVariants = cva(
  "flex items-center justify-center rounded-2xl shadow-sm",
  {
    variants: {
      variant: {
        default: "bg-slate-600 dark:bg-slate-400",
        blue: "bg-blue-600 dark:bg-blue-400", 
        green: "bg-green-600 dark:bg-green-400",
        amber: "bg-amber-600 dark:bg-amber-400",
        red: "bg-red-600 dark:bg-red-400",
        muted: "bg-stone-200 dark:bg-stone-600"
      },
      size: {
        sm: "w-10 h-10",
        default: "w-12 h-12", 
        lg: "w-16 h-16",
        xl: "w-20 h-20"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
);

export interface IconContainerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof iconContainerVariants> {
  icon: React.ReactNode;
}

const IconContainer = React.forwardRef<HTMLDivElement, IconContainerProps>(
  ({ className, variant, size, icon, ...props }, ref) => {
    const iconSizeClasses = {
      sm: "w-5 h-5",
      default: "w-6 h-6",
      lg: "w-8 h-8", 
      xl: "w-10 h-10"
    };

    const iconColorClasses = {
      default: "text-white dark:text-slate-800",
      blue: "text-white dark:text-blue-900",
      green: "text-white dark:text-green-900", 
      amber: "text-white dark:text-amber-900",
      red: "text-white dark:text-red-900",
      muted: "text-stone-600 dark:text-stone-300"
    };

    return (
      <div
        ref={ref}
        className={cn(iconContainerVariants({ variant, size }), className)}
        {...props}
      >
        <div className={cn(iconSizeClasses[size || "default"], iconColorClasses[variant || "default"])}>
          {icon}
        </div>
      </div>
    );
  }
);

IconContainer.displayName = "IconContainer";

export { IconContainer, iconContainerVariants };