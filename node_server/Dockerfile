ARG BUILD_FROM
FROM $BUILD_FROM

# Install git Node.js jaoks
RUN apk add --no-cache git nodejs npm

WORKDIR /app

# Kloonitav repo ja run.sh
COPY run.sh /run.sh
RUN chmod +x /run.sh

# CMD peab vastama faili asukohale
CMD [ "/run.sh" ]