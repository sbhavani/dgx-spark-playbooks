# Simple single-stage Dockerfile without caching
FROM node:18-slim
WORKDIR /app

# Set environment variables
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Install pnpm
RUN npm install -g pnpm --force --yes

# Copy dependency files
COPY ./frontend/package.json ./frontend/pnpm-lock.yaml* ./
COPY ./scripts/ /scripts/

# Update the setup-pinecone.js path
RUN sed -i 's|"setup-pinecone": "node ../scripts/setup-pinecone.js"|"setup-pinecone": "node /scripts/setup-pinecone.js"|g' package.json

# Install dependencies without cache
RUN pnpm config set auto-install-peers true && \
    if [ -f pnpm-lock.yaml ]; then \
        pnpm install --no-optional --frozen-lockfile || pnpm install --no-optional --no-frozen-lockfile; \
    else \
        pnpm install --no-optional --no-frozen-lockfile; \
    fi

# Copy source code
COPY ./frontend/ ./

# Build the application
RUN pnpm build

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Set ownership
RUN chown -R nextjs:nodejs /app

# Create data directory for query logs
RUN mkdir -p /app/data && chown -R nextjs:nodejs /app/data

USER nextjs

EXPOSE 3000

CMD ["node", ".next/standalone/server.js"]
