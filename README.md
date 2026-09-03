# sprint-timing-gates
Automatic sprint timing gates - ESP32 and ultrasonic sensors, built for $30

---------------
**Why build sprint timing gates?**

In football, speed is critical, especially on the wider positions (RW,LW, RB,LB). Ever since I was 13 years old, every coach I would play for would assign me a central position for the following reasons:
- My ball control was superb for my age.
- My game intelligence and awareness was very special and the most valuable part of my game. 
- My passes in behind the defense were very accurate and well timed.
- I was one of the slowest players on my team, which does not make me a great option on the wider positions in the modern game, as wingers and fullbacks are expected to have speed to match modern football tactics.

Despite all these indications that the midfield was my strongest position, I was not convinced. Growing up, I always had the smallest frame on my team. Football, especially in our time, needs physicality, which I did not have. This made it harder for me to perform in games, as I would easily get pushed off the ball if I took more than two touches, eliminating one of my biggest strengths: dribbling. I requested to play on the wing many times to all my coaches across U13-U17, but most coaches were not willing to change their tactical approaches of a modern winger to accommodate me at this position, except one, my U17 coach. He stood in the middle ground. He was willing to change his tactics as he truly believed in my potential, but he also believed that any winger must at least be average in terms of speed. Thus, he made an agreement with me. If I could get my sprint time down by 20 %, he would most definitely play me on the wing. We agreed on the 10 meter sprint.

The day after our discussion, I got to work immediately. I needed someone to time me with a stopwatch while I sprint. The only person who I had consistent access to was my little brother. I went to the park with him, estimated a distance of 10 meters and marked it with yellow tape. I sprinted many times, and the timings I got were in the range of on average +- 0.3 seconds, which is a large margin of error for a 10 meter sprint. Human reaction time is around 0.2 seconds, which is unavoidable no matter who holds the stopwatch. A 20% cut on a roughly 2 second sprint is about 0.4 seconds. My measurement error was +-0.3 seconds. The stopwatch could not tell me whether I had succeeded. 

**What I had to work with**

Commercial timing gates cost around $200. I already had a starter kit with two ultrasonic sensors, an ESP32, resistors and jumper wires. I did not have IR emitters or receivers. Break-beam gates using IR would have been more accurate, but buying the parts and waiting for them to ship would have cost me weeks. Working with what I had, the total cost was about $30 against roughly $200 for a commercial system.

---------------
**Hardware**
Everything below was built and tested indoors on a desk, with the sensors about 30 cm from the cardboard instead of the 1.2 m they will be on a lane. All the parameters and results are for that setup. The numbers will change on the field, and the code learns the baseline at startup so it adapts on its own, but the threshold and the timing accuracy will both need retesting outdoors.
| Part | # | Notes |
|---|---|---|
| ESP32  | 1 | Freenove ESP32-WROOM, headers pre-soldered |
| HC-SR04 ultrasonic sensor | 3 | 2 gates + 1 profiler |
| 1 k ohm resistor | 3 | one per voltage divider |
| 2 k ohm resistor | 3 | one per voltage divider |
| Breadboard | 1 | from starter kit |
| Jumper wires | around 20 | from starter kit |
| Ethernet cable, 50 ft | 1 | cut into runs to each gate |
| Cardboard reflector panel | 2 | one per gate |
| Posts or cones | 4 | two per gate |

- Flat cardboard works better than a cone as a reflector. A curved surface scatters the burst, so the echo is weaker and dropouts are more frequent. 
- The profiler has no panel. It points down the lane at the runner's back, so the runner is the reflector.



Wiring(V1 - without profiler):

| Sensor | Trig | Echo (via divider) |
|---|---|---|
| Start gate | GPIO 25 | GPIO 32 |
| Finish gate | GPIO 26 | GPIO 33 |


<img width="771" height="574" alt="Screenshot 2026-09-02 at 2 17 23 PM" src="https://github.com/user-attachments/assets/f021c1fc-26c1-46c9-b8a4-562b98ce1249" />


**Circuit Diagram**

Vcc pin on the ultrasonic sensor was fairly easy, only needing to attach 5v of power into it.
<img width="438" height="516" alt="Screenshot 2026-09-02 at 2 14 24 PM" src="https://github.com/user-attachments/assets/1978ffe5-afd7-4a3b-97ea-23d8b8e01d8f" />

This is the way I attached every sensor. The sensor runs on 5 V, so its Echo pin sends back 5v. The ESP32 pins can only take 3.3V. Sending 5V into a pin damages it slowly, so the two resistors split the voltage and the ESP32 reads the point between them at 3.33V.

