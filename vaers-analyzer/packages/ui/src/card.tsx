"use client";

import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "./utils";

const cardVariants = cva(
  "rounded-2xl border border-stone-200/50 dark:border-stone-700/50 transition-all duration-300",
  {
    variants: {
      variant: {
        default: "bg-white/60 dark:bg-stone-800/40",
        elevated: "bg-white/80 dark:bg-stone-800/80 backdrop-blur-sm shadow-sm hover:shadow-lg",
        interactive: "bg-white/80 dark:bg-stone-800/80 backdrop-blur-sm shadow-sm hover:shadow-lg border-stone-200/60 dark:border-stone-700/60 hover:border-stone-300 dark:hover:border-stone-600 group cursor-pointer",
        muted: "bg-stone-50/50 dark:bg-stone-800/30"
      },
      size: {
        default: "p-6",
        large: "p-8",
        xlarge: "p-10"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  hoverOverlay?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, size, hoverOverlay, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, size }), "relative", className)}
      {...props}
    >
      {hoverOverlay && variant === "interactive" && (
        <div className="absolute inset-0 bg-gradient-to-br from-stone-100/20 to-stone-200/20 dark:from-stone-700/20 dark:to-stone-600/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      )}
      <div className={variant === "interactive" ? "relative" : undefined}>
        {children}
      </div>
    </div>
  )
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 mb-6", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight text-stone-900 dark:text-stone-100",
      className
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-stone-600 dark:text-stone-400 leading-relaxed", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center mt-6", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent, cardVariants };
