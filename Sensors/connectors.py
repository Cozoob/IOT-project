import typing
import uuid

from paho.mqtt import client as mqtt_client


class MQTTConnector:
    # main_topic is actually a sensor_id (the main topic for sensor)
    def __init__(self, broker: str, port: int, main_topic: str):
        self.broker = broker
        self.port = port
        self.main_topic = main_topic

        self.client_id = f"python-mqttt-{uuid.uuid1()}"
        self.client = self.__connect_mqtt()
        self.data: typing.Dict[str, str] = {}

    def set_broker(self, broker: str):
        self.broker = broker

    def set_port(self, port: int):
        self.port = port

    def publish(self, topic: str, data: typing.Any):
        # example of the actual topic: /sensor-0
        self.client.loop_start()
        self.client.publish(self.__get_actual_topic(topic), data)

    def subscribe(self, topic: str):
        def on_message(client, userdata, msg):
            self.data[topic] = msg.payload.decode("utf-8")
            print(f"Received `{self.data[topic]}` of key from `{msg.topic}` topic")

        self.data[topic] = "0"
        self.client.loop_start()
        actual_topic = self.__get_actual_topic(topic)
        self.client.subscribe(actual_topic)
        self.client.on_message = on_message

    def unsubscribe(self, topic: str):
        self.client.unsubscribe(self.__get_actual_topic(topic))

    def __connect_mqtt(self) -> mqtt_client:
        def on_connect(client_id: mqtt_client, userdata, flags, rc: int):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id=self.client_id)
        client.on_connect = on_connect

        try:
            client.connect(self.broker, self.port)
        except ConnectionRefusedError:
            print("Client was not able to connect to broker")

        return client

    def __get_actual_topic(self, topic: str):
        return self.main_topic + "/" + topic


class SensorConnector:
    subscribed_topics: typing.Dict[str, bool] = dict()

    def __init__(self, broker: str, port: int, main_topic: str):
        self.broker = broker
        self.port = port
        self.main_topic = main_topic
        self.connectors = {"publisher": MQTTConnector(broker, port, main_topic)}

    def send_data(self, topic: str, data: typing.Any):
        self.connectors["publisher"].publish(topic, data)

    def get_data(self, topic: str) -> str:
        if (
            topic not in self.subscribed_topics.keys()
            or topic not in self.connectors.keys()
        ):
            self.subscribed_topics[topic] = False
            self.connectors[topic] = MQTTConnector(
                self.broker, self.port, self.main_topic
            )
            self.subscribe(topic)
        elif self.subscribed_topics[topic] is False:
            self.subscribe(topic)

        return self.connectors[topic].data[topic]

    def subscribe(self, topic: str):
        self.connectors[topic].subscribe(topic)
        self.subscribed_topics[topic] = True

    def unsubscribe(self, topic: str):
        self.connectors[topic].unsubscribe(topic)
        self.subscribed_topics[topic] = False

    def unsubscribe_all(self):
        for topic, value in self.subscribed_topics.items():
            if value:
                print("Unsubscribed topic -> ", topic)
                self.unsubscribe(topic)