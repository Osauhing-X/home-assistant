ARG BUILD_FROM
FROM $BUILD_FROM

# Kopeeri s6 ja muud vajalikud skriptid (Supervisor base tegeleb selle eest)
COPY run.sh /run.sh
COPY www /data/www

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
