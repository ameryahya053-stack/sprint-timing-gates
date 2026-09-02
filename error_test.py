from machine import Pin
import time
 
trig1, echo1 = Pin(25, Pin.OUT), Pin(32, Pin.IN)
trig2, echo2 = Pin(26, Pin.OUT), Pin(33, Pin.IN)
 
THRESHOLD = 7
CONFIRM   = 2
LOCKOUT   = 400
 
TRIALS = 30       # how many hand waves to record
 
 
def read_cm(trig, echo):
    trig.value(0)
    time.sleep_us(5)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    t0 = time.ticks_us()
    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), t0) > 20000:
            return None
    start = time.ticks_us()
    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), start) > 20000:
            return None
    return time.ticks_diff(time.ticks_us(), start) * 0.01715
 
 
class Gate:
    def __init__(self, trig, echo, name):
        self.trig, self.echo, self.name = trig, echo, name
        self.base = None
        self.count = 0
        self.last = 0
        self.reads = 0        # total readings taken, used for sample rate
        self.drops = 0        # how many came back None
 
    def calibrate(self, n=60):
        vals = []
        for _ in range(n):
            d = read_cm(self.trig, self.echo)
            if d is not None:
                vals.append(d)
            time.sleep_ms(15)
        if len(vals) < n // 2:
            print(self.name, "calibration failed - check aim")
            return False
        vals.sort()
        self.base = vals[len(vals) // 2]
        print(self.name, "baseline {:.1f} cm".format(self.base))
        return True
    
 
    def check(self):
        d = read_cm(self.trig, self.echo)
        self.reads += 1
        if d is None:
            self.drops += 1
        blocked = (d is None) or (abs(d - self.base) > THRESHOLD)
        if blocked:
            self.count += 1
        else:
            self.count = 0
        if self.count == CONFIRM:
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last) > LOCKOUT:
                self.last = now
                self.count = 0
                return time.ticks_us()
        return None
 
 
def mean(xs):
    return sum(xs) / len(xs)
 
 
def stdev(xs):
    m = mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5
 
 
g1 = Gate(trig1, echo1, "gate A")
g2 = Gate(trig2, echo2, "gate B")
 
print("place both sensors side by side, aimed at the same panel")
print("calibrating - keep clear\n")
 
if g1.calibrate() and g2.calibrate():
 
    # measure the real sample rate first, it is what predicts the error
    t0 = time.ticks_ms()
    for _ in range(50):
        read_cm(trig1, echo1)
        read_cm(trig2, echo2)
    elapsed = time.ticks_diff(time.ticks_ms(), t0)
    rate = 50 / (elapsed / 1000)
    print("loop rate: {:.1f} Hz".format(rate))

 
    print("wave cardboard through", TRIALS, "times\n")
    

 
    diffs = []
    for i in range(TRIALS):
        tA = tB = None
        # wait until both gates have fired
        while tA is None or tB is None:
            if tA is None:
                tA = g1.check()
            if tB is None:
                tB = g2.check()
        d_ms = time.ticks_diff(tB, tA) / 1000
        diffs.append(d_ms)
        print("{:2d}  {:+.2f} ms".format(i + 1, d_ms))
        time.sleep(1)          # pause so one wave is not counted twice
 
    print("\n--- results ---")
    print("trials       ", len(diffs))
    print("mean         {:+.2f} ms".format(mean(diffs)))
    print("std dev      {:.2f} ms".format(stdev(diffs)))
    print("min          {:+.2f} ms".format(min(diffs)))
    print("max          {:+.2f} ms".format(max(diffs)))
    print("dropout rate {:.1f}%".format(
        100 * (g1.drops + g2.drops) / (g1.reads + g2.reads)))
 
