# Example file showing a circle moving on screen
import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from piratesim.game import SingleRun

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

game = SingleRun()

manager = UIManager(
    (screen.get_width(), screen.get_height()), "data/themes/quick_theme.json"
)
button = UIButton((screen.get_width() // 2, screen.get_height() // 2), "PLAY!")

background = pygame.Surface((screen.get_width(), screen.get_height()))
background.fill(manager.ui_theme.get_colour("dark_bg"))

window_surface = pygame.display.set_mode((screen.get_width(), screen.get_height()))

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == button:
                print("Hello World!")
        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()

pygame.quit()
