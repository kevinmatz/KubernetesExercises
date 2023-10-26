FROM tiangolo/uwsgi-nginx-flask:python3.11
# RUN apk --update add bash nano

# Environment variables particular to this Docker image:
# ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static

COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt

