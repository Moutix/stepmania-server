FROM python:alpine3.13

WORKDIR /usr/src/stepmania-server

RUN pip install smserver \
 && addgroup -S stepmania \
 && adduser -S stepmania -G stepmania

USER stepmania
WORKDIR /home/stepmania

EXPOSE 8765

ENTRYPOINT ["smserver"]