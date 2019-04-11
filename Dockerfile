
FROM python:3.6-alpine

RUN apk update && apk add py-configobj libusb py-pip python-dev gcc linux-headers musl-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

CMD [ "python", "./cloud4rpi_monitor.py" ]
