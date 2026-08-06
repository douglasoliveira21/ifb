# =============================================================================
# Dockerfile — IFB Frontend (Next.js)
# =============================================================================

# --- Stage 1: Dependencies ---
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

# --- Stage 2: Builder ---
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build args viram env vars para o Next.js substituir NEXT_PUBLIC_*
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# --- Stage 3: Runner ---
FROM node:20-alpine AS runner
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

CMD ["node", "server.js"]
