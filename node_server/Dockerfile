ARG BUILD_FROM
FROM $BUILD_FROM

# Node.js ja git priv repo jaoks
RUN apk add --no-cache nodejs npm git

# s6 teenuste kataloog
COPY etc /etc

# CMD peab jääma HA init / s6 overlay standardiks
CMD ["/init"]