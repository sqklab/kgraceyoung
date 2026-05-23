FROM node:20-alpine AS deps
WORKDIR /app
COPY scripts /app/scripts
COPY frontend/admin/package.json /app/frontend/admin/package.json
WORKDIR /app/frontend/admin
RUN npm install

FROM node:20-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_CLIENT_ORIGIN
ARG NEXT_PUBLIC_ADMIN_ORIGIN
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_CLIENT_ORIGIN=$NEXT_PUBLIC_CLIENT_ORIGIN \
    NEXT_PUBLIC_ADMIN_ORIGIN=$NEXT_PUBLIC_ADMIN_ORIGIN
COPY --from=deps /app/frontend/admin/node_modules /app/frontend/admin/node_modules
COPY scripts /app/scripts
COPY frontend/admin /app/frontend/admin
WORKDIR /app/frontend/admin
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app/frontend/admin
ENV NODE_ENV=production
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/frontend/admin /app/frontend/admin
EXPOSE 3001
CMD ["npm", "run", "start", "--", "--port", "3001"]
