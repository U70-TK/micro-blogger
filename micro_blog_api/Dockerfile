FROM node
# run npm 
WORKDIR /micro_blog_api
COPY . .
RUN npm ci

#TODO: this will need to be a different command (without the dev) for prod
CMD [ "npm",  "run", "start:dev" ]