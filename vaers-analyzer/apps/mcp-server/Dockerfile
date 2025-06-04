FROM node:18-alpine AS base

# Install pnpm and enable corepack for better package manager handling
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy package manager files first for better caching
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./

# Copy only package.json files from all packages for dependency installation
COPY apps/mcp-server/package.json ./apps/mcp-server/package.json
COPY packages/types/package.json ./packages/types/package.json
COPY packages/database/package.json ./packages/database/package.json
COPY packages/mcp-tools/package.json ./packages/mcp-tools/package.json
COPY packages/analyzer/package.json ./packages/analyzer/package.json
COPY packages/ui/package.json ./packages/ui/package.json
COPY packages/eslint-config/package.json ./packages/eslint-config/package.json
COPY packages/typescript-config/ ./packages/typescript-config/

# Install dependencies with optimizations
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prefer-offline

# Copy TypeScript configs first
COPY packages/types/tsconfig.json ./packages/types/tsconfig.json
COPY packages/database/tsconfig.json ./packages/database/tsconfig.json
COPY packages/mcp-tools/tsconfig.json ./packages/mcp-tools/tsconfig.json
COPY apps/mcp-server/tsconfig.json ./apps/mcp-server/tsconfig.json

# Copy source code
COPY packages/types/src/ ./packages/types/src/
COPY packages/database/src/ ./packages/database/src/
COPY packages/database/drizzle.config.ts ./packages/database/drizzle.config.ts
COPY packages/mcp-tools/src/ ./packages/mcp-tools/src/
COPY apps/mcp-server/src/ ./apps/mcp-server/src/

# Build packages in dependency order
RUN pnpm --filter @vaers/types build && \
    pnpm --filter @vaers/database build && \
    pnpm --filter @vaers/mcp-tools build && \
    pnpm --filter @vaers/mcp-server build

# Production stage
FROM node:18-alpine AS production

# Install pnpm with corepack
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files for production dependencies
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/mcp-server/package.json ./apps/mcp-server/package.json
COPY packages/types/package.json ./packages/types/package.json
COPY packages/database/package.json ./packages/database/package.json
COPY packages/mcp-tools/package.json ./packages/mcp-tools/package.json

# Install production dependencies with cache mount
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prod --prefer-offline

# Copy built applications and packages
COPY --from=base /app/apps/mcp-server/dist ./apps/mcp-server/dist
COPY --from=base /app/packages/types/dist ./packages/types/dist
COPY --from=base /app/packages/database/dist ./packages/database/dist
COPY --from=base /app/packages/mcp-tools/dist ./packages/mcp-tools/dist

# Add non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Change ownership and switch to non-root user
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3001

# Start the application
CMD ["pnpm", "--filter", "@vaers/mcp-server", "start"]