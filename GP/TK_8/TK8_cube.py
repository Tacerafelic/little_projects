import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.widgets import Slider


# CUBE (entertainment)
def draw_box(ax, center, size_xyz, color="blue", alpha=0.3):
    # Variablen
    cx, cy, cz = center
    sx, sy, sz = size_xyz[0] / 2, size_xyz[1] / 2, size_xyz[2] / 2

    vertices = np.array(
        [
            [cx - sx, cy - sy, cz - sz],
            [cx + sx, cy - sy, cz - sz],
            [cx + sx, cy + sy, cz - sz],
            [cx - sx, cy + sy, cz - sz],
            [cx - sx, cy - sy, cz + sz],
            [cx + sx, cy - sy, cz + sz],
            [cx + sx, cy + sy, cz + sz],
            [cx - sx, cy + sy, cz + sz],
        ]
    )

    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[4], vertices[7], vertices[3], vertices[0]],
    ]

    return Poly3DCollection(faces, alpha=alpha, facecolor=color, edgecolor="k")


# Initialisierung
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_zlim(0, 1)

# Großer Würfel
big_cube = draw_box(
    ax, center=(0.5, 0.5, 0.5), size_xyz=(1.0, 1.0, 1.0), color="lightgrey", alpha=0.4
)
ax.add_collection3d(big_cube)

# itty bitty teeny tiny litle  Würfel
small_center = [0.5, 0.5, 0.5]
small_size_xyz = [0.3, 0.3, 0.3]

# Kleiner Würfel initial zeichnen
small_cube_artist = draw_box(
    ax, center=small_center, size_xyz=small_size_xyz, color="red", alpha=0.6
)
ax.add_collection3d(small_cube_artist)
ax.set_title(f"Kleiner Quader: Volumen = {np.prod(small_size_xyz):.4f}", fontsize=14)

# Slider-Achsen
slider_axes = {
    "x": plt.axes([0.25, 0.00, 0.5, 0.02]),
    "y": plt.axes([0.25, 0.025, 0.5, 0.02]),
    "z": plt.axes([0.25, 0.05, 0.5, 0.02]),
    "sx": plt.axes([0.25, 0.075, 0.5, 0.02]),
    "sy": plt.axes([0.25, 0.1, 0.5, 0.02]),
    "sz": plt.axes([0.25, 0.125, 0.5, 0.02]),
}

# Slider-Objekte
sliders = {
    "x": Slider(slider_axes["x"], r"$x_{pos}$", 0.0, 1.0, valinit=small_center[0]),
    "y": Slider(slider_axes["y"], r"$y_{pos}$", 0.0, 1.0, valinit=small_center[1]),
    "z": Slider(slider_axes["z"], r"$z_{pos}$", 0.0, 1.0, valinit=small_center[2]),
    "sx": Slider(
        slider_axes["sx"], r"$x_{width}$", 0.05, 1.0, valinit=small_size_xyz[0]
    ),
    "sy": Slider(
        slider_axes["sy"], r"$y_{width}$", 0.05, 1.0, valinit=small_size_xyz[1]
    ),
    "sz": Slider(
        slider_axes["sz"], r"$z_{width}$", 0.05, 1.0, valinit=small_size_xyz[2]
    ),
}


def update(val):
    global small_cube_artist
    small_cube_artist.remove()

    # Neue Position und Größe
    cx, cy, cz = sliders["x"].val, sliders["y"].val, sliders["z"].val
    sx, sy, sz = sliders["sx"].val, sliders["sy"].val, sliders["sz"].val

    # Begrenzung
    cx = np.clip(cx, sx / 2, 1 - sx / 2)
    cy = np.clip(cy, sy / 2, 1 - sy / 2)
    cz = np.clip(cz, sz / 2, 1 - sz / 2)

    sliders["x"].set_val(cx)
    sliders["y"].set_val(cy)
    sliders["z"].set_val(cz)

    # Neuer Würfel
    small_cube_artist = draw_box(
        ax, center=[cx, cy, cz], size_xyz=[sx, sy, sz], color="red", alpha=0.6
    )
    ax.add_collection3d(small_cube_artist)
    ax.set_title(f"Kleiner Quader: Volumen = {sx * sy * sz:.4f}", fontsize=14)

    fig.canvas.draw_idle()


# Sliders mit Update verbinden
for s in sliders.values():
    s.on_changed(update)

plt.show()
