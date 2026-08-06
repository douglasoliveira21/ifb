# =============================================================================
# Dockerfile — IFB Frontend (Next.js)
# Multi-stage build para imagem otimizada com standalone output
# =============================================================================

# --- Stage 1: Dependencies ---
FROM node:20-alpine AS deps

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# --- Stage 2: Builder ---
FROM node:20-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# --- Stage 3: Runner ---
FROM node:20-alpine AS runner

LABEL maintainer="IFB Team"
LABEL description="Instituto Fiscaliza Brasil - Frontend"

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 ifb && \
    adduser --system --uid 1001 ifb

COPY --from=builder /app/public ./public
COPY --from=builder --chown=ifb:ifb /app/.next/standalone ./
COPY --from=builder --chown=ifb:ifb /app/.next/static ./.next/static

USER ifb

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
