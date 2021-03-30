#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# main.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2021/3/30 下午2:49:20

from machine import Pin
from utime import ticks_ms, sleep_ms
from am7020.am7020_nb import AM7020NB
from am7020.am7020_mqtt import AM7020MQTT


apn = "twm.nbiot"
band = 28
MQTT_BROKER = "io.adafruit.com"
PORT = 1883
MQTT_USERNAME = "<YOUR USERNAME>"
MQTT_PASSWORD = "<YOUR AIO KEY>"
PUB_TEST_TOPIC = MQTT_USERNAME + "/feeds/pub"
SUB_TEST_TOPIC = MQTT_USERNAME + "/feeds/sub"
UPLOAD_INTERVAL_MS = 60000


nb = AM7020NB(1, 9600, 4, 5, 3, False)
mqtt = AM7020MQTT(nb)

led = Pin(25, Pin.OUT)


def nbConnect():
    print("Initializing modem...")
    while((not nb.init() or (not nb.nbiotConnect(apn, band)))):
        print(".")

    print("Waiting for network...")
    while(not nb.waitForNetwork()):
        print(".")
        sleep_ms(5000)
    print(" success")


def reConnBroker():
    if(not mqtt.chkConnBroker()):
        print("Connecting to", MQTT_BROKER, end="...")
        if(mqtt.connBroker(MQTT_BROKER, PORT, username=MQTT_USERNAME, password=MQTT_PASSWORD, mqtt_id="MY_AM7020_TEST_MQTTID")):
            print(" success")
            print("subscribe: ", SUB_TEST_TOPIC, end="")
            if(mqtt.subscribe(SUB_TEST_TOPIC, callback1)):
                print(" success")
            else:
                print(" fail")
        else:
            print(" fail")


def callback1(msg):
    print(SUB_TEST_TOPIC, ":", msg)
    if(msg == "ON"):
        led.value(1)
    else:
        led.value(0)


def main():
    nbConnect()
    reConnBroker()
    chk_net_timer = 0
    pub_data_timer = 0
    while(True):
        if(ticks_ms() > chk_net_timer):
            chk_net_timer = ticks_ms() + 10000
            if(not nb.chkNet()):
                nbConnect()
            reConnBroker()

        if(ticks_ms() > pub_data_timer):
            pub_data_timer = ticks_ms() + UPLOAD_INTERVAL_MS
            print("publish: ", pub_data_timer, end="")
            if(mqtt.publish(PUB_TEST_TOPIC, str(pub_data_timer))):
                print("  success")
            else:
                print("  Fail")
        mqtt.procSubs()


main()
