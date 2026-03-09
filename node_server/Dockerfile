FROM node:20-alpine

# vajalik git private repo jaoks
RUN apk add --no-cache git

# töökaust /app
WORKDIR /app

# paneme run.sh containerisse rooti
COPY run.sh /run.sh
RUN chmod +x /run.sh

# käivita addon
CMD ["/run.sh"]