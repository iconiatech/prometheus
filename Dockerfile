FROM python:3.6

EXPOSE 5000

WORKDIR /usr/src/app

# RUN apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev

RUN pip install --upgrade pip

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./prometheus.py"]
