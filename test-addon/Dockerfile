FROM python:3.11-slim

RUN pip install flask

COPY run.sh /run.sh
COPY www /data/www
RUN chmod +x /run.sh

EXPOSE 5000
CMD ["/run.sh"]
