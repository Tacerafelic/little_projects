import pygame
import time

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

click_start_time = None
wave_sources = []

# Konstante Wellen-Ausbreitungsgeschwindigkeit (px/s)
WAVE_SPEED = 100  # 100 Pixel pro Sekunde
WAVE_DURATION = 3  # Sekunden, wie lange eine Quelle Wellen aussendet
SOURCE_LIFETIME = 5 

class WaveSource:
    def __init__(self, pos, wavelength):
        self.pos = pos
        self.wavelength = wavelength
        self.created_time = time.time()
        self.waves = []

    def update(self, current_time):
        t_since_start = current_time - self.created_time

        # Neue Wellen nur erzeugen, wenn Quelle nicht abgelaufen
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
    # wave_sources = [source for source in wave_sources if not source.is_expired(current_time)]

    # Update und zeichne alle Quellen
    for source in wave_sources:
        source.update(current_time)
        source.draw(screen, current_time)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
