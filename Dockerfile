FROM ubuntu:16.04

RUN sed -i "s/archive.ubuntu./mirrors.aliyun./g" /etc/apt/sources.list
RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list
RUN sed -i "s/security.debian.org/mirrors.aliyun.com\/debian-security/g" /etc/apt/sources.list
RUN apt-get update -y && \

	apt-get install -y python-pip python-dev


COPY ./requirements.txt /app/requirements.txt


WORKDIR /app


RUN pip install -r requirements.txt


EXPOSE 5000
COPY . /app


ENV FLASK_APP=app


ENV FLASK_RUN_PORT=5000
CMD [ "flask", "run", "--host", "0.0.0.0" ]
