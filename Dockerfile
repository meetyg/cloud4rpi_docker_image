FROM python:3.6-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

# Install dependencies needed for pip installations (pip compiles some packages)
 # Remove dependencies previously installed

RUN apk update && \
    apk add --no-cache py-configobj libusb py-pip python-dev gcc linux-headers musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del py-configobj libusb py-pip python-dev gcc linux-headers musl-dev

COPY *.py ./

CMD [ "python", "./cloud4rpi_monitor.py" ]
