## Docker Image for running Cloud4RPi (https://cloud4rpi.io/) monitoring script on SBCs
---
### Prerequisites:
- Register at Cloud4rpi (https://cloud4rpi.io/)
- In Cloud4Rpi site add a new device and get a device TOKEN (do this for each device you want to monitor on Cloud4Rpi)
- On your SBC (Raspberry pi, Odroid etc...) make sure you have docker installed.

### Usage:
You can pull this image from docker hub (https://hub.docker.com/r/meetyg/cloud4rpi), or build it yourself (usefull for customization).

#### Run it:
`sudo docker run -d --name c4rpi -e TOKEN=<YOUR-DEVICE-TOKEN> --hostname $(hostname) --restart unless-stopped meetyg/cloud4rpi:<architecture>`

Currently the following architectures are supported:<br>
`arm64v8` or `aarch64` - for 64 bit ARM devices<br>
`armhf` - for 32 bit ARM devices<br>

**NEW Feature:** Support for Getting Weather data from [OpenWeatherMap](https://openweathermap.org) !
In order to get data from OpenWeatherMap, you need to register, and get an API key.
You need to specify this key, and your city and country code (as recognized in OWM) as environment variables.
So just add to the `docker run` command the following variables (after specifying your Cloud4Rpi token):
`-e OWM_API_KEY=<YOUR-OWM-KEY> -e OWM_CITY_COUNTRY="London,GB"` for example.

#### Build it yourself:

In order to use the image, you need to build it first.
**Please note:** Building the docker image should be on your SBC.

1. Clone this repo: <br>
`git clone https://github.com/meetyg/cloud4rpi_docker_image.git`

2. Build the Dockerfile (this may take a while, please be patient!): <br>
`cd cloud4rpi_docker_image` <br>
`sudo docker build -t cloud4rpi .`

3. Now you can run the image. <br>
Don't forget to replace `<YOUR-DEVICE-TOKEN>` with the specific device token you got from Cloud4Rpi <br>
`sudo docker run -d --name c4rpi -e TOKEN=<YOUR-DEVICE-TOKEN> --hostname $(hostname) --restart unless-stopped cloud4rpi`
The docker container will run at startup, unless you stop it.

4. Check at Cloud4Rpi site to see if you device's info shows up. If so, you can create dashboards and alerts as you wish.
If it doesn't show up, check the docker logs to make sure the image is running without problems:
`sudo docker logs c4rpi` or `sudo docker ps` and check if its still running.

This was tested  and is working on the following SBCs running DietPi:
- Raspberry Pi 3
- Odroid XU4
- Pine Rock64 (Running 64 bit Linux)

#### License
Feel free to clone this repo and change the monitoring script `cloud4rpi_monitor.py` or the Dockerfile as you wish.
If you run into any problems open an issue, and I'll try to help as best as I can.
Please see the Cloud4Rpi licenses and terms/conditions.

#### Disclaimer
**Use this at your own risk!** <br>
I do not take any responsability what so ever...



