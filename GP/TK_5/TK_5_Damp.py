import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

# Kleines aber feines Programm zur Darstellung eines Fadenpendels.Es kann auch eine Dämpfung eingestellt werden. Mit den Einstellungen ist es auch möglich den aperiodischen Grenzfall darzustellen.
# Die "Aufhängung" des Pendels befindet sich bei (0,0)
# De Berechnungen sind alle mit der klein WInkelnäherung. Wer kennt ihn nicht? Den besonders kleinen Winkel von 90°
# Anmerkungen, Kommentare, Verbesserungen sind gewünscht.

# Konstanten
g = 9.81  # Erdbeschleunigung sollten wir uns auf den Jupiter befinden, dann bitte hier ändern
t_max = 20
fps = 60
t = np.linspace(0, t_max, int(t_max * fps))

# Anfangswerte
init_length = 1.0
init_theta = np.radians(20)
init_gamma = 0.0

# Steuerungsvariable für Pause
is_paused = False


# Dämpfungs-Schwingung
def theta_damped(theta0, L, gamma):
    omega0 = np.sqrt(g / L)
    omega_d = np.sqrt(np.maximum(omega0**2 - gamma**2, 0))
    return theta0 * np.exp(-gamma * t) * np.cos(omega_d * t)


# Set up figure and axes
fig, (ax_pendulum, ax_theta) = plt.subplots(1, 2, figsize=(12, 6))
plt.subplots_adjust(bottom=0.25)

# Achse 1: Pendel
ax_pendulum.set_xlim(-1.2, 1.2)
ax_pendulum.set_ylim(-1.2, 0.2)
ax_pendulum.set_aspect("equal")
ax_pendulum.set_title("Fadenpendel")

(line_pendulum,) = ax_pendulum.plot([], [], "o-", lw=2)
arrow_force = ax_pendulum.arrow(0, 0, 0, 0, head_width=0.05, color="r")

# Achse 2: Winkelverlauf
ax_theta.set_xlim(0, t_max)
ax_theta.set_ylim(-1.1 * init_theta, 1.1 * init_theta)
ax_theta.set_title("Auslenkung & Dämpfung")
ax_theta.set_xlabel("Zeit [s]")
ax_theta.set_ylabel("Winkel [rad]")
(line_theta,) = ax_theta.plot([], [], lw=2)
(envelope_upper,) = ax_theta.plot([], [], "r--", alpha=0.5)
(envelope_lower,) = ax_theta.plot([], [], "r--", alpha=0.5)

# Sliders
axcolor = "lightgoldenrodyellow"
ax_length = plt.axes([0.25, 0.18, 0.65, 0.03], facecolor=axcolor)
ax_theta0 = plt.axes([0.25, 0.13, 0.65, 0.03], facecolor=axcolor)
ax_gamma = plt.axes([0.25, 0.08, 0.65, 0.03], facecolor=axcolor)

slider_length = Slider(ax_length, "Länge [m]", 0.1, 2.0, valinit=init_length)
slider_theta0 = Slider(
    ax_theta0, "Startwinkel [°]", 0, 90, valinit=np.degrees(init_theta)
)
slider_gamma = Slider(ax_gamma, "Dämpfung " r"$\gamma$", 0.0, 1.5, valinit=init_gamma)

# Pause-Button
ax_button = plt.axes([0.8, 0.02, 0.1, 0.04])
button = Button(ax_button, "Pause", color=axcolor, hovercolor="lightblue")


def toggle_pause(event):
    global is_paused
    is_paused = not is_paused
    button.label.set_text("Play" if is_paused else "Pause")


button.on_clicked(toggle_pause)


# Update-Funktion für die Animation
def update(frame):
    global arrow_force
    if is_paused:
        return line_pendulum, line_theta, arrow_force, envelope_upper, envelope_lower

    L = slider_length.val
    theta0 = np.radians(slider_theta0.val)
    gamma = slider_gamma.val

    theta = theta_damped(theta0, L, gamma)

    # Pendel-Position
    x = L * np.sin(theta[frame])
    y = -L * np.cos(theta[frame])
    line_pendulum.set_data([0, x], [0, y])

    # Rückstellkraft als Pfeil (F_r =  -m·g·sin(θ), hier proportional)
    force_mag = -np.sin(theta[frame])
    scale = 0.2 * L

    # Alten Pfeil entfernen, damit es wie eine flüssige Animation aussieht
    arrow_force.remove()

    # Neuen Pfeil zeichnen
    arrow_force = ax_pendulum.arrow(
        x,
        y,
        force_mag * scale * np.cos(theta[frame]),
        force_mag * scale * np.sin(theta[frame]),
        head_width=0.05 * L,
        color="red",
    )

    # Zeitdiagramm
    line_theta.set_data(t[:frame], theta[:frame])
    envelope = theta0 * np.exp(-gamma * t[:frame])
    envelope_upper.set_data(t[:frame], envelope)
    envelope_lower.set_data(t[:frame], -envelope)

    # Achsen automatisch anpassen
    ax_theta.set_ylim(-1.1 * theta0, 1.1 * theta0)
    ax_pendulum.set_xlim(-L - 0.2, L + 0.2)
    ax_pendulum.set_ylim(-L - 0.2, 0.2)

    return line_pendulum, line_theta, arrow_force, envelope_upper, envelope_lower


ani = FuncAnimation(fig, update, frames=len(t), interval=1000 / fps, blit=True)
plt.show()
