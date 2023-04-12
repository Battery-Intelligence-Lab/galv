FROM node:lts@sha256:132309f5136555725debd57b711eb4b329fff22a00588834dbec391a3f9782cf as build
RUN mkdir -p /app
WORKDIR /app
COPY package.json yarn.lock /app/

# Required to get react running:
ENV NODE_OPTIONS=--openssl-legacy-provider

RUN yarn install

COPY . /app
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

