import Sensors.sensor_scripts as sensors
import argparse


def create_sensor(sensor: sensors, number: int, sender_topic: str) -> sensors:
    s = sensor(BROKER, PORT, sender_topic + str(number), NAME + str(number))
    return s


if __name__ == "__main__":
    type_of_sensors = {
        "GasValveSensor": sensors.GasValveSensor,
        "SmartPlug": sensors.SmartPlug,
        "Lock": sensors.Lock,
        "GasDetector": sensors.GasDetector,
        "Light": sensors.Light,
        "TemperatureSensor": sensors.TemperatureSensor,
        "HumidSensor": sensors.HumidSensor,
        "RollerShade": sensors.RollerShade,
        "GarageDoor": sensors.GarageDoor,
    }

    parser = argparse.ArgumentParser(description="Process input...")
    parser.add_argument("broker", type=str)
    parser.add_argument("port", type=int)
    parser.add_argument("name", type=str)
    parser.add_argument("number", type=int)
    parser.add_argument("object", type=str)
    parser.add_argument("topic", type=str)

    args = parser.parse_args()
    BROKER = args.broker
    PORT = args.port
    NAME = args.name
    sensor_num = args.number
    sensor_name = args.object
    sensor_topic = args.topic

    SENSOR = type_of_sensors[sensor_name]

    print("My ID: ", NAME + str(sensor_num), " | Sensor: ", sensor_name)

    sensor = create_sensor(SENSOR, sensor_num, sensor_topic)
    sensor.publish({})