## How it works

### Detection
Each sensor pings across the lane at a cardboard panel. With the lane
empty the reading is steady, that is the baseline. When a runner
passes, the echo comes back short off their body, or does not come
back at all. Both count as blocked.

### Calibration
60 readings at startup, failed readings thrown away, median taken as
the baseline. Median not average, so one stray reading cannot drag it
off. 

### The three parameters

| Parameter | Value | What it does |
|---|---|---|
| THRESHOLD | 7 cm | how far off baseline counts as blocked (This number will also change when I get on the field) |
| CONFIRM | 2 | blocked readings in a row before triggering timer |
| LOCKOUT | 400 ms | gate ignores everything after firing |

### Timing
Both timestamps come from the same ESP32 clock, so there is no
syncing problem. Two wireless boards would each have their own
crystal and would need an NTP (Network Time Protocol) style exchange to agree.

---

## Measured performance

### How I measured it
Both sensors side by side, aimed at the same panel. Waved a piece of cardboard
through 30 times. In theory both should fire at the same instant, so
any difference is the device's own error with no running variation
mixed in.

### Results

I ran the test twice. Both runs used the same setup, panel about 30 cm
away.

| | Run 1 | Run 2 |
|---|---|---|
| Loop rate | 124 Hz | 125 Hz |
| Mean difference | -2.30 ms | -0.05 ms |
| Standard deviation | 9.35 ms | 5.70 ms |
| Range | -27 to +23 ms | -27 to +3 ms |
| Dropout rate | 2.2% | 2.4% |

In run 2, 29 of the 30 trials landed within +-3 ms. The standard
deviation of 5.70 ms is almost entirely caused by one outlier at
-26.65 ms. The mean of -0.05 ms means the two gates have no built in
bias, neither one is consistently faster.

The outliers are all about the same size because they happen when one
gate catches the cardboard a full loop pass later than the other. The
loop reads gate A, then gate B, then repeats, so if the cardboard
arrives right between two reads, one gate sees it now and the other
sees it on the next pass.

**Note on field conditions:** these numbers were measured with the
panel about 30 cm away. On the field the gap will be about 1.2 m, so
the sound has to travel four times further and each reading takes
longer. That slows the loop down, and since the loop speed is what
sets the timing error, the error will get bigger. I would guess
somewhere around 15 to 20 ms. That is still far better than a
stopwatch, so it does not change anything about the project, but I
will run the same test on the field to get the real number.

### Compared to a stopwatch

| Method | Error |
|---|---|
| Stopwatch | +-300 ms |
| This device | about +-6 ms |
| Improvement | about 50x |

My target was a 0.4 s improvement. At this precision that is easy to
detect. With a stopwatch it was not.

---

## Problems I hit

### Panel distance changed everything
At 12 cm the baseline was noisy and 33% of readings came back with no
echo. Since a missing echo counts as blocked, gates were firing on
nothing. Moving the panel to 30 cm dropped the dropout rate to 2.2%
and the false triggers stopped.

### THRESHOLD is not a fixed number
3 cm caused false triggers on a noisy baseline. This triggered the count variable to be raised for the first trial, making the timer for one of the gates (A or B) start before I even wave the cardboard.
Raised it to 7 cm and it worked. The right value depends on how much the baseline wobbles,
which depends on the setup.



---

## Version 2: adding the profiler

Why a total time is not enough:
 
The two gates give me one number: how long the 10 metres took. That is useful, but it does not tell me anything about how I ran it. Two players can have the exact same 10 metre time and get there in completely different ways. One explodes off the line and then slows down. The other starts slowly and keeps building the whole way.
 
My coach cares about the first few steps, because that is what matters for a winger. A total time hides exactly the part I need to see. So I added a third sensor to measure where I am during the run, not just when I cross the two lines.
 
How the profiler works:
 
The third sensor sits behind the start line, pointing down the lane at my back. I run away from it, so it is never in my path. While the timer is running, the sensor keeps measuring how far away I am. That gives me a list of positions with a timestamp on each one. From that list I can work out how fast I was moving at any point during the run, which the gates cannot do.
 
| | Gates | Profiler |
|---|---|---|
| What it gives | one time for the whole run | position all the way through |
| How reliable | very | noisier |
| Range needed | 1.2 m across the lane | up to 4 m down the lane |
 
Wiring (V2):
 
