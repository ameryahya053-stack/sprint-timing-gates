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
| 1 k ohm resistor | 9 | three per voltage divider |
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


![IMG_0893](https://github.com/user-attachments/assets/5257f855-8485-4c8a-8673-a5fc6f44eb65)




