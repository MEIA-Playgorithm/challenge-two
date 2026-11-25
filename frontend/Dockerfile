FROM node:22.22-alpine
WORKDIR /app

COPY . .
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm ci && npm run build

CMD ["./node_modules/.bin/vite", "preview", "--host"]