| Sensor | Trig | Echo (via divider) |
|---|---|---|
| Start gate | GPIO 25 | GPIO 32 |
| Finish gate | GPIO 26 | GPIO 33 |
| Profiler | GPIO 27 | GPIO 35 |

**V2 Image**
<img width="612" height="399" alt="Screenshot 2026-09-03 at 1 22 48 PM" src="https://github.com/user-attachments/assets/346de15f-6617-41b2-961d-42a95ad52425" />
 
GPIO 35 is input only on the ESP32. That is fine for Echo because I only ever read it, and it saves an output pin for something else later.
 
The profiler needs the same voltage divider as the gates. It does not need a cardboard panel though, because I am the reflector. PROFILER_OFFSET is how far the sensor sits behind the start line. The code subtracts it from every reading, so the numbers come out as distance from the start line instead of distance from the sensor.
 
How far the profiler can see:
 
I tested this before writing any code, by walking away from the sensor and watching where the readings stopped coming back. It reads reliably out to about 4 metres. After that the echo is too weak and I get nothing back at all.
 
That is not enough to cover a full 10 metre sprint, but it does cover the acceleration phase, which is the part I actually care about. So the design ended up being: profiler for the first few metres in detail, gates for the total time across all 10.
 
---------------
**Signal processing**
 
This is where the real work in V2 was, and it is not the part I expected to be hard.
 
Step 1 - fixing the sampling pattern:
 
The first thing I noticed when I plotted the raw position data was a sawtooth in it. It went up, down, up, down, every other point. That was not the sensor being bad. When I looked at the timestamps I saw they came in pairs about 7 ms apart, then a 23 ms gap, then another pair. So the profiler was being read twice in some loop passes and once in others, depending on what the finish gate was doing at the time.
 
Because the two types of reading happened under slightly different conditions, they gave slightly different distances, and that showed up as the sawtooth. I fixed it by adding a counter and only recording every second reading:
 
```python
i += 1
if i % 2 == 0 and len(log) < MAX_LOG:
```
 
That gave me evenly spaced samples at about 27 ms and the sawtooth disappeared. It also halves the amount of data I have to move off the board, which is a bonus.
 
Step 2 - the problem with turning position into speed:
 
Getting speed from position sounds easy. Take two positions, see how far apart they are, divide by the time between them. That is one line of code. The problem is what it does to the small errors in each reading.
 
Every position reading is off by a small amount, maybe half a centimetre. When two readings are taken very close together in time, the actual movement between them is also small. So the error stays the same size while the thing I am measuring gets smaller, and the error takes over. Then doing the same thing again to get acceleration makes it much worse, because now I am amplifying a number that is already noisy.
 
Here is what that looked like with no smoothing at all:
 
- Position: fine, a clear rising line
- Speed: mostly noise, jumping around way more than the real signal
- Acceleration: completely unusable, swinging between plus and minus 30
Those acceleration numbers were physically impossible for what I was actually moving. The sensor was not broken. This happens because of the maths, not the hardware, and a better sensor would have had the same problem.
 
Step 3 - smoothing:
 
The fix is to clean up the position readings before working out the speed. I used a moving average. Each point gets replaced by the average of itself and the points on either side of it. With a window of 5, point number 10 becomes the average of points 8, 9, 10, 11 and 12. The window slides along so every point gets its own average.
 
```python
smoothing_window_size = 5
smoothed_positions = []

for i in range(len(positions)):
    low_index = max(0, i - smoothing_window_size // 2)
    high_index = min(len(positions), i + smoothing_window_size // 2 + 1)

    smoothed_positions.append(
        sum(positions[low_index:high_index])
        / (high_index - low_index)
    )

```
 
This works because the errors are random. Sometimes a reading is a bit high, sometimes a bit low. Averaging several of them together lets those cancel out. The real movement is the same in all of them, so it survives.
 
One thing I want to be clear about is that a moving average does not delete a single bad reading. It spreads it out over the points around it, so the spike gets shorter and wider instead of disappearing. To actually get rid of single bad readings I would use a median filter, which takes the middle value instead of the average. That is the same reason I already use a median and not an average for the baseline during calibration.
 
Step 4 - choosing the window size:
 
The window size is a trade off and there is no single right answer. A small window keeps the curve sharp and reacting quickly, but it is still noisy. A large window gives a smooth curve, but it lags behind the real movement and flattens anything that happens fast. If my speed really does spike for a short moment and my window covers a longer stretch than that, the spike just disappears.
 
I tried a few sizes and compared them. With only about 22 points of data, a window of 15 would be averaging most of the run into every single point, so the curve came out almost featureless. A window of 5 kept the shape while removing most of the noise.
 
