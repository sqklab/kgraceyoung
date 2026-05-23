FROM node:20-alpine AS deps
WORKDIR /app
COPY scripts /app/scripts
COPY frontend/client/package.json /app/frontend/client/package.json
WORKDIR /app/frontend/client
RUN npm install

FROM node:20-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_CLIENT_ORIGIN
ARG NEXT_PUBLIC_ADMIN_ORIGIN
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_CLIENT_ORIGIN=$NEXT_PUBLIC_CLIENT_ORIGIN \
    NEXT_PUBLIC_ADMIN_ORIGIN=$NEXT_PUBLIC_ADMIN_ORIGIN
COPY --from=deps /app/frontend/client/node_modules /app/frontend/client/node_modules
COPY scripts /app/scripts
COPY frontend/client /app/frontend/client
WORKDIR /app/frontend/client
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app/frontend/client
ENV NODE_ENV=production
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/frontend/client /app/frontend/client
EXPOSE 3000
CMD ["npm", "run", "start"]
