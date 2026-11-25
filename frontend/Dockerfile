FROM node:22.22-alpine
WORKDIR /app

COPY . .
RUN npm ci && npm run build

CMD ["./node_modules/.bin/vite", "preview", "--host"]
