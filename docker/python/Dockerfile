FROM python:3

WORKDIR /var/www/api

RUN pip install eve

RUN pip install PyJWT

RUN pip install flask_bcrypt

RUN pip install flask_cors

EXPOSE 5000

CMD [ "python", "./run.py" ]
