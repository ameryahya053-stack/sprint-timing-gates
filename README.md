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

| | Value |
|---|---|
| Loop rate | 124 Hz |
| Mean difference | -2.30 ms |
| Standard deviation | 9.35 ms |
| Range | -27 to +23 ms |
| Dropout rate | 2.2% |

NOTE
This 9.35 ms was measured with the panel about 30 cm away. On the field the gap will be about 1.2 m, so the sound has to travel four times further and each reading takes longer. That slows the loop down, and since the loop speed is what sets the timing error, the error will get bigger. I would guess somewhere around 15 to 20 ms instead of 9. That is still far better than a stopwatch, so it does not change anything about the project.

### Compared to a stopwatch

| Method | Error |
|---|---|
| Stopwatch | +-300 ms |
| This device | +-9 ms |
| Improvement | about 32x |

My target was a 0.4 s improvement. At +-9 ms that is easy to detect.
With a stopwatch it was not.

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

## Version 2: adding the profiler + Ethernet wiring for outdoor testing






