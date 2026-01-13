FROM node
WORKDIR /micro_blog_frontend
COPY . .
RUN npm ci
EXPOSE 5173
CMD ["npm", "run", "dev"]