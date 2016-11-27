# encoding: utf-8

# Start docker image with
# -e "DB=homecenter" -e "COLLECTION=edf" --link mongodb

import os
import RPi.GPIO as GPIO
from serial import Serial
import pyparsing as pp
from pymongo import MongoClient
from datetime import datetime
import threading


def main():
    threading.Timer(30, main).start()
    RED = 24
    GREEN = 26
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)

    client = MongoClient('mongodb', 27017)
    db = client[os.environ['DB']]
    collection = db[os.environ['COLLECTION']]

    ser = Serial('/dev/ttyAMA0', 1200, 7, 'E', 1, timeout=1)
    # must stty -F /dev/ttyAMA0 1200 sane evenp parenb cs7 -crtscts before !!
    # ser.open()
    # start by reading till the next new packet
    chunk = []
    while chunk[-2:] != ['\x02', '\n']:
        chunk.append(ser.read(1))
    chunk = []
    while chunk[-1:] != ['\x03']:
        chunk.append(ser.read(1))
    lines = ''.join(chunk).split('\r\n')

    # now parse the output
    parse_str = pp.Word(pp.alphas) + pp.Word(pp.alphanums)

    doc = {
        'datetime': datetime.now(),
    }

    for line in lines:
        res = parse_str.parseString(line)
        try:
            res[1] = float(res[1])
        except Exception:
            pass
        doc[res[0]] = res[1]

    collection.insert(doc)
    client.close()

    print('Successfully queried EDF information.')

    power = doc['IINST'] * 230.0
    if(power > 800):
        GPIO.output(RED, True)
        GPIO.output(GREEN, False)
    else:
        GPIO.output(RED, False)
        GPIO.output(GREEN, True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error while querying EDF information : {0}'.format(e))
