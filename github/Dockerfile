FROM node:20-alpine

RUN apk add --no-cache git

WORKDIR /app

COPY run.sh .

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]