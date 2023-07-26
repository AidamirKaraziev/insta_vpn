FROM python:3.8

RUN mkdir /vpn_app

WORKDIR /vpn_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh
