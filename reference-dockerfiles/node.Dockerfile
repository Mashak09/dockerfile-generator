FROM node:22-slim
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev
COPY . .
USER node
EXPOSE 3000
CMD ["node", "index.js"]
