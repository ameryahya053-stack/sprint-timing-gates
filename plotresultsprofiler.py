import matplotlib.pyplot as plt

data = """
P,27.2,2.5
P,54.0,1.6
P,80.9,3.0
P,107.8,3.0
P,134.7,4.0
P,161.7,4.4
P,188.7,4.4
P,215.7,4.4
P,242.7,6.0
P,269.8,6.0
P,296.8,6.5
P,323.9,6.5
P,351.1,7.4
P,378.2,8.4
P,405.5,9.3
P,432.8,9.8
P,460.1,10.8
P,487.4,10.7
P,514.9,13.4
P,542.4,14.2
P,569.9,15.2
P,597.5,14.2
P,625.0,14.8
P,652.6,15.7
P,680.2,15.2
P,707.8,15.6
P,735.3,15.2
P,763.0,15.6
P,790.6,16.6
P,818.4,18.5
P,846.1,18.0
"""

time_points = []
positions = []

for line in data.strip().split("\n"):
    if line.startswith("P,"):
        parts = line.split(",")
        time_points.append(float(parts[1]) / 1000)   # ms to s
        positions.append(float(parts[2]) / 100)      # cm to m

plt.figure()
plt.plot(time_points, positions, marker=".")
plt.xlabel("Time (s)")
plt.ylabel("Position (m)")
plt.title("Position")
plt.grid(True)

smoothing_window_size = 5
smoothed_positions = []

for i in range(len(positions)):
    low_index = max(0, i - smoothing_window_size // 2)
    high_index = min(len(positions), i + smoothing_window_size // 2 + 1)

    smoothed_positions.append(
        sum(positions[low_index:high_index])
        / (high_index - low_index)
    )

plt.figure()
plt.plot(time_points, positions, alpha=0.3, label="raw")
plt.plot(time_points, smoothed_positions, label="smoothed")
plt.xlabel("Time (s)")
plt.ylabel("Position (m)")
plt.title("Position, smoothed")
plt.legend()
plt.grid(True)

velocity_times = []
velocities = []

for i in range(1, len(smoothed_positions)):
    time_change = (
        time_points[i]
        - time_points[i - 1]
    )

    if time_change > 0:
        velocity_times.append(time_points[i])

        position_change = (
            smoothed_positions[i]
            - smoothed_positions[i - 1]
        )

        velocities.append(
            position_change / time_change
        )

plt.figure()
plt.plot(velocity_times, velocities)
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.title("Velocity")
plt.grid(True)

acceleration_times = []
accelerations = []

for i in range(1, len(velocities)):
    time_change = (
        velocity_times[i]
        - velocity_times[i - 1]
    )

    if time_change > 0:
        acceleration_times.append(
            velocity_times[i]
        )

        velocity_change = (
            velocities[i]
            - velocities[i - 1]
        )

        accelerations.append(
            velocity_change / time_change
        )

plt.figure()
plt.plot(acceleration_times, accelerations)
plt.xlabel("Time (s)")
plt.ylabel("Acceleration (m/s²)")
plt.title("Acceleration")
plt.grid(True)

plt.show()