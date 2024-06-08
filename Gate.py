from Sensors import *
from Motors import *
from Lights import *

red = Light(8, "Red Light LED")
green = Light(13, "Green Light LED")

class Gate:
    """...."""

    def __init__(self, servoPin=10, pirpin=11, proxpin=12):
        self._servo = Servo(pin=servoPin, name="Gate 1")
        self._pir = DigitalSensor(pin=pirpin, lowactive=False)
        self._prox = DigitalSensor(pin=proxpin)

    def open(self):
        self._servo.setAngle(90)
        red.off()
        green.on()

    def close(self):
        self._servo.setAngle(180)
        green.off()
        red.on()

    def motionDetected(self):
        return self._pir.tripped()

    def vehiclePresent(self):
        return self._prox.tripped()
        