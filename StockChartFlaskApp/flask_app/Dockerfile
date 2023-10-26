FROM tiangolo/uwsgi-nginx-flask:python3.11

# Environment variables particular to this Docker image:
# ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static

# As it turns out, the source image has a "buildkit" that does "COPY ./app /app # buildkit",
# but let's be intentional about it and copy that folder as well as the other required files:

COPY ./app /app/app
COPY ./main.py /app/main.py
COPY ./uwsgi.ini /app/uwsgi.ini
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
