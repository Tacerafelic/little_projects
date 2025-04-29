import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation


# Dient nur zur Veranschaulichung. Strenggenommen fehlen hier noch ein paar sahcen, wie die Wellenlänge, Temperatur, etc.
# Aber I guess it is fine...


# Parameter
x_vals = np.linspace(0, 10, 500)
initial_probe_start = 3
initial_probe_length = 4
initial_total_rotation = 90
initial_rotation_direction = (
    1  # 1 = rechts, -1 = links aber jetzt anders gelöst mit winkel [-180, 180]
)
current_angle = 0
konzentration = 1

is_paused = False
# Plot Setup
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(0, 10)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(-1.5, 1.5)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.set_title("Optische Aktivität")

# Vektor
vector = ax.quiver(0, 0, 0, 1, 0, 0, color="orange", length=1, normalize=True)


# Sliders
axcolor = "lightgoldenrodyellow"
ax_probe_start = plt.axes([0.2, 0.025, 0.65, 0.02], facecolor=axcolor)
ax_probe_length = plt.axes([0.2, 0.05, 0.65, 0.02], facecolor=axcolor)
ax_rotation = plt.axes([0.2, 0.075, 0.65, 0.02], facecolor=axcolor)
# ax_direction = plt.axes([0.2, 0.1, 0.3, 0.02], facecolor=axcolor)
ax_konzentration = plt.axes([0.2, 0.1, 0.3, 0.02], facecolor=axcolor)

slider_probe_start = Slider(
    ax_probe_start, "Probe-Start", 0, 8, valinit=initial_probe_start
)
slider_probe_length = Slider(
    ax_probe_length, "Länge der Probe", 0.5, 8, valinit=initial_probe_length
)
slider_rotation = Slider(
    ax_rotation, "Drehvermögen (°)", -180, 180, valinit=initial_total_rotation
)

slider_konzentration = Slider(
    ax_konzentration, "Konzentration", 0, 1, valinit=konzentration
)
# slider_direction = Slider(
#     ax_direction,
#     "Richtung (L=-1, R=1)",
#     -1,
#     1,
#     valinit=initial_rotation_direction,
#     valstep=2,
# )

probe_area = ax.bar3d(
    initial_probe_start,  # x-Start
    -1.5,  # y-Start
    -1.5,  # z-Start
    initial_probe_length,  # Breite entlang x
    3,  # Breite entlang y
    3,  # Breite entlang z
    color="cyan",
    alpha=0.3,
    zsort="min",
)


ax_button = plt.axes([0.1, 0.6, 0.1, 0.04])
button = Button(ax_button, "Pause", color=axcolor, hovercolor="lightblue")


def toggle_pause(event):
    global is_paused
    is_paused = not is_paused
    button.label.set_text("Play" if is_paused else "Pause")


button.on_clicked(toggle_pause)


# Update Funktion
def update(frame):
    global vector, current_angle, probe_area
    if is_paused:
        return probe_area, vector

    # nötig für updates/animation
    vector.remove()
    probe_area.remove()

    probe_start = slider_probe_start.val
    probe_length = slider_probe_length.val
    total_rotation_deg = slider_rotation.val
    # direction = slider_direction.val
    konzentration = slider_konzentration.val

    x_pos = (frame * 0.05) % 10

    if x_pos < 0.05:
        current_angle = 0

    if probe_start <= x_pos <= (probe_start + probe_length):
        progress = (x_pos - probe_start) / probe_length
        current_angle = (
            np.deg2rad(total_rotation_deg * konzentration * probe_length) * progress
        )
        color = "red"
    else:
        color = "orange"

    u = 0
    v = -np.sin(current_angle)
    w = np.cos(current_angle)

    vector = ax.quiver(x_pos, 0, 0, u, v, w, color=color, length=1, normalize=True)

    # Neuen Probenbereich einfügen
    probe_area = ax.bar3d(
        probe_start,
        -1.5,
        -1.5,
        probe_length,
        3,
        3,
        color="cyan",
        alpha=0.5 * konzentration,
        zsort="min",
    )

    ax.set_title(
        f"Optische Aktivität – Aktueller Winkel: {np.rad2deg(current_angle):.1f}°"
    )


ani = FuncAnimation(fig, update, frames=np.arange(0, 400), interval=30, blit=False)

plt.subplots_adjust(bottom=0.3)
plt.show()
