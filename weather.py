"""Module for displaying weather data on a Waveshare EPaper display."""

import os
import sys
import requests
import datetime as dt
import time
from collections import namedtuple
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, List


WIDTH = 640  # width of the display in pixels
HEIGHT = 384  # height of the display in pixels
SLEEP_TIME_S = 300  # sleep time in seconds

# open weather map type constants
OWM_TYPE_WEATHER = "weather"
OWM_TYPE_FORECAST = "forecast"
OWM_LOCATION = os.environ["OWM_LOCATION"]
OWM_API_KEY = os.environ["OWM_API_KEY"]  # open weather map API key
OWM_URL_TEMPLATE = (
    "https://api.openweathermap.org/data/2.5/{type}?"
    "q={location}&APPID={appid}&lang=de&units=metric"
)


WeatherData = namedtuple("WeatherData", "temp_c hum_pct press_hpa icon")
ForecastData = namedtuple("ForecastData", "dt temp_c icon")


def get_weather_data() -> Optional[WeatherData]:
    """Get current weather data from OpenWeatherMap API."""
    resp = requests.get(
        OWM_URL_TEMPLATE.format(
            type=OWM_TYPE_WEATHER, location=OWM_LOCATION, appid=OWM_API_KEY
        )
    )

    if not (resp.status_code == requests.codes.ok):
        return None

    json = resp.json()

    data = WeatherData(
        temp_c=json["main"]["temp"],
        hum_pct=json["main"]["humidity"],
        press_hpa=json["main"]["pressure"],
        icon=json["weather"][0]["icon"],
    )
    return data


def get_forecast_data() -> Optional[List[ForecastData]]:
    """Get forecast weather data from OpenWeatherMap API."""
    resp = requests.get(
        OWM_URL_TEMPLATE.format(
            type=OWM_TYPE_FORECAST, location=OWM_LOCATION, appid=OWM_API_KEY
        )
    )

    if not (resp.status_code == requests.codes.ok):
        return None

    json = resp.json()
    items = [json["list"][i] for i in range(1, 7, 2)]
    data = [
        ForecastData(
            format(dt.datetime.fromtimestamp(item["dt"]), "%Hh"),
            item["main"]["temp"],
            item["weather"][0]["icon"],
        )
        for item in items
    ]
    return data


def get_icon(icon_code, max_size=None):
    """Get an icon by the given icon code."""
    icon = Image.open("icons/{0}.bmp".format(icon_code))

    if max_size is not None:
        icon.thumbnail((max_size, max_size))
    return icon


def draw_image():
    """Download weather data and create an image."""
    img = Image.new("1", (WIDTH, HEIGHT), 1)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 48)
    font_sm = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 28
    )
    font_lg = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 96
    )

    # current date and time
    now = dt.datetime.now()
    draw.text((130, 10), format(now, "%d.%m.%y %H:%M"), font=font)
    draw.line([(0, 60), (img.size[0], 60)], width=5)

    try:
        weather_data = get_weather_data()
    except Exception:
        weather_data = None

    if weather_data is not None:
        # add weather info to the image
        draw.text((280, 70), "{:3.1f}°C".format(weather_data.temp_c), font=font_lg)

        hum_img = Image.open("humidity.bmp", "r")
        draw.bitmap((40, 325), hum_img)
        draw.text((80, 330), "{:.0f}%".format(weather_data.hum_pct), font=font)

        pres_img = Image.open("pressure.bmp", "r")
        draw.bitmap((365, 325), pres_img)
        draw.text((410, 330), "{:.0f}hPa".format(weather_data.press_hpa), font=font)

        # weather icon
        try:
            icon_code = weather_data.icon
            icon = Image.open("icons/{icon_code}.bmp".format(icon_code=icon_code))
            draw.bitmap((20, 50), icon)

        except Exception:
            print("Error: No icon with id {0}.".format(icon_code))

    try:
        fc_dat = get_forecast_data()
    except Exception:
        fc_dat = None

    if fc_dat is not None:
        x = 140
        draw.text((x, 180), fc_dat[0].dt, font=font_sm)
        draw.text((x-30, 210), "{:.0f}°C".format(fc_dat[0].temp_c), font=font)
        draw.bitmap((x-20, 240), get_icon(fc_dat[0].icon, 80))

        x += 150
        draw.text((x, 180), fc_dat[1].dt, font=font_sm)
        draw.text((x-30, 210), "{:.0f}°C".format(fc_dat[1].temp_c), font=font)
        draw.bitmap((x-20, 240), get_icon(fc_dat[1].icon, 80))

        x += 150
        draw.text((x, 180), fc_dat[2].dt, font=font_sm)
        draw.text((x-30, 210), "{:.0f}°C".format(fc_dat[2].temp_c), font=font)
        draw.bitmap((x-20, 240), get_icon(fc_dat[2].icon, 80))

    return img


def display_loop():
    """Display the weather data in a loop."""
    import epd7in5

    epd = epd7in5.EPD()
    epd.init()

    while 1:
        # display the image on the epaper display
        epd.display_frame(epd.get_frame_buffer(draw_image()))
        time.sleep(SLEEP_TIME_S)


def save_image():
    """Draw an image and save it."""
    img = draw_image()
    img.save("output.bmp")


if __name__ == "__main__":
    if "-o" in sys.argv:
        save_image()
    else:
        display_loop()
