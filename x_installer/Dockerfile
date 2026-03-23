ARG BUILD_FROM
FROM $BUILD_FROM

# Node.js ei ole vajalik, kuna run.sh ainult kopeerib pluginad
COPY run.sh /run.sh
COPY plugins /plugins
RUN chmod +x /run.sh

CMD [ "/run.sh" ]