import random
import time
import json
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smart_agriculture_iot"

client = mqtt.Client()
client.connect(BROKER, PORT)

print("Sending sensor data...")

while True:

    data = {
        "temperature": random.randint(20, 40),
        "humidity": random.randint(40, 90),
        "soil_moisture": random.randint(10, 100)
    }

    client.publish(TOPIC, json.dumps(data))

    print(data)

    time.sleep(3)