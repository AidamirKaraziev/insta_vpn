FROM python:3.8

RUN mkdir /insta_vpn

WORKDIR /insta_vpn

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh
