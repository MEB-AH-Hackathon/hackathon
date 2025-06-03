#!/bin/bash

echo "=== Build Debug Script ==="
echo "Current directory: $(pwd)"
echo "NODE_ENV: $NODE_ENV"
echo "VERCEL: $VERCEL"
echo "VERCEL_ENV: $VERCEL_ENV"
echo ""

echo "=== Directory Structure Before Build ==="
find . -type d -name "node_modules" -prune -o -type d -print | grep -E "(apps|packages)" | head -20
echo ""

echo "=== Running pnpm build:prod ==="
pnpm build:prod

echo ""
echo "=== Directory Structure After Build ==="
find . -type d -name ".next" -o -name "dist" -o -name "build" | grep -v node_modules
echo ""

echo "=== Contents of apps/web/.next (if exists) ==="
if [ -d "apps/web/.next" ]; then
  ls -la apps/web/.next/
else
  echo "Directory apps/web/.next does not exist!"
fi
echo ""

echo "=== Checking for build output in other locations ==="
find . -name ".next" -type d | grep -v node_modules