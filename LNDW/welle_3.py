import pygame
import numpy as np
import time
import math

pygame.init()
pygame.mixer.quit()  # sicherheitshalber Mixer neu starten
pygame.mixer.init(frequency=44100, size=-16, channels=2)  # Stereo

# Bildschirm
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Interferenz Simulation mit Audio")

# Hintergrundbild laden und skalieren
background = pygame.image.load("C:/Users/victo/Documents/Python Scripts/LNDW/Wasser_back.jpg").convert()
background = pygame.transform.scale(background, (width, height))


# Parameter
max_lifetime = 5  # Sekunden
sample_rate = 44100
tone_update_interval = 0.1  # Audio alle 0.1s aktualisieren
step = 5  # Pixel-Schritt für Rendering

# Schallgeschwindigkeit & Frequenzmapping
def wavelength_to_freq(wavelength_px):
    if wavelength_px < 1:
        wavelength_px = 1
    freq = 2000 / wavelength_px
    return max(200, min(1000, freq))

# Wellenquelle Klasse mit Ausbreitung
class WaveSource:
    def __init__(self, pos, wavelength, start_time):
        self.pos = pos
        self.wavelength = wavelength
        self.start_time = start_time
        self.lifetime = max_lifetime
        self.wave_duration = 3
        self.wave_speed = 100  # px/s

    def amplitude(self, point, current_time):
        elapsed = current_time - self.start_time
        if elapsed < 0 or elapsed > self.lifetime + self.wave_duration:
            return 0
        
        dist = math.dist(self.pos, point)
        
        # Zeit, die die Welle braucht, um diesen Punkt zu erreichen
        wave_age = elapsed - dist / self.wave_speed
        
        # Nur sichtbar innerhalb wave_duration nach Passieren des Punktes
        if wave_age < 0 or wave_age > self.wave_duration:
            return 0
        
        phase = 2 * math.pi * ((dist / self.wavelength) - (self.wave_speed / self.wavelength) * elapsed)
        
        # Optional: Fadeout der Amplitude am Ende der Lebensdauer
        fade = max(0, 1 - elapsed / self.lifetime)
        
        return math.sin(phase) * fade

wave_sources = []

running = True
clock = pygame.time.Clock()

mouse_down_time = None
last_audio_update = 0
current_sound = None

def generate_tone(freqs, amps, duration=0.1):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    signal = np.zeros_like(t)
    for f, a in zip(freqs, amps):
        signal += a * np.sin(2 * np.pi * f * t)
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val
    signal_int16 = np.int16(signal * 32767)
    stereo_signal = np.column_stack((signal_int16, signal_int16))
    sound = pygame.sndarray.make_sound(stereo_signal)
    return sound

while running:
    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down_time = current_time
            click_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if mouse_down_time is not None:
                press_duration = current_time - mouse_down_time
                wavelength = max(5, 150 - press_duration * 100)
                wave_sources.append(WaveSource(click_pos, wavelength, current_time))
                mouse_down_time = None

    screen.blit(background, (0, 0))


    surface_array = np.zeros((height // step, width // step))
    for y in range(0, height, step):
        for x in range(0, width, step):
            point = (x, y)
            amp_sum = 0
            for source in wave_sources:
                amp_sum += source.amplitude(point, current_time)
            surface_array[y // step, x // step] = amp_sum

    max_amp = np.max(np.abs(surface_array))
    if max_amp == 0:
        max_amp = 1

    for y in range(surface_array.shape[0]):
        for x in range(surface_array.shape[1]):
            val = surface_array[y, x] / max_amp
            if val > 0:
                # Position im Originalbild
                px = x * step
                py = y * step
                if 0 <= px < width and 0 <= py < height:
                    # Farbe aus dem Hintergrund
                    bg_color = background.get_at((px, py))
                    r, g, b = bg_color.r, bg_color.g, bg_color.b

                    # Helligkeit je nach Wellenstärke anpassen
                    brightness_factor = 1 + val * 0.5  # z. B. bis zu 50 % heller
                    r = min(255, int(r * brightness_factor))
                    g = min(255, int(g * brightness_factor))
                    b = min(255, int(b * brightness_factor))

                    # Nur blau betonen, andere Farben optional abschwächen:
                    r = int(r * 0.5)
                    g = int(g * 0.5)

                    pygame.draw.rect(screen, (r, g, b), (px, py, step, step))

    wave_sources = [s for s in wave_sources if current_time - s.start_time <= s.lifetime + s.wave_duration]

    # Audioausgabe (Mitte des Bildschirms)
    if current_time - last_audio_update > tone_update_interval and wave_sources:
        center = (width // 2, height // 2)
        freqs = []
        amps = []
        for source in wave_sources:
            a = source.amplitude(center, current_time)
            f = wavelength_to_freq(source.wavelength)
            freqs.append(f)
            amps.append(abs(a))
        if freqs:
            if current_sound:
                current_sound.stop()
            current_sound = generate_tone(freqs, amps)
            current_sound.play(-1)
        last_audio_update = current_time
    elif not wave_sources and current_sound:
        current_sound.stop()
        current_sound = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
