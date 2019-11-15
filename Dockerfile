FROM ubuntu:18.04

RUN apt-get update --fix-missing && \
    apt-get install -y sudo libsm6 libxext6 libxrender-dev libv4l-dev python3.6 python3-pip python3.6-dev git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /code/

RUN pip3 install -r /code/requirements.txt
