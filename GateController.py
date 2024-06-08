import time
import random
from StateModel import *
from Button import *
from Counters import *
from Log import *
from Gate import *
from Displays import *
from Buzzer import *

class GateController:

    def __init__(self):
        
        self._button1 = Button(9, "Yellow Button", buttonhandler=None)
        self._button2 = Button(14, "Blue Button", buttonhandler=None)  # Update to use GP14
        self._display = LCDDisplay(sda=0, scl=1, i2cid=0)
        self._gate = Gate()
        self._buzzer = PassiveBuzzer(16)
        self._timer = SoftwareTimer(None)
        
        self._model = StateModel(6, self, debug=True)
        
        self._model.addButton(self._button1)
        self._model.addButton(self._button2)
        
        self._model.addTimer(self._timer)
        
        # Define transitions for the passcode sequence
        self._model.addTransition(0, [BTN1_PRESS], 1)
        self._model.addTransition(1, [BTN2_PRESS], 2)
        self._model.addTransition(2, [BTN1_PRESS], 3)
        
        self._model.addTransition(3, [TIMEOUT], 0)  # Reset to state 0 after timeout
        
        # Reset to state 0 for any incorrect button press in state 1 and 2, with wrong passcode message
        self._model.addTransition(1, [BTN1_PRESS], 5)
        self._model.addTransition(2, [BTN2_PRESS], 5)
        
        # Allow the gate to be triggered by motion sensor
        self._model.addTransition(0, [TIMEOUT], 4)  # Initial state to motion detection state after timeout
        
        # Motion detection transitions
        self._model.addTransition(4, [TIMEOUT], 0)
        self._model.addTransition(4, [BTN1_PRESS, BTN2_PRESS, BTN2_RELEASE, BTN1_RELEASE], 0)  # Reset sequence on any button press in this state
        
        # Transition from wrong passcode state to initial state
        self._model.addTransition(5, [TIMEOUT], 0)

    def run(self):
        self._model.run()

    def stateDo(self, state):
        if state == 0:
            if self._gate.motionDetected():
                self._model.gotoState(4)
        elif state == 4:
            if self._gate.vehiclePresent():
                self._model.gotoState(3)

    def stateEntered(self, state, event):
        Log.d(f'State {state} entered')
        if state == 0:
            self._gate.close()
            self._display.clear() # to clear the screen
            self._display.showText('Enter 3 Digit   Passcode     ')
        elif state == 1:
            self._display.showText('Enter 2nd Digit         ')
        elif state == 2:
            self._display.showText('Enter 3rd Digit          ')
        elif state == 3:
            self._gate.open()
            self._buzzer.beep()
            self._display.showText('Gate OPEN        ')
            self._timer.start(5)  # Keep gate open for 5 seconds
        elif state == 4:
            self._display.showText('Gate Opening..  ')
        elif state == 5:
            self._display.showText('Wrong Passcode  Try Again ')
            self._timer.start(2)  # Display wrong passcode message for 2 seconds

    def stateLeft(self, state, event):
        Log.d(f'State {state} exited')
        if state in (3, 4, 5):
            self._timer.cancel()

if __name__ == '__main__':
    GateController().run()
