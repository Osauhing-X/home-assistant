FROM node:20-alpine

RUN apk add --no-cache git

# run.sh rootis
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]