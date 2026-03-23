ARG BUILD_FROM
FROM $BUILD_FROM

# Node.js + bash
RUN apk add --no-cache nodejs npm bash

# Kopeeri run.sh ja tee executeable
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Kopeeri plugins kaust
COPY plugins /plugins

# Käivita run.sh PID 1
CMD ["/run.sh"]