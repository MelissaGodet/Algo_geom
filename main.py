import pygame
import sys

# Initialize Pygame
pygame.init()

# Define the size of the window
width, height = 800, 800
window_size = (width, height)
rectangle = pygame.Rect(200, 200, 400, 400)

# Create the window
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("My first Pygame application")

# Main loop of the game
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Color the background
    window.fill('white')

    # Draw on the window
    pygame.draw.line(window, "black", (0, 0), (800, 800), 2)
    pygame.draw.line(window, "black", (0, 800), (800, 0), 2)
    pygame.draw.circle(window, "red", (400, 400), 180, 5)
    pygame.draw.circle(window, "red", (400, 400), 5)
    pygame.draw.arc(window, "blue", rectangle, 0, 3.14, 10)


    # Update the window
    pygame.display.flip()

# Quit Pygame
pygame.quit()
