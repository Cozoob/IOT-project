import fnmatch
import os
import subprocess
import sys
import time

from Sensors import sensor, sensor_scripts
import signal

NAME = "sensor-"
COUNTER = 0

BROKER = "127.0.0.1"
PORT = 8080

CHILDREN = []


def signal_handler(signum, frame):
    print("Killing all children!")
    for child in CHILDREN:
        print("pid: ", child.pid)
        child.terminate()
        time.sleep(1)
        print("status: ", child.poll())

    print("Exit the program in 3 seconds...")
    time.sleep(3)
    exit(0)


def create_subprocess(class_name: str):
    global COUNTER
    p = subprocess.Popen(
        ["python3", file] + [BROKER, str(PORT), NAME, str(COUNTER), class_name, NAME],
        env=process_env,
    )
    print("Sensor child's pid: ", p.pid, " | Sensor type: ", class_name)
    CHILDREN.append(p)
    COUNTER += 1


def locate(pattern, root=os.curdir):
    """
    Locate dir matching supplied dirname pattern in and below
    supplied root directory.
    """
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for dirname in fnmatch.filter(dirs, pattern):
            return os.path.join(path, dirname)


if __name__ == "__main__":
    # handling all signals
    for i in [x for x in dir(signal) if x.startswith("SIG")]:
        try:
            signum = getattr(signal, i)
            if isinstance(signum, signal.Signals):
                signal.signal(signum, signal_handler)
        except (OSError, RuntimeError):  # OSError for Python3, RuntimeError for 2
            print("Skipping {}".format(i))

    time.sleep(1)

    file = os.path.join(os.getcwd(), "sensor.py")
    process_env = os.environ.copy()

    create_subprocess(sensor_scripts.GasValveSensor.__name__)
    create_subprocess(sensor_scripts.SmartPlug.__name__)
    create_subprocess(sensor_scripts.Lock.__name__)
    create_subprocess(sensor_scripts.GasDetector.__name__)
    create_subprocess(sensor_scripts.Light.__name__)
    create_subprocess(sensor_scripts.TemperatureSensor.__name__)
    create_subprocess(sensor_scripts.HumidSensor.__name__)
    create_subprocess(sensor_scripts.RollerShade.__name__)
    create_subprocess(sensor_scripts.GarageDoor.__name__)
    create_subprocess(sensor_scripts.RollerShade.__name__)

    while True:
        pass
