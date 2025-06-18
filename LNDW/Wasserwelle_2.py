import pygame
import time
import math
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Bildschirm
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Interferenz Simulation mit Audio-Mikrofon")

clock = pygame.time.Clock()

# Konstanten
WAVE_SPEED = 100       # px/s
WAVE_DURATION = 3      # Dauer, wie lange ein einzelner Kreis sichtbar ist (s)
SOURCE_LIFETIME = 5    # Lebensdauer der Quelle (s)
MIC_POS = (width // 2, height // 2)  # Mikrofon-Mitte
ARRIVAL_TOLERANCE = 5  # Toleranz für "Ankommen" am Mikrofon in Pixel

# Frequenz aus Wellenlänge (Pixel) berechnen
def wavelength_to_freq(wavelength_px):
    if wavelength_px < 1:
        wavelength_px = 1
    freq = 2000 / wavelength_px
    return max(200, min(1000, freq))


class WaveSource:
    def __init__(self, pos, wavelength):
        self.pos = pos
        self.wavelength = wavelength
        self.created_time = time.time()
        self.waves = []

    def update(self, current_time):
        t_since_start = current_time - self.created_time
        if t_since_start < SOURCE_LIFETIME:
            num_waves_expected = int(t_since_start * WAVE_SPEED / self.wavelength)
            while len(self.waves) < num_waves_expected:
                wave_time = self.created_time + len(self.waves) * self.wavelength / WAVE_SPEED
                self.waves.append(wave_time)

    def draw(self, surface, current_time):
        for wave_time in self.waves:
            age = current_time - wave_time
            if age < WAVE_DURATION:
                radius = age * WAVE_SPEED
                pygame.draw.circle(surface, (0, 100, 255), self.pos, int(radius), 1)

    def is_expired(self, current_time):
        return (current_time - self.created_time) > SOURCE_LIFETIME


# Audio-Ton erzeugen aus Frequenzen
sample_rate = 44100

def generate_tone(freqs, amps, duration=0.1):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    signal = np.zeros_like(t)
    for f, a in zip(freqs, amps):
        signal += a * np.sin(2 * np.pi * f * t)
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val
    sound_array = np.int16(signal * 32767)
    sound = pygame.sndarray.make_sound(sound_array)
    return sound


wave_sources = []
click_start_time = None
current_sound = None

running = True
while running:
    current_time = time.time()

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
                print(f"Neue Wellenquelle bei {click_pos}, Wellenlänge: {wavelength:.1f}")
                wave_sources.append(WaveSource(click_pos, wavelength))
                click_start_time = None

    screen.fill((0, 0, 0))

    # Update und zeichne alle Quellen
    for source in wave_sources:
        source.update(current_time)
        source.draw(screen, current_time)

    # Entferne abgelaufene Quellen
    wave_sources = [s for s in wave_sources if not s.is_expired(current_time)]

    # --- Audio: Welche Wellenfronten erreichen gerade das Mikrofon? ---
    freqs_to_play = []
    for source in wave_sources:
        dist = math.dist(source.pos, MIC_POS)
        for wave_time in source.waves:
            age = current_time - wave_time
            if 0 <= age < WAVE_DURATION:
                radius = age * WAVE_SPEED
                if abs(radius - dist) <= ARRIVAL_TOLERANCE:
                    freq = wavelength_to_freq(source.wavelength)
                    freqs_to_play.append(freq)
                    break  # pro Quelle nur einmal pro Frame Ton spielen

    if freqs_to_play:
        amps = [1]*len(freqs_to_play)
        if current_sound:
            current_sound.stop()
        current_sound = generate_tone(freqs_to_play, amps)
        current_sound.play(-1)
    else:
        if current_sound:
            current_sound.stop()
            current_sound = None

    # Optional: Mikrofonposition visualisieren
    pygame.draw.circle(screen, (255, 255, 255), MIC_POS, 5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
