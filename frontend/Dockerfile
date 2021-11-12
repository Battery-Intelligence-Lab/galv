FROM node:lts as build
RUN mkdir -p /app
WORKDIR /app
COPY package.json yarn.lock /app/

RUN yarn install

COPY . /app
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

