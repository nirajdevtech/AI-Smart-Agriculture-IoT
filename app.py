from flask import Flask, render_template
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import random

app = Flask(__name__)

sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "soil_moisture": 0
}

pump_status = "OFF"
crop_health = "🟢 Healthy"
system_status = "🟢 ONLINE"
water_saved = 0

history = []

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smart_agriculture_iot"

weather_temp = 32
rain_probability = 40
recommendation = "Irrigation Recommended"


def calculate_crop_health(temp, humidity, soil):

    score = 0

    if 20 <= temp <= 35:
        score += 1

    if humidity >= 50:
        score += 1

    if soil >= 40:
        score += 1

    if score == 3:
        return "🟢 Healthy"
    elif score == 2:
        return "🟡 Warning"
    else:
        return "🔴 Critical"


def update_weather():

    global weather_temp
    global rain_probability
    global recommendation

    weather_temp = random.randint(28, 40)
    rain_probability = random.randint(0, 100)

    if rain_probability > 60:
        recommendation = "⛈ Delay Irrigation"
    else:
        recommendation = "💧 Irrigation Recommended"


def on_message(client, userdata, msg):

    global sensor_data
    global pump_status
    global crop_health
    global water_saved
    global history

    try:

        sensor_data = json.loads(msg.payload.decode())

        if sensor_data["soil_moisture"] < 30:
            pump_status = "ON"
        else:
            pump_status = "OFF"
            water_saved += 2

        crop_health = calculate_crop_health(
            sensor_data["temperature"],
            sensor_data["humidity"],
            sensor_data["soil_moisture"]
        )

        update_weather()

        history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "temperature": sensor_data["temperature"],
            "humidity": sensor_data["humidity"],
            "soil_moisture": sensor_data["soil_moisture"]
        })

        history = history[-10:]

    except Exception as e:
        print("Error:", e)


client = mqtt.Client()
client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(TOPIC)

client.loop_start()


@app.route("/")
def home():

    avg_temp = round(
        sum(x["temperature"] for x in history) /
        max(len(history), 1),
        1
    )

    avg_humidity = round(
        sum(x["humidity"] for x in history) /
        max(len(history), 1),
        1
    )

    return render_template(
        "index.html",
        data=sensor_data,
        pump_status=pump_status,
        crop_health=crop_health,
        history=history[::-1],
        avg_temp=avg_temp,
        avg_humidity=avg_humidity,
        total_readings=len(history),
        water_saved=water_saved,
        system_status=system_status,
        weather_temp=weather_temp,
        rain_probability=rain_probability,
        recommendation=recommendation
    )


if __name__ == "__main__":
    app.run(debug=True)