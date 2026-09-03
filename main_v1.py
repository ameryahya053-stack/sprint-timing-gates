from machine import Pin      # lets me control the ESP32 pins
import time                  # lets me measure time

# gate 1 = start line, gate 2 = finish line
# trig sends the sound out, echo listens for it coming back
trig1, echo1 = Pin(25, Pin.OUT), Pin(32, Pin.IN)
trig2, echo2 = Pin(26, Pin.OUT), Pin(33, Pin.IN)

THRESHOLD = 7      # cm away from normal before I call the lane blocked
CONFIRM   = 2      # need this many blocked readings in a row, stops random glitches
LOCKOUT   = 400    # ms of ignoring after a trigger, so one runner is not counted twice. This is useless in this version of the code, but could help later avoid such issues.


def read_cm(trig, echo):
    # take one distance measurement, or None if the echo never comes back

    trig.value(0)              # start low so the pulse is clean
    time.sleep_us(5)
    trig.value(1)              # 10 microsecond pulse tells the sensor to fire
    time.sleep_us(10)
    trig.value(0)

    t0 = time.ticks_us()
    while echo.value() == 0:   # wait for the sound to leave
        if time.ticks_diff(time.ticks_us(), t0) > 20000:
            return None        # nothing happened, give up instead of freezing

    start = time.ticks_us()    # the moment the sound left

    while echo.value() == 1:   # wait for the sound to come back
        if time.ticks_diff(time.ticks_us(), start) > 20000:
            return None        # echo got lost, probably absorbed or aimed wrong

    # 0.01715 is the speed of sound in cm per microsecond, already halved
    # because the sound travelled there and back
    return time.ticks_diff(time.ticks_us(), start) * 0.01715


class Gate:
    # one sensor plus the logic that decides when someone passed it

    def __init__(self, trig, echo, name):
        self.trig, self.echo, self.name = trig, echo, name
        self.base = None       # normal distance when the lane is empty
        self.count = 0         # how many blocked readings in a row so far
        self.last = 0          # when this gate last triggered

    def calibrate(self, n=60):
        # learn what an empty lane looks like, so I never hardcode a distance

        vals = []
        for _ in range(n):
            d = read_cm(self.trig, self.echo)
            if d is not None:  # throw away failed readings
                vals.append(d)
            time.sleep_ms(15)

        if len(vals) < n // 2:            # more than half failed
            print(self.name, "calibration failed - check aim")
            return False

        vals.sort()
        # median not average, so one bad reading cannot drag the baseline off
        self.base = vals[len(vals) // 2]
        print(self.name, "baseline {:.1f} cm".format(self.base))
        return True

    def check(self):
        # returns the trigger time if someone just passed, otherwise None

        d = read_cm(self.trig, self.echo)

        # no echo counts as blocked too, a body can swallow the sound completely
        blocked = (d is None) or (abs(d - self.base) > THRESHOLD)

        if blocked:
            self.count += 1
        else:
            self.count = 0     # one clear reading resets it

        if self.count == CONFIRM:
            now = time.ticks_ms()
            # torso and trailing arm fire separately without this check
            if time.ticks_diff(now, self.last) > LOCKOUT:
                self.last = now
                return time.ticks_us()
        return None


g1 = Gate(trig1, echo1, "start")
g2 = Gate(trig2, echo2, "finish")

print("calibrating - keep the lanes clear")

if g1.calibrate() and g2.calibrate():
    print("ready\n")

    while True:
        # wait at the start gate
        t_start = None
        while t_start is None:
            t_start = g1.check()
        print("go")

        # wait at the finish gate
        t_end = None
        while t_end is None:
            t_end = g2.check()

        # both times come off the same clock, so no syncing needed
        ms = time.ticks_diff(t_end, t_start) / 1000
        print("{:.3f} s\n".format(ms / 1000))
