# Первый этап: компилируем файлы React в статику
FROM node:13.12.0-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
RUN npm ci 
COPY . ./
RUN npm run build

# Второй этап: копируем скомпилированные файлы и запускаем nginx
FROM nginx:stable-alpine
COPY --from=build /app/build usr/share/nginx/html
CMD [ "nginx", "-g", "daemon off;" ]

