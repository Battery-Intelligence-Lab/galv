FROM node:lts as build
RUN mkdir -p /app
WORKDIR /app
COPY package.json /app

RUN npm install --legacy-peer-deps

COPY . /app
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

