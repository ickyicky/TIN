FROM python:slim

RUN mkdir /app

ARG bsp_username="user"
ARG bsp_group="group"
RUN addgroup --gid 1024 $bsp_group
RUN useradd --home-dir /app --shell /sbin/nologin --gid 1024 $bsp_username

WORKDIR /app

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY . /app
CMD ["python", "server.py"]
