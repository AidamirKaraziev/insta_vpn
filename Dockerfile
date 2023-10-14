FROM python:3.8

RUN mkdir /insta_vpn
RUN apt-get update && apt-get install -y postgresql-client


WORKDIR /insta_vpn

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh
