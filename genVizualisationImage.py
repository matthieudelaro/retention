#!/usr/bin/env python3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as pltdate
from PIL import Image, ImageDraw

vizPathTemplate = 'viz/{runIndex}_{stateIndex}.png'


def vizualiseState(now, runIndex, stateIndex, dates, data):
    doReverse = True
    if doReverse:
        dates = list(reversed(dates))
        min_date = dates[0]
        data = list(reversed(data))
    else:
        min_date = dates[-1]
    # lines = []
    # with open('date') as f:
    #     lines = list(csv.reader(f))
    #     frmt = '%a %d %b %X %Z %Y'
    #     dates = [datetime.strptime(line[0], frmt) for line in lines]
    #     data = [line[1] for line in lines]

    # lines = [["Tue  2 Jun 16:55:51 CEST 2015","3"],
    #     ["Wed  3 Jun 14:51:49 CEST 2015","2",]]
    #     # "Fri  5 Jun 10:31:59 CEST 2015",]
    #     # "Sat  6 Jun 20:47:31 CEST 2015",
    #     # "Sun  7 Jun 13:58:23 CEST 2015",
    #     # "Mon  8 Jun 14:56:49 CEST 2015",
    #     # "Tue  9 Jun 23:39:11 CEST 2015",
    #     # "Sat 13 Jun 16:55:26 CEST 2015",
    #     # "Sun 14 Jun 15:52:34 CEST 2015",
    #     # "Sun 14 Jun 16:17:24 CEST 2015",
    #     # "Mon 15 Jun 13:23:18 CEST 2015"]
    #
    # frmt = '%a %d %b %X %Z %Y'
    # dates = [datetime.strptime(line[0], frmt) for line in lines]
    # data = [line[1] for line in lines]

    #datesnum = pltdate.date2num(dates)
    #fig, ax = plt.subplots()
    #ax.plot_date(datesnum, data, 'o')

    #plt.show()

    #generate image
    WIDTH, HEIGHT = 4000, 400
    BORDER = 70
    W = WIDTH - (2 * BORDER)
    H = HEIGHT - (2 * BORDER)


    colors = { '0': "lime", '1' : (255,200,200), '2' : (255,100,100), '3' : (255,0,0), '4': (0, 0, 255), '5': (100, 100, 255) }

    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    # min_date = dates[0]
    # max_date = datetime.now()
    max_date = now
    #print(min_date)
    #print(max_date)
    interval = max_date - min_date
    #print(interval.days)

    #draw frame
    draw = ImageDraw.Draw(image)
    draw.rectangle((BORDER, BORDER, WIDTH-BORDER, HEIGHT-BORDER), fill=(128,128,128), outline=(0,0,0))

    #draw circles
    circle_w = 10
    range_secs = W / interval.total_seconds()
    #print(range_secs)
    for i in range(len(dates)):
        wat = dates[i] - min_date
        offset_sec = (dates[i] - min_date).total_seconds()
        offset = range_secs * offset_sec
        x = BORDER + offset
        draw.ellipse((x, BORDER + 50, x + circle_w, BORDER + 50 + circle_w), outline=colors[data[i]])
        #draw.text((x, BORDER + 75), str(i), fill=colors[data[i]])

    #draw rectangles
    range_days = W / (interval.days + 1)
    #print("range_days",range_days)
    current_date = min_date
    date_month = min_date + relativedelta(months=1)
    current_index = 0
    for i in range(interval.days + 1):
        max_color = '0'
        while dates[current_index].date() == current_date.date():
            if int(data[current_index]) > int(max_color):
                max_color = data[current_index]
            current_index += 1
            if current_index > len(dates) - 1:
                current_index = 0
        x = BORDER + range_days * i
        draw.rectangle((x, BORDER + 100, x+range_days, BORDER + 100 + 50), fill=colors[max_color], outline=(0,0,0))
        if current_date == date_month:
            draw.line((x, BORDER + 100 +50, x, H + BORDER + 20), fill="black")
            draw.text((x, H + BORDER + 20), str(date_month.date()), fill="black")
            date_month = date_month + relativedelta(months=1)
        #draw.text((x, BORDER + 175), str(i), fill=colors[max_color])
        current_date = current_date + timedelta(days=1)

    #draw start and end dates
    draw.text((BORDER, H + BORDER + 20), str(min_date.date()), fill="black")
    draw.text((BORDER + W, H + BORDER + 20), str(max_date.date()), fill="black")

    # image.show()
    path = vizPathTemplate.format(runIndex=runIndex, stateIndex=stateIndex)
    path = path.replace(' ', '_')
    image.save(path)
    print(path)
