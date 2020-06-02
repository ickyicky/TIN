FROM python:slim

RUN mkdir /app
RUN mkdir /app/tin

ARG bsp_username="user"
ARG bsp_group="group"
RUN addgroup --gid 1024 $bsp_group
RUN useradd --home-dir /app --shell /sbin/nologin --gid 1024 $bsp_username

WORKDIR /app

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update && apt install postgresql gcc libpq-dev -y
RUN python -m pip install pyjwt sqlalchemy psycopg2 pytest coverage requests pytest-cov

USER $bsp_username

COPY ./tin /app/tin
CMD ["python", "-m", "tin", "-c", "/app/config.json", "--start"]
