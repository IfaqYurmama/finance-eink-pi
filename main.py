#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import locale
import time
from datetime import datetime
import signal
import urllib.request, json
from PIL import Image,ImageDraw,ImageFont, ImageOps

from symbols import symbols
class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True

IS_RASP = os.environ['LOGNAME'] == 'pi'
IS_FULL_REFRESH = time.localtime().tm_hour % 3 == 0
currentTimeStamp = datetime.now()

if IS_RASP:
    libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
    if os.path.exists(libdir):
        sys.path.append(libdir)
    from waveshare_epd import epd3in7
    epd = epd3in7.EPD()

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
ubuntuFont = os.path.join(os.path.dirname(os.path.realpath(__file__)), "UbuntuMono-R.ttf")
font16 = ImageFont.truetype(ubuntuFont, 16)
font18 = ImageFont.truetype(ubuntuFont, 22)

symbols = sorted(symbols, key=lambda k: k['name'])

def nf(val):
    return locale.format_string('%.2f', val)

def toNum(val):
    if (type(val) == str):
        val = val.replace('%', '')
        val = locale.atof(val)
    return val

def nfPlus(val):
    return locale.format_string('%+.2f', val) + '€'

def drawImage(draw, startPoint, isin):
    chartImg = Image.new('RGBA', (145, 70), (255, 255, 255, 1))
    try:
    	url = 'https://www.tradegate.de/images/charts/small/' + isin + '.png'
    	chartImg = Image.open(urllib.request.urlopen(url))
    #TODO: refactor and change this so the chart size fits better, perhaps reduce # of tickers per page
    except Exception as inst:
    	print(inst)
    	print(url)
    	print('Fehler bei Bilderstellung für ',isin)
    chartImg = chartImg.resize((145, 70))
    chartImg = chartImg.crop(
       	(0, 0, chartImg.size[0], chartImg.size[1] - 17)
    )
    chartImg = ImageOps.invert(chartImg.convert('L'))
    chartImg = ImageOps.autocontrast(chartImg, cutoff=8)
    offset = (startPoint[0], startPoint[1] - 20)
    draw.bitmap(offset, chartImg)
    #chartImg.save(isin + '.png')

width=480
height=280
lineHeight=52

cols = [2, 85, 180,
    280, 340]
def getImage():
    y=32
    colTexts = [
        'WKN',
        'Preis'.rjust(7),
        'Tag/Gesamt'.rjust(8),
        'High/low'.rjust(6),
        currentTimeStamp.strftime("%a %d.%m.%H:%M").rjust(17)
    ]
    image = Image.new('L', (width, height), 0xFF)
    draw = ImageDraw.Draw(image)
    for idx, colText in enumerate(colTexts):
        draw.text((cols[idx], 0), colText, font=font16, fill=0)

    if sys.argv[1] == '1':
        filtered_symbols = symbols[:5]
    elif sys.argv[1] == '2':
        filtered_symbols = symbols[5:10]
    else:
        filtered_symbols = symbols[10:]

    for symbol in filtered_symbols:
        print('aktie: ', symbol['name'])
        tradegateCall = "https://www.tradegate.de/refresh.php?isin=" + symbol['isin']
        with urllib.request.urlopen(tradegateCall) as url:
            data = json.loads(url.read().decode())
            tradesToday = True
            try:
                price = toNum(data['last'])
            except:
                price = toNum(data['close'])
                tradesToday = False
                print('Aktie hat noch keine Trades heute, nehme Close Price')
            cost = 0
            worth = 0
            for lot in symbol['lots']:
                cost += lot['shares'] * lot['cost']
                worth += lot['shares'] * price
            if(tradesToday):
                dayLow = toNum(data['low'])
                dayHigh = toNum(data['high'])
            else:
                dayLow = toNum(data['close'])
                dayHigh = dayLow
            delta = toNum(data['delta'])
            if symbol['name'].startswith("."):
                vals = [
                    symbol['name'],
                    nf(price).rjust(6)+" \u20ac",
                    str(data['delta']).rjust(9)+ " %",
                    nf(dayHigh).rjust(6)
                ]
            else:
                vals = [
                    symbol['name']+"x"+str(lot['shares']),
                    nf(price).rjust(6)+" \u20ac",
                    str(data['delta']).rjust(9)+ " %",
                    nf(dayHigh).rjust(6)
                ]
            lowerVals = [
                None,
                nf(price * lot['shares']).rjust(6)+" \u20ac",
                nfPlus(worth - cost).rjust(9),
                nf(dayLow).rjust(6)
            ]
            for idx, val in enumerate(vals):
                font = font18
                offsetY = 0
                lowerVal = lowerVals[idx]
                if lowerVal:
                    offsetY = -9
                    font = font16
                    draw.text((cols[idx], y+20 + offsetY), lowerVal, font=font16, fill=0)
                draw.text((cols[idx], y + offsetY), val, font=font, fill=0)

            try:
                drawImage(draw, (cols[-1], y), symbol['isin'])
            except Exception as e:
                print("error drawing for", symbol['code'], e)
        y += lineHeight
        #print('symbol: ',symbol)
    return image

def draw(image):
    image=image.transpose(Image.ROTATE_180)
    epd.init(0)
    epd.display_4Gray(epd.getbuffer_4Gray(image))
    epd.sleep()

if __name__ == '__main__':
    if IS_RASP:
        image = getImage()
        draw(image)
    else:
        image = getImage()
        image.show()
