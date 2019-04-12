
FROM python:3.6-alpine

# Install dependencies needed for pip installations (pip compiles some packages)
RUN apk update && apk add --no-cache py-configobj libusb py-pip python-dev gcc linux-headers musl-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Remove dependencies previously installed
RUN apk remove py-configobj libusb py-pip python-dev gcc linux-headers musl-dev && apk clean cache

COPY *.py ./

CMD [ "python", "./cloud4rpi_monitor.py" ]
