FROM python:3.7-alpine3.10

ARG FUNCTION_DIR="/function"

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.10/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.10/community" >> /etc/apk/repositories

RUN apk update && \
    apk add --no-cache \
    chromium \
    chromium-chromedriver \
    build-base \
    libtool \ 
    autoconf \ 
    automake \ 
    libexecinfo-dev \ 
    make \
    cmake \ 
    libcurl

WORKDIR ${FUNCTION_DIR}

ADD requirements.txt requirements.txt

RUN pip3 install -r requirements.txt awslambdaric

ADD app.py app.py

ADD entry_script.sh /entry_script.sh
ADD aws-lambda-rie /usr/local/bin/aws-lambda-rie

ENTRYPOINT [ "/entry_script.sh" ]
CMD [ "app.lambda_handler" ]