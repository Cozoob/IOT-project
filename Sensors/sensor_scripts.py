import uuid
import json

from paho.mqtt import client as mqtt_client
from time import sleep
from random import randint

from abc import ABC, abstractmethod

SLEEP_TIME = 0.5


class Sensor(ABC):
    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        self.sender_topic = sender_topic
        self.port = port
        self.client_id = client_id
        self.broker = broker
        self.client = self.__connect_mqtt()

    def __connect_mqtt(self) -> mqtt_client:
        def on_connect(client_id: mqtt_client, userdata, flags, rc: int):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id=self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)

        return client

    def _check_status(self, status: int):
        if status != 0:
            print(f"Failed to send message to topic {self.sender_topic}")

    @abstractmethod
    def publish(self, data: str):
        ...

    @abstractmethod
    def subscribe(self, client: mqtt_client):
        ...

    @abstractmethod
    def _get_random_data(self) -> str:
        ...


class GasValveSensor(Sensor):
    is_open = True

    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        self.client.loop_start()
        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            # Should receive JSON of format :
            # {
            # 'open': True/False,
            # }
            m = msg.payload.decode("utf-8")
            m = json.loads(m)
            print(f"Received `{m}` from `{msg.topic}` topic")

            try:
                if m["open"] == "False":
                    self.is_open = False
                else:
                    self.is_open = True
            except KeyError:
                # inappropriate data sent
                pass

        topic = self.sender_topic + "/state"
        client.subscribe(topic)
        client.on_message = on_message

    def _get_random_data(self) -> str:
        # average usage of gas per minute is 0.5 kwh
        # then I assume that per 5 seconds usage is
        # between 300 kws and 420 kws
        data = dict()
        if self.is_open:
            gas_value = randint(300, 420)
        else:
            gas_value = 0
        data["gas_value"] = gas_value
        data["open"] = self.is_open
        return json.dumps(data)


class SmartPlug(Sensor):
    is_turn_on = True

    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        self.client.loop_start()
        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            # Should receive JSON of format :
            # {
            # 'turn_on': True/False,
            # }
            m = msg.payload.decode("utf-8")
            m = json.loads(m)
            print(f"Received `{m}` from `{msg.topic}` topic")

            try:
                if m["turn_on"] == "False":
                    self.is_turn_on = False
                else:
                    self.is_turn_on = True
            except KeyError:
                # inappropriate data sent
                pass

        topic = self.sender_topic + "/state"
        client.subscribe(topic)
        client.on_message = on_message

    def _get_random_data(self) -> str:
        # average usage of gas per minute is 5 kwh
        # then I assume that per 5 seconds usage is
        # between 3000 kws and 4200 kws
        data = dict()
        if self.is_turn_on:
            power_value = randint(3000, 4200)
        else:
            power_value = 0
        data["power_value"] = power_value
        data["turn_on"] = self.is_turn_on
        return json.dumps(data)


class Lock(Sensor):
    open = True

    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        self.client.loop_start()
        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            # Should receive JSON of format :
            # {
            # 'open': True/False,
            # }
            m = msg.payload.decode("utf-8")
            m = json.loads(m)
            print(f"Received `{m}` from `{msg.topic}` topic")

            try:
                if m["open"] == "False":
                    self.open = False
                else:
                    self.open = True
            except KeyError:
                # inappropriate data sent
                pass

        topic = self.sender_topic + "/state"
        client.subscribe(topic)
        client.on_message = on_message

    def _get_random_data(self) -> str:
        data = dict()
        data["open"] = self.open
        return json.dumps(data)


class GasDetector(Sensor):
    is_gas_detected: bool = True

    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        self.client.loop_start()
        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        # Cannot modify state of gas detection
        ...

    def _get_random_data(self) -> str:
        data = dict()
        self.is_gas_detected = bool(randint(1, 100) > 2)
        data["gas_detected"] = self.is_gas_detected
        data["gas_density"] = 0
        if self.is_gas_detected:
            data["gas_density"] = randint(5, 20)  # [%]

        return json.dumps(data)


