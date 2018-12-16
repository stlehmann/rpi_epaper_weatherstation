FROM python:latest
RUN apt-get update
RUN apt-get install -y fonts-freefont-ttf
RUN pip install pillow requests
WORKDIR epaper
ENV OWM_LOCATION="Schleußig,de"
ENV OWM_API_KEY="fc58dc7f33f2663ac890fdf4305cc783"
CMD python weather.py