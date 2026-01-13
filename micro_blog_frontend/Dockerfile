FROM node:20

WORKDIR /micro_blog_frontend

# Copy package files first to leverage Docker layer caching
COPY package.json package-lock.json* ./

# Use npm install to regenerate lockfile in-image when lockfile is out of sync.
# `--legacy-peer-deps` helps avoid peer-dependency failures during image builds.
RUN npm install --legacy-peer-deps --no-audit --no-fund

# Copy the rest of the app
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]