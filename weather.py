import pprint
import os
import requests
import sys
import datetime as dt
import time
from PIL import Image, ImageDraw, ImageFont



WIDTH = 640  # width of the display in pixels
HEIGHT = 384  # height of the display in pixels
SLEEP_TIME_S = 300  # sleep time in seconds
OWM_URL_TEMPLATE = "https://api.openweathermap.org/data/2.5/weather?q={location}&APPID={appid}&lang=de&units=metric"
OWM_LOCATION = os.environ["OWM_LOCATION"]
OWM_API_KEY = os.environ["OWM_API_KEY"]  # open weather map API key


def draw_image():
    img = Image.new('1', (WIDTH, HEIGHT), 1)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 48)
    font_lg = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 96)

    # current date and time
    now = dt.datetime.now()
    draw.text((130, 10), format(now, "%d.%m.%y %H:%M"), font=font)
    draw.line([(0, 60), (img.size[0], 60)], width=5)

    # get current weather data from open weather map
    resp = requests.get(OWM_URL_TEMPLATE.format(location=OWM_LOCATION, appid=OWM_API_KEY))
    if resp.status_code == requests.codes.ok:
        w_data = resp.json()

        temp_C = w_data["main"]["temp"]
        hum_pct = w_data["main"]["humidity"]
        press_hPa = w_data["main"]["pressure"]

        # add weather info to the image
        draw.text((180, 90), "{:.1f}°C".format(temp_C), font=font_lg)

        hum_img = Image.open("humidity.bmp", "r")
        draw.bitmap((35, 295), hum_img)
        draw.text((100, 310), "{:.0f}%".format(hum_pct), font=font)

        pres_img = Image.open("pressure.bmp", "r")
        draw.bitmap((355, 295), pres_img)
        draw.text((420, 310), "{:.0f}hPa".format(press_hPa), font=font)

        # weather icon
        try:
            icon_code = w_data["weather"][0]["icon"]
            icon = Image.open("icons/{icon_code}.bmp".format(icon_code=icon_code))
            draw.bitmap((240, 170), icon)

        except Exception:
            print("Error reading weather id.")

    return img


def display_loop():
    import epd7in5
    epd = epd7in5.EPD()
    epd.init()

    while 1:
        # display the image on the epaper display
        epd.display_frame(epd.get_frame_buffer(draw_image()))
        time.sleep(SLEEP_TIME_S)


def save_image():
    img = draw_image()
    img.save("output.bmp")


if __name__ == "__main__":
    # save_image()
    display_loop()
