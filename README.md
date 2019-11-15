# fake-cam

![Supported Python Versions](https://img.shields.io/badge/python-3.3%20%7C%203.4%20%7C%203.5%20%7C%203.6%20%7C%203.7-blue.svg)
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![License](http://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](LICENSE)

A Python app and Docker image for webcam stream manipulation. This app will take the feed from the webcam (/dev/video0) and allow you to modify the video stream. It will send that modified output to a new, fake webcam device (/dev/video1) which can be used in chat applications like Google Hangouts/Meet, Zoom, etc.

Requires: A Linux host system (I used Ubuntu)

Original purpose: being able to apply deep fake effects during live video calls.

## Running

1) Make sure you install the libraries from 'On the host system'
2) Build docker image

Then:
```
sudo modprobe v4l2loopback exclusive_caps=1 && \
docker run -it --rm --device /dev/video0:/dev/video0 --device /dev/video1:/dev/video1 -v $(pwd):/code webcam:latest /bin/bash -l
```

You should be able to select the new webcam in your web browser / chat application.

## On the host system
```
sudo apt install v4l2loopback-dkms
```

Allows webcam to be used by Chrome, etc
```
sudo modprobe v4l2loopback exclusive_caps=1
```

## Docker image

### Building

```
docker build -t webcam:latest .
```