The way I decided was to check whether the smoothed curve still showed the features I could already see in the raw data. If smoothing removed something that was clearly real, the window was too big.



**Results**

Position: 
The position curve is smooth enough that the raw and smoothed lines almost sit on top of each other. The speed builds up to a peak of about 0.39 m/s around 0.5 seconds and then drops off, which is a real motion profile rather than noise.
Raw - 
<img width="633" height="536" alt="Screenshot 2026-09-03 at 1 05 43 PM" src="https://github.com/user-attachments/assets/59452665-163c-4066-9429-207ef4a5df6e" />

Smoothed - 
<img width="633" height="536" alt="Screenshot 2026-09-03 at 1 06 12 PM" src="https://github.com/user-attachments/assets/e84e0d67-a5b8-4455-9d5c-3355231e4d6f" />

Velocity: 
The speed curve shows a clear shape: it builds from about 0.06 m/s up to a peak of 0.39 m/s around 0.5 seconds, then drops off. That is a real motion profile, not noise.
<img width="633" height="536" alt="Screenshot 2026-09-03 at 1 08 32 PM" src="https://github.com/user-attachments/assets/30ec6e41-45da-4d82-8d05-a54bc7f98553" />

Acceleration: 
The acceleration curve is still noisy, swinging between about plus and minus 5. It is readable but not clean. This is the part that would improve most from smoothing the speed before working out acceleration, which is the next thing I would change.
<img width="633" height="536" alt="Screenshot 2026-09-03 at 1 09 39 PM" src="https://github.com/user-attachments/assets/43d91789-f80f-4741-a15c-bb475fe71b95" />


The two curves agree with each other, which is a good check. The speed peaks at around 0.5 seconds, and the acceleration crosses from positive to negative right around the same point. That is what should happen physically, so the processing is not producing nonsense.

**What I would do differently**
 
Smooth the speed as well. Right now I smooth the position and then work out speed and acceleration from it. Smoothing the speed before working out acceleration would give a cleaner acceleration curve.
 
Cut the data where the sensor loses me. Near the end of my runs the same value kept repeating, which means the sensor had locked onto something behind me instead of me. That part of the data is not valid and should be removed before processing.
 
Try a median filter instead of a moving average and compare the two properly, instead of assuming the moving average is the right choice.


**Conclusion**
 
I set out to build something that could time a 10 metre sprint well enough to tell me if I was actually getting faster. The stopwatch could not do that, because its error was almost as big as the improvement I was going for.
 
The two gates do the job. When I tested them side by side, the spread was about 6 ms, compared to around 300 ms for a stopwatch. That is roughly 50 times better. A 0.4 second improvement is way bigger than that, so now I can tell a real change from a bad run.
 
The profiler goes further. Instead of one number for the whole sprint, it gives me a speed curve for the first few metres, which is the part my coach cares about. A stopwatch cannot do that at all.
 
The whole thing cost about $30, compared to roughly $200 for a system I could have just bought.
 
**What I actually learned**
 
Most of the hard parts were not where I thought they would be.
 
The hardware was the easy half. Three sensors, three voltage dividers, a breadboard, and some wires. What actually took the time was everything after that.
 
The hardest part by far was the signal processing, which is just a name for cleaning up messy data before you use it.Every reading is off by a small amount, and on its own that does not matter much. But when I tried to turn position into speed, those small errors got much bigger, and when I did it again to get acceleration they took over completely. My first acceleration graph was swinging between plus and minus 30, which is impossible for what I was actually moving. Nothing was broken. It just happens because of how the maths works.
 
Fixing that meant learning about smoothing, and that there is no perfect setting. A small window leaves the graph noisy. A big window makes it smooth but flattens out things that are real. I had to try different sizes and compare them, and pick the one that cleaned things up without deleting anything that mattered. I also learned that a moving average does not remove a single bad reading, it just spreads it out, which is not what I assumed at first.
 
The other thing I learned is that measuring your own device matters as much as building it. Before I ran the side by side test I had no idea if my timer was good to 5 ms or 500 ms. Without that number I could not honestly say it was better than a stopwatch. Building something is not the same as knowing what it does.
 
**Version 3**
 
The main limit right now is the ultrasonic sensor. Every reading has to wait for the sound to go out and come back, and that waiting is what causes most of my timing error. An infrared beam does not wait, so it would fire almost instantly and make the timing much more accurate. I would also go wireless so there are no cables across the field, but that brings back the problem of two boards having two clocks that do not agree.

