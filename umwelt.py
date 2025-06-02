import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.spatial import cKDTree
from scipy.interpolate import splprep, splev

# Universal Parameter
N = 50
VISIBLE = N
v0_mean = 3.0
tau = 470
delta_kappa = 340
D_omega = (v0_mean * delta_kappa) ** 2 / tau # falls etwas getestet werden soll, könnte man hier auch 0.05 schreiben. Ob das aber sooo sinnvoll  ist.....
dt = 0.5  # Zeitschritt
domain_size = 100
n_segments = 30
filament_length = 15
segment_length = filament_length / n_segments

# Sliding Parameter 
## Hier ist vermutlich sehr viel falsch bzw. basiert auf Annahmen ####
SLIDE_PROBABILITY = 0.04
SLIDE_DISTANCE = 3.0
SLIDE_VELOCITY = 1.5
ANGLE_PARALLEL_THRESHOLD = np.pi / 4
ANGLE_ANTIPARALLEL_THRESHOLD = 3 * np.pi / 4

class Filament:
    def __init__(self):
        self.v = v0_mean
        self.theta = np.random.uniform(0, 2 * np.pi)
        self.polarity = 1
        self.reversal_rate = 0.01
        dx, dy = np.cos(self.theta), np.sin(self.theta)
        margin = filament_length + 5
        start = np.random.rand(2) * (domain_size - 2 * margin) + margin

        self.points = np.array([
            start - i * segment_length * np.array([dx, dy])
            for i in range(n_segments)
        ])

        self.is_stuck = False
        self.stuck_to = None
        self.stuck_direction = 0

    #### No short cuts für  den Speed run #######
    def reflect_if_out_of_bounds(self):
        x, y = self.points[0]
        if x < 0:
            x = 0
            self.theta = np.pi - self.theta
        elif x > domain_size:
            x = domain_size
            self.theta = np.pi - self.theta
        if y < 0:
            y = 0
            self.theta = -self.theta
        elif y > domain_size:
            y = domain_size
            self.theta = -self.theta
        self.theta %= 2 * np.pi
        self.points[0] = np.array([x, y])
    
    #####  BEWEGUNG der Spaghetti. Hier wird auch geregelt, dass die Spaghetti nicht den Kochtopf verlässt ######
    def update(self, alignment_force=0, slide_velocity=np.array([0.0, 0.0])):
        if np.random.rand() < self.reversal_rate * dt:
            self.polarity *= -1

        noise = np.sqrt(2 * D_omega * dt) * np.random.normal()
        self.theta += noise - 0.02 * alignment_force
        self.theta %= 2 * np.pi

        move_dir = np.array([np.cos(self.theta), np.sin(self.theta)])
        speed = self.v  # konstante Geschwindigkeit
        self.points[0] += (speed * self.polarity * move_dir + slide_velocity) * dt

        for i in range(1, n_segments):
            vec = self.points[i] - self.points[i - 1]
            dist = np.linalg.norm(vec)
            if dist > 1e-8:
                diff = (dist - segment_length) / dist * vec
                self.points[i] -= 0.5 * diff

        self.reflect_if_out_of_bounds()

### S = cos(2\theta) #####
def compute_global_nematic_order(filaments):
    thetas = np.array([f.theta for f in filaments])
    return np.mean(np.cos(2 * thetas))

def unwrap_and_plot(points, box_size):
    points = np.copy(points)
    for i in range(1, len(points)):
        delta = points[i] - points[i - 1]
        delta = (delta + box_size / 2) % box_size - box_size / 2
        points[i] = points[i - 1] + delta
    return points

#### Beauty and the beast ##### no but for real I just want something beautiful
def smooth_points(points, smoothness=0):
    x, y = points[:, 0], points[:, 1]
    tck, u = splprep([x, y], s=smoothness)
    unew = np.linspace(0, 1, 100)
    out = splev(unew, tck)
    return np.vstack(out).T

filaments = [Filament() for _ in range(N)]


##### alles für den Plot #######
fig, ax = plt.subplots()
ax.set_xlim(0, domain_size)
ax.set_ylim(0, domain_size)
ax.set_aspect("equal")
ax.set_title("Simulation aktiver Filamente mit Sliding-Geschwindigkeitsänderung")

lines = [ax.plot([], [], lw=2, alpha=0.4)[0] for _ in range(VISIBLE)]
text = ax.text(5, 5, "", color="red")

def calculate_slide_velocity(filament, neighbors):
    slide_velocity = np.array([0.0, 0.0])

    if filament.is_stuck:
        other = filament.stuck_to
        direction = filament.stuck_direction
        move_dir = np.array([np.cos(other.theta), np.sin(other.theta)])
        return direction * SLIDE_VELOCITY * move_dir

    for other in neighbors:
        if other is filament:
            continue

        vec = other.points[0] - filament.points[0]
        dist = np.linalg.norm(vec)
        if dist > SLIDE_DISTANCE:
            continue

        if np.random.rand() < SLIDE_PROBABILITY:
            theta1 = filament.theta % (2 * np.pi)
            theta2 = other.theta % (2 * np.pi)
            dtheta = abs((theta1 - theta2 + np.pi) % (2 * np.pi) - np.pi)

            if dtheta < ANGLE_PARALLEL_THRESHOLD:
                direction = 1
            elif dtheta > ANGLE_ANTIPARALLEL_THRESHOLD:
                direction = -1
            else:
                continue

            filament.is_stuck = True
            filament.stuck_to = other
            filament.stuck_direction = direction
            move_dir = np.array([np.cos(other.theta), np.sin(other.theta)])
            slide_velocity += direction * SLIDE_VELOCITY * move_dir
            break

    return slide_velocity


#### Lebwoh-Lasher-Potential    #######
def lebwohl_lasher_force(theta_i, neighbors_theta):
    if len(neighbors_theta) == 0:
        return 0.0
    diffs = theta_i - neighbors_theta
    return 2 * np.mean(np.sin(2 * diffs))


#### Update Schleife ####### check: Lebwohl, slide, checking for neighbors
def update(frame):
    positions = np.array([f.points[0] for f in filaments])
    tree = cKDTree(positions)

    alignment_strength = 0.02

    for f in filaments:
        neighbors_idx = tree.query_ball_point(f.points[0], r=SLIDE_DISTANCE)
        neighbors = [filaments[i] for i in neighbors_idx if i != filaments.index(f)]

        neighbors_theta = np.array([n.theta for n in neighbors])
        alignment_force = lebwohl_lasher_force(f.theta, neighbors_theta)
        alignment = -alignment_strength * alignment_force

        slide_velocity = calculate_slide_velocity(f, neighbors)
        f.update(alignment_force=alignment, slide_velocity=slide_velocity)

    if frame % 2 == 0:
        S = compute_global_nematic_order(filaments)
        text.set_text(f"Nemat. Ordnung S = {S:.2f}")

    for i, f in enumerate(filaments[:VISIBLE]):
        pts = unwrap_and_plot(f.points, domain_size)
        smooth_pts = smooth_points(pts, smoothness=1)
        x, y = smooth_pts[:, 0], smooth_pts[:, 1]
        color = (0.0, 0.6, 0.0, 0.4)
        lines[i].set_data(x, y)
        lines[i].set_color(color)

    return lines + [text]

ani = FuncAnimation(fig, update, frames=500, interval=30, blit=True)
plt.show()
