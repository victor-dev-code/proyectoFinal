FROM php:7.2-apache

RUN apt-get update
RUN apt-get install -y nano
RUN apt-get install -y python3-pip
RUN RUNLEVEL=1 apt-get install -y libapache2-mod-wsgi-py3

FROM python:3.7
 
COPY ./requirements.txt /tmp 

RUN pip3 install -r /tmp/requirements.txt 


ENV secretKey="" 
ENV nameBD="" 
ENV userBD="josu" 
ENV pwdbd="" 
ENV bdHost="" 
ENV bdPort="3306" 

RUN mkdir /code 

RUN mkdir /start 

COPY ./run.sh /start 

WORKDIR /code 

RUN chmod +x /start/run.sh 

RUN useradd josu -s /bin/bash 

RUN chown -R josu /code 

RUN chown -R josu /start 

USER josu

CMD /start/run.sh
