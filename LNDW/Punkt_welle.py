import pygame
import numpy as np
import matplotlib.cm as cm

# Projects:
#   Menü hinzufügen mit Steuerungserklärung
#   Reset-Buttom (erledigt EASY)
#   Farbskala rgb (meh)


# Pygame initialisieren
pygame.init()
width, height = 800, 600
legend_width = 100
screen = pygame.display.set_mode((width + legend_width, height))
pygame.display.set_caption("Interferenz zweier Kugelwellen – unabhängig steuerbar")

# Farben
# vielleicht kann man hier etwas mit den wellenlängen und so hinzufügen
BG_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
colormap = cm.get_cmap("plasma")

# Parameter
amplitude = 1

# Quellpositionen
# Quelle 1
source1_x = 100
source1_y = 250
wavelength1 = 30

# Quelle 2
source2_x = 100
source2_y = 350
wavelength2 = 30


def wavelength_to_rgb(wavelength):
    # Bereich: 380 nm – 780 nm
    gamma = 0.8
    intensity_max = 255

    if wavelength < 380 or wavelength > 780:
        return (0, 0, 0)

    if wavelength < 440:
        r, g, b = -(wavelength - 440) / (440 - 380), 0.0, 1.0
    elif wavelength < 490:
        r, g, b = 0.0, (wavelength - 440) / (490 - 440), 1.0
    elif wavelength < 510:
        r, g, b = 0.0, 1.0, -(wavelength - 510) / (510 - 490)
    elif wavelength < 580:
        r, g, b = (wavelength - 510) / (580 - 510), 1.0, 0.0
    elif wavelength < 645:
        r, g, b = 1.0, -(wavelength - 645) / (645 - 580), 0.0
    else:
        r, g, b = 1.0, 0.0, 0.0

    # Dämpfung an den Rändern
    if wavelength < 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
    elif wavelength > 700:
        factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)
    else:
        factor = 1.0

    def adjust(color):
        return int(round(intensity_max * (color * factor) ** gamma))

    return adjust(r), adjust(g), adjust(b)


# Heatmap-Funktion
def compute_intensity_colored(pos1, wl1, pos2, wl2):
    x = np.arange(0, width)
    y = np.arange(0, height)
    X, Y = np.meshgrid(x, y)

    r1 = np.sqrt((X - pos1[0]) ** 2 + (Y - pos1[1]) ** 2)
    r2 = np.sqrt((X - pos2[0]) ** 2 + (Y - pos2[1]) ** 2)

    k1 = 2 * np.pi / wl1
    k2 = 2 * np.pi / wl2

    wave1 = amplitude * np.sin(k1 * r1)
    wave2 = amplitude * np.sin(k2 * r2)

    # Normiert auf -1 bis 1
    norm_wave1 = (wave1 + 1) / 2
    norm_wave2 = (wave2 + 1) / 2

    color1 = np.array(wavelength_to_rgb(400 + wl1)) / 255
    color2 = np.array(wavelength_to_rgb(400 + wl2)) / 255

    # Überlagern
    rgb_image = (
        np.stack([norm_wave1, norm_wave1, norm_wave1], axis=-1) * color1
        + np.stack([norm_wave2, norm_wave2, norm_wave2], axis=-1) * color2
    )

    # Normalisieren und auf 0–255 skalieren
    rgb_image = np.clip(rgb_image, 0, 1)
    return (rgb_image * 255).astype(np.uint8).swapaxes(0, 1)


# Legende
# muss noch irgendwie besser dargestellt werden

def draw_legend(surface):
    legend_height = int(height * 0.9)
    legend_top = int((height - legend_height) / 2)
    for i in range(legend_height):
        wavelength = 780 - (i / legend_height) * (780 - 380)
        color = wavelength_to_rgb(wavelength)
        y_pos = legend_top + i
        pygame.draw.line(surface, color, (width + 10, y_pos), (width + 40, y_pos))

    # Beschriftung
    font = pygame.font.SysFont(None, 20)
    for wl in [780, 700, 620, 580, 530, 490, 450, 400, 380]:
        y = legend_top + int((1 - (wl - 380) / (780 - 380)) * legend_height)
        label = font.render(f"{wl} nm", True, WHITE)
        surface.blit(label, (width + 45, y - 10))

# def draw_legend(surface):
#     font = pygame.font.SysFont(None, 20)
#     for i in range(height):
#         # Sichtbares Spektrum: 380 nm bis 780 nm
#         wl = 780 - (i / height) * 400  # oben 780, unten 380
#         color = wavelength_to_rgb(wl)
#         pygame.draw.line(surface, color, (width + 10, i), (width + 40, i))

#     # Beschriftungen für typische Wellenlängen
#     for wl in [780, 700, 620, 580, 530, 490, 450, 400, 380]:
#         y = int((780 - wl) / 400 * height)
#         label = f"{int(wl)} nm"
#         txt = font.render(label, True, WHITE)
#         surface.blit(txt, (width + 45, y - 10))

# Initialisierung
# rgb_map = compute_intensity()

# Hauptloop
running = True
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

while running:
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    changed = False

    # Bewegung Quelle 1
    # klassisch WASD- Steuerung
    if keys[pygame.K_w]:
        source1_y -= 5
    if keys[pygame.K_s]:
        source1_y += 5
    if keys[pygame.K_a]:
        source1_x -= 5
    if keys[pygame.K_d]:
        source1_x += 5

    # Quelle 2 bewegen
    # IJKL-Steuerung
    if keys[pygame.K_i]:
        source2_y -= 5
    if keys[pygame.K_k]:
        source2_y += 5
    if keys[pygame.K_j]:
        source2_x -= 5
    if keys[pygame.K_l]:
        source2_x += 5

    # Wellenlängen ändern
    # q und e für Quelle 1
    # u und o für Quelle 2
    if keys[pygame.K_q]:
        wavelength1 = max(5, wavelength1 - 1)
    if keys[pygame.K_e]:
        wavelength1 += 1
    if keys[pygame.K_u]:
        wavelength2 = max(5, wavelength2 - 1)
    if keys[pygame.K_o]:
        wavelength2 += 1

    # RESET
    if keys[pygame.K_ESCAPE]:
        source1_x = 100
        source1_y = 250
        source2_x = 100
        source2_y = 350
        wavelength1 = 30
        wavelength2 = 30

    rgb_map = compute_intensity_colored(
        (source1_x, source1_y), wavelength1, (source2_x, source2_y), wavelength2
    )

    surface = pygame.surfarray.make_surface(rgb_map)
    screen.fill(BG_COLOR)
    screen.blit(surface, (0, 0))

    # Quellen anzeigen
    pygame.draw.circle(screen, WHITE, (source1_x, source1_y), 5)
    pygame.draw.circle(screen, WHITE, (source2_x, source2_y), 5)

    # Textanzeige
    info1 = font.render(
        f"Quelle 1: x={source1_x} y={source1_y} λ={400 + wavelength1} nm", True, WHITE
    )
    info2 = font.render(
        f"Quelle 2: x={source2_x} y={source2_y} λ={400 + wavelength2} nm", True, WHITE
    )

    screen.blit(info1, (10, 10))
    screen.blit(info2, (10, 35))

    draw_legend(screen)
    pygame.display.flip()

pygame.quit()