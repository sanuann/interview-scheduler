FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install unzip
RUN mkdir /src
WORKDIR /src
ADD requirements.pip .
RUN pip install -r requirements.pip --src /usr/local/src
ADD . .
EXPOSE 8000
VOLUME /src
CMD [".docker/run.sh"]
