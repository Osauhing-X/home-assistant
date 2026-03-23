FROM node:20-bullseye-slim

# Töökataloog add-onis
WORKDIR /data

# Kopeerime Node.js koodi
COPY package.json package-lock.json* ./ 
RUN npm install --production

COPY index.js ./ 
COPY plugins/ ./plugins

CMD ["node", "index.js"]