FROM klakegg/hugo:latest as hugo

COPY / /src

RUN cd /src && hugo

FROM nginx

COPY --from=hugo /src/public /usr/share/nginx/html
COPY container/nginx.conf /etc/nginx/nginx.conf

