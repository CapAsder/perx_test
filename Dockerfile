FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential redis

COPY . /home/app
WORKDIR /home/app/
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

expose 80
CMD ["gunicorn", "boot:app", "-b", "0.0.0.0:5000"]
