import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button


# Im folgenden Code werden die Zylinderkoordinaten visualisiert. Bisher können phi und r variiert werden. Z kann auch varriert werden, allerdings wird auch hier der Referenzzylinder bewegt ( nervt mich meh )
# tbh. Einheiten fehlen auch.... Das Volumen ist deshalb nur eine Zahl....
# Sollte aber trotzdem für den anfang reichen.


def format_phi(phi):
    fraction = phi / np.pi
    if np.isclose(fraction, round(fraction)):
        return r"{}\pi".format(int(round(fraction)))
    else:
        return r"{:.2f}\pi".format(fraction)


def plot_cylinder_with_segment(ax, r_center, r_width, phi_max, z_max):
    ax.clear()

    # Params fix. Weil sind eh schon zuviele sachen. könnte überfordern, wenn man jetzt auch noch z einstellen könnte
    # z_max = 1.0
    R_outer = 1.0

    # Begrenzung der Breite. Ansonsten wächst ds segement über den Zylinder hinaus.
    r_width = min(r_width, 2 * min(r_center, R_outer - r_center))

    # Min- und Max-Radien des Segments
    r_min = r_center - r_width / 2
    r_max = r_center + r_width / 2

    # Volumenberechnung
    volume = 0.5 * (r_max**2 - r_min**2) * phi_max * z_max

    # Titel hier wird auch das Volumen und der phi wert angezeigt
    ax.set_title(
        f"Zylindersegment\nVolumen = {volume:.4f}",  # (φ = {phi_max/np.pi:.2f}π)",
        fontsize=12,
    )

    # Auflösung
    resolution = 50
    phi = np.linspace(0, 2 * np.pi, resolution)
    z = np.linspace(0, z_max, resolution)
    r = np.linspace(r_min, r_max, resolution)
    z_fixed = np.linspace(0, 1.0, resolution)  # Immer 10 cm hoch

    # Vollständiger Zylinder (Referenz). Damit das Segment nicht allzu alleine ist
    PHI_outer, Z_outer = np.meshgrid(phi, z_fixed)
    X_outer = R_outer * np.cos(PHI_outer)
    Y_outer = R_outer * np.sin(PHI_outer)
    ax.plot_surface(
        X_outer, Y_outer, Z_outer, color="lightgray", alpha=0.4, edgecolor="none"
    )

    # Segmentflächen
    phi_segment = np.linspace(0, phi_max, resolution)
    PHI_seg, Z_seg = np.meshgrid(phi_segment, z)
    X = r_max * np.cos(PHI_seg)
    Y = r_max * np.sin(PHI_seg)
    ax.plot_surface(X, Y, Z_seg, color="skyblue", alpha=0.8, edgecolor="none")

    X_inner = r_min * np.cos(PHI_seg)
    Y_inner = r_min * np.sin(PHI_seg)
    ax.plot_surface(
        X_inner, Y_inner, Z_seg, color="skyblue", alpha=0.4, edgecolor="none"
    )

    R_top, PHI_top = np.meshgrid(r, phi_segment)
    X_top = R_top * np.cos(PHI_top)
    Y_top = R_top * np.sin(PHI_top)
    Z_top = np.full_like(X_top, z_max)
    Z_bottom = np.zeros_like(X_top)

    ax.plot_surface(X_top, Y_top, Z_top, color="cyan", alpha=0.5, edgecolor="none")
    ax.plot_surface(X_top, Y_top, Z_bottom, color="cyan", alpha=0.5, edgecolor="none")

    R_side, Z_side = np.meshgrid(r, z)
    X_side0 = R_side * np.cos(0)
    Y_side0 = R_side * np.sin(0)
    X_side1 = R_side * np.cos(phi_max)
    Y_side1 = R_side * np.sin(phi_max)

    ax.plot_surface(
        X_side0, Y_side0, Z_side, color="orange", alpha=0.8, edgecolor="none"
    )
    ax.plot_surface(
        X_side1, Y_side1, Z_side, color="orange", alpha=0.8, edgecolor="none"
    )

    # Achsen
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_box_aspect([1, 1, 1])
    ax.set_xlim([-R_outer, R_outer])
    ax.set_ylim([-R_outer, R_outer])
    ax.set_zlim([0, 1.0])
    plt.draw()

    # Darstellung der Bereiche für r, phi und z
    coord_text = (
        r"$r \in [{:.2f}, {:.2f}]$".format(r_min, r_max) + "\n"
        r"$\varphi \in [0, {}]$".format(format_phi(phi_max)) + "\n"
        r"$z \in [0, {:.2f}]$".format(z_max)
    )
    ax.text2D(
        0.001,
        1,
        coord_text,
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.8, boxstyle="round"),
    )


def main():
    # Startwerte
    r_center0 = 0.75
    r_width0 = 0.4
    phi_max0 = np.pi / 2
    z_max0 = 1.0

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    plot_cylinder_with_segment(ax, r_center0, r_width0, phi_max0, z_max0)

    # Slider-Achsen aka wo befinden sie sich.
    axcolor = "lightgoldenrodyellow"
    ax_r_center = plt.axes([0.25, 0.00, 0.65, 0.03], facecolor=axcolor)
    ax_r_width = plt.axes([0.25, 0.025, 0.65, 0.03], facecolor=axcolor)
    ax_phi_max = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
    ax_slider_z = plt.axes([0.25, 0.075, 0.65, 0.03], facecolor=axcolor)

    # Sliders und deren min/max werte
    slider_r_center = Slider(
        ax_r_center, r"$r_{center}$", 0.0, 1.0, valinit=r_center0, valstep=0.01
    )
    slider_r_width = Slider(
        ax_r_width, r"$r_{width}$", 0.0, 1.0, valinit=r_width0, valstep=0.01
    )
    slider_phi_max = Slider(
        ax_phi_max, r"$\varphi $", 0.1, 2 * np.pi, valinit=phi_max0, valstep=0.1
    )

    slider_z = Slider(ax_slider_z, r"$z_{max}$", 0.1, 1.0, valinit=z_max0, valstep=0.01)

    resetax = plt.axes([0.8, 0.90, 0.1, 0.04])
    button_reset = Button(resetax, "Reset", color=axcolor, hovercolor="0.975")

    # Reset-button Es ist ansonsten zu nervig wieder zum default zum kommen
    def reset(event):
        slider_r_center.reset()
        slider_r_width.reset()
        slider_phi_max.reset()
        slider_z.reset()

    button_reset.on_clicked(reset)

    def update(val):
        r_center = slider_r_center.val
        r_width = slider_r_width.val
        phi_max = slider_phi_max.val
        z_max = slider_z.val

        # Grenzen von r_center anpassen
        max_center = 1.0 - r_width / 2
        min_center = r_width / 2
        r_center = np.clip(r_center, min_center, max_center)

        # Segment automatisch anpassen
        slider_r_center.eventson = False
        slider_r_center.set_val(r_center)
        slider_r_center.eventson = True

        plot_cylinder_with_segment(ax, r_center, r_width, phi_max, z_max)

    slider_r_center.on_changed(update)
    slider_r_width.on_changed(update)
    slider_phi_max.on_changed(update)
    slider_z.on_changed(update)

    plt.show()


if __name__ == "__main__":
    main()
