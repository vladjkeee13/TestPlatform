FROM python:3.6-jessie

RUN mkdir /test_platform

WORKDIR /test_platform

COPY . /test_platform/

RUN pip3 install -r requirements.txt

EXPOSE 8000
