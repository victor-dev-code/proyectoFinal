FROM python:3.7
RUN pip3 install django==3.2.1
RUN pip3 install mysqlclient==1.4.6 
RUN pip3 install mysql-connector-python
RUN pip3 install PyMySQL
RUN pip3 install gunicorn

ENV secretKey="" 
ENV nameBD="" 
ENV userBD="root" 
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
