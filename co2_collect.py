from time import sleep
import board
import adafruit_scd4x
import requests

HA_URL = 'http://homeassistant:8123/api/states/'
with open('secrets.txt', 'r') as f:
    TOKEN = f.read().strip()

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "content-type": "application/json",
}

def push_sensor(entity_id, value, unit, name):
    url = HA_URL + entity_id
    data = {
        "state": value,
        "attributes": {
            "unit_of_measurement": unit,
            "friendly_name": name
        }
    }
    try:
        requests.post(url, headers=headers, json=data, timeout=5)
    except Exception as e:
        print(f"Error posting {entity_id}: {e}")

if __name__ == '__main__':
    i2c = board.I2C()
    scd4x = adafruit_scd4x.SCD4X(i2c)

    scd4x.start_periodic_measurement()
    print("Waiting for first measurement...")

    while True:
        if scd4x.data_ready:
            this_co2 = scd4x.CO2
            this_t = scd4x.temperature
            this_rh = scd4x.relative_humidity

            print(f"CO2: {this_co2} ppm, T: {this_t:.1f} °C, RH: {this_rh:.1f}%")
            push_sensor("sensor.living_room_co2", this_co2, "ppm", "Living Room CO₂")
            push_sensor("sensor.living_room_temperature", round(this_t, 1), "°C", "Living Room Temperature")
            push_sensor("sensor.living_room_humidity", round(this_rh, 1), "%", "Living Room Humidity")
            sleep(10)
        else:
            sleep(0.1)