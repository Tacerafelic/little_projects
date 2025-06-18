import pygame
import time
import math
import numpy as np

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

WAVE_SPEED = 100  # px/s
SOURCE_LIFETIME = 5
WAVE_DURATION = 3

class WaveSource:
    def __init__(self, pos, wavelength):
        self.pos = pos
        self.wavelength = wavelength
        self.created_time = time.time()

    def is_active(self, t):
        return (t - self.created_time) < SOURCE_LIFETIME + WAVE_DURATION

    def amplitude(self, pos, t):
        r = math.dist(pos, self.pos)
        elapsed = t - self.created_time
        if elapsed < 0 or elapsed > SOURCE_LIFETIME + WAVE_DURATION:
            return 0
        # Phase der Welle
        phase = 2 * math.pi * ((r / self.wavelength) - (WAVE_SPEED / self.wavelength) * elapsed)
        # Dämpfung: Welle nur innerhalb WAVE_DURATION nach Durchlaufen des Radius sichtbar
        wave_age = elapsed - r / WAVE_SPEED
        if wave_age < 0 or wave_age > WAVE_DURATION:
            return 0
        return math.sin(phase)

wave_sources = []
click_start_time = None
click_pos = (0,0)

running = True
while running:
    t = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_start_time = time.time()
            click_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if click_start_time is not None:
                duration = time.time() - click_start_time
                wavelength = max(20, 100 - duration * 80)
                wave_sources.append(WaveSource(click_pos, wavelength))
                click_start_time = None

    screen.fill((0,0,0))

    # Erzeuge Pixel-Array für Interferenz (nur jedes 5. Pixel zur Performance)
    step = 5
    surface_array = np.zeros((height//step, width//step), dtype=np.float32)

    for y in range(0, height, step):
        for x in range(0, width, step):
            pos = (x, y)
            amplitude_sum = 0
            for source in wave_sources:
                amplitude_sum += source.amplitude(pos, t)
            surface_array[y//step, x//step] = amplitude_sum

    # Normiere & Zeichne
    max_amp = np.max(np.abs(surface_array))
    if max_amp == 0:
        max_amp = 1

    for y in range(surface_array.shape[0]):
        for x in range(surface_array.shape[1]):
            val = surface_array[y,x] / max_amp  # -1 bis 1
            brightness = int((val + 1) / 2 * 255)
            color = (brightness, brightness, brightness)
            pygame.draw.rect(screen, color, (x*step, y*step, step, step))

    # Entferne alte Quellen
    wave_sources = [ws for ws in wave_sources if ws.is_active(t)]

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