class Light(Sensor):
    is_turn_on = True
    color_temperatures = ["COOLEST", "COOL", "NEUTRAL", "WARM", "WARMEST"]
    color_temperature: str = "COOLEST"
    brightness: int = 0

    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        # self.subscribe_temperature()
        # self.subscribe_brightness()
        self.client.loop_start()
        # self.client2.loop_start()
        # self.client3.loop_start()

        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            # Should receive JSON of format :
            # {
            # 'turn_on': True/False,
            # 'brightness_value': INTEGER,
            # 'color_value': STRING
            # }

            m = msg.payload.decode("utf-8")
            m = json.loads(m)
            print(f"Received `{m}` from `{msg.topic}` topic")

            try:
                if m["turn_on"] == "False":
                    self.is_turn_on = False
                else:
                    self.is_turn_on = True

                try:
                    self.brightness = int(m["brightness_value"])
                except ValueError:
                    self.brightness = 0

                self.color_temperature = m["color_value"]
            except KeyError:
                # inappropriate data sent
                pass

        topic = self.sender_topic + "/state"
        client.subscribe(topic)
        client.on_message = on_message

    def _get_random_data(self) -> str:
        # brightness [%]
        # color_temperature in [coolest, cool, neutral, warm, warmest]

        data = dict()
        data["brightness_value"] = self.brightness
        data["color_value"] = self.color_temperature
        data["turn_on"] = self.is_turn_on
        print(data)
        return json.dumps(data)


class TemperatureSensor(Sensor):
    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        self.client.loop_start()
        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        # Cannot change state of temperature
        ...

    def _get_random_data(self) -> str:
        # return average temperature in household [celsius scale]
        # between 18-24
        data = dict()
        data["temperature"] = randint(18, 24)
        return json.dumps(data)


class HumidSensor(Sensor):
    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        self.client.loop_start()
        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        # Cannot change state of humidity
        ...

    def _get_random_data(self) -> str:
        # return average humidity in household:
        # between 30-60
        data = dict()
        data["humid"] = randint(30, 60)
        return json.dumps(data)


class RollerShade(Sensor):
    is_open = True
    open_value = 100

    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        self.client.loop_start()
        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            # Should receive JSON of format :
            # {
            # 'open': True/False,
            # 'open_value': INTEGER
            # }
            m = msg.payload.decode("utf-8")
            m = json.loads(m)
            print(f"Received `{m}` from `{msg.topic}` topic")

            try:
                if m["open"] == "False":
                    self.is_open = False
                    self.open_value = 0
                elif m["open"] == "True":
                    self.open = True

                if m["open_value"]:
                    self.open_value = int(m["open_value"])
                    self.is_open = self.open_value > 0
            except KeyError:
                # inappropriate data sent
                pass

        topic = self.sender_topic + "/state"
        client.subscribe(topic)
        client.on_message = on_message

    def _get_random_data(self) -> str:
        data = dict()
        data["open"] = self.is_open
        data["open_value"] = self.open_value
        return json.dumps(data)


class GarageDoor(Sensor):
    is_open = True

    def __init__(self, broker: str, port: int, sender_topic: str, client_id: str):
        super().__init__(broker, port, sender_topic, client_id)

    def publish(self, data: str):
        self.subscribe(self.client)
        self.client.loop_start()
        while True:
            random_data = self._get_random_data()
            result = self.client.publish(
                self.sender_topic, random_data
            )
            status = result[0]
            self._check_status(status)
            sleep(SLEEP_TIME)

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            # Should receive JSON of format :
            # {
            # 'open': True/False,
            # }
            m = msg.payload.decode("utf-8")
            m = json.loads(m)
            print(f"Received `{m}` from `{msg.topic}` topic")

            try:
                if m["open"] == "False":
                    self.is_open = False
                else:
                    self.is_open = True
            except KeyError:
                # inappropriate data sent
                pass

        client.subscribe(self.sender_topic + "/state")
        client.on_message = on_message

    def _get_random_data(self) -> str:
        data = dict()
        data["open"] = self.is_open
        return json.dumps(data)
