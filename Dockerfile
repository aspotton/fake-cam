FROM ubuntu:20.04

# Prevent tzdata config questions
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update --fix-missing && \
    apt-get install -y sudo libsm6 libxext6 libxrender-dev libv4l-dev python3.8 python3-pip python3.8-dev git libgl1-mesa-glx libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /code/

RUN pip3 install -r /code/requirements.txt
