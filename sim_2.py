import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

# Simulationsparameter
v0_mean = 3.0
tau = 470
delta_kappa = 340
D_omega = (v0_mean * delta_kappa) ** 2 / tau
dt = 0.2
domain_size = 100  # µm
n_segments = 30
filament_length = 15
segment_length = filament_length / n_segments

# Sliding-Parameter
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

    def update(self, alignment_force=0, slide_velocity=np.array([0.0, 0.0])):
        if np.random.rand() < self.reversal_rate * dt:
            self.polarity *= -1
        noise = np.sqrt(2 * D_omega * dt) * np.random.normal()
        self.theta += noise + alignment_force
        self.theta %= 2 * np.pi

        move_dir = np.array([np.cos(self.theta), np.sin(self.theta)])
        speed = self.v
        self.points[0] += (speed * self.polarity * move_dir + slide_velocity) * dt

        for i in range(1, n_segments):
            vec = self.points[i] - self.points[i - 1]
            dist = np.linalg.norm(vec)
            if dist > 1e-8:
                diff = (dist - segment_length) / dist * vec
                self.points[i] -= 0.5 * diff

        self.reflect_if_out_of_bounds()


def lebwohl_lasher_force(theta_i, neighbors_theta):
    if len(neighbors_theta) == 0:
        return 0.0
    diffs = theta_i - neighbors_theta
    return 2 * np.mean(np.sin(2 * diffs))


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
            return direction * SLIDE_VELOCITY * move_dir
    return slide_velocity


def compute_blockwise_nematic_order(filaments, l=10):
    thetas = np.array([f.theta for f in filaments])
    positions = np.array([f.points[0] for f in filaments])
    n_blocks = int(domain_size // l)
    S_blocks = []

    for i in range(n_blocks):
        for j in range(n_blocks):
            x_min, x_max = i * l, (i + 1) * l
            y_min, y_max = j * l, (j + 1) * l
            in_block = np.where(
                (positions[:, 0] >= x_min) & (positions[:, 0] < x_max) &
                (positions[:, 1] >= y_min) & (positions[:, 1] < y_max)
            )[0]
            if len(in_block) > 1:
                block_thetas = thetas[in_block]
                cos2 = np.cos(2 * block_thetas)
                sin2 = np.sin(2 * block_thetas)
                mean_cos = np.mean(cos2)
                mean_sin = np.mean(sin2)
                S_block = np.sqrt(mean_cos ** 2 + mean_sin ** 2)
                S_blocks.append(S_block)

    return np.mean(S_blocks) if S_blocks else 0.0


# def plot_order_vs_density(N_values, steps=1000, block_size=10):
#     S_means = []
#     densities = []

#     for N in N_values:
#         print(f"Simuliere N = {N}")
#         filaments = [Filament() for _ in range(N)]

#         for frame in range(steps):
#             positions = np.array([f.points[0] for f in filaments])
#             tree = cKDTree(positions)
#             for f in filaments:
#                 neighbors_idx = tree.query_ball_point(f.points[0], r=SLIDE_DISTANCE)
#                 neighbors = [filaments[i] for i in neighbors_idx if i != filaments.index(f)]
#                 neighbors_theta = np.array([n.theta for n in neighbors])
#                 alignment_force = -0.02 * lebwohl_lasher_force(f.theta, neighbors_theta)
#                 slide_velocity = calculate_slide_velocity(f, neighbors)
#                 f.update(alignment_force=alignment_force, slide_velocity=slide_velocity)

#         S_mean = compute_blockwise_nematic_order(filaments, l=block_size)
#         area_mm2 = (domain_size / 1000) ** 2  # µm² → mm²
#         rho = N / area_mm2
#         densities.append(rho)
#         S_means.append(S_mean)

#     # Sortieren nach Dichte
#     sorted_pairs = sorted(zip(densities, S_means))
#     densities, S_means = zip(*sorted_pairs)

#     # Plot
#     plt.figure(figsize=(8, 5))
#     plt.plot(densities, S_means, 'o-', color='darkgreen')
#     plt.xlabel("Dichte ρ [Filamente / mm²]")
#     plt.ylabel("⟨S⟩ (Block-Durchschnitt)")
#     plt.title("Ordnungsübergang in Abhängigkeit von der Dichte")
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()

def plot_order_vs_density(N_values, steps=1000, block_size=10, repeats=5):
    densities = []
    S_means = []
    S_stds = []

    for N in N_values:
        print(f"Simuliere N = {N} ({repeats} Wiederholungen)...")
        S_repeat = []

        for rep in range(repeats):
            filaments = [Filament() for _ in range(N)]

            for frame in range(steps):
                positions = np.array([f.points[0] for f in filaments])
                tree = cKDTree(positions)
                for f in filaments:
                    neighbors_idx = tree.query_ball_point(f.points[0], r=SLIDE_DISTANCE)
                    neighbors = [filaments[i] for i in neighbors_idx if i != filaments.index(f)]
                    neighbors_theta = np.array([n.theta for n in neighbors])
                    # alignment_force = -0.02 * lebwohl_lasher_force(f.theta, neighbors_theta)
                    alignment_strength = 0.02
                    alignment_raw = lebwohl_lasher_force(f.theta, neighbors_theta)
                    alignment_force = alignment_strength * alignment_raw
                    slide_velocity = calculate_slide_velocity(f, neighbors)
                    f.update(alignment_force=alignment_force, slide_velocity=slide_velocity)

            S_mean = compute_blockwise_nematic_order(filaments, l=block_size)
            S_repeat.append(S_mean)

        # Dichte berechnen (gleich für alle Wiederholungen)
        area_mm2 = (domain_size / 1000) ** 2
        rho = N / area_mm2
        densities.append(rho)
        S_means.append(np.mean(S_repeat))
        S_stds.append(np.std(S_repeat))

    # Sortieren nach Dichte
    sorted_data = sorted(zip(densities, S_means, S_stds))
    densities, S_means, S_stds = zip(*sorted_data)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.errorbar(densities, S_means, yerr=S_stds, fmt='o-', capsize=5, color='darkgreen', ecolor='gray')
    plt.xlabel("Dichte ρ [Filamente / mm²]")
    plt.ylabel("⟨S⟩ (Block-Durchschnitt)")
    plt.title(f"Ordnungsübergang mit Wiederholungen (n={repeats})")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


N_values = [50, 100, 150, 200, 250, 300, 400, 500]
plot_order_vs_density(N_values=N_values, steps=1000, block_size=10)
