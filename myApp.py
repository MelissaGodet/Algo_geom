import pygame
import sys
import classes

# Pygame initialization
pygame.init()

# Window parameters
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Interactive Polygon Drawing")

# List to store points and segments of the polygon
points = []
unconnected_points = []
segments = []

drawing = True  # Start in drawing mode

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                x, y = event.pos
                if drawing:
                    # Connect the last point to the current point
                    if points:
                        segments.append(classes.Segment(points[-1], classes.Point(x, y)))
                    points.append(classes.Point(x, y))
                else:
                    # Add a new point without connecting
                    unconnected_points.append(classes.Point(x, y))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if drawing and len(points) > 1:
                    # Connect the last point to the first one to close the polygon
                    segments.append(classes.Segment(points[-1], points[0]))
                drawing = not drawing  # Toggle drawing mode with the space bar

    # Clear the screen
    window.fill((255, 255, 255))

    # If there are points and drawing is True, connect the last point to the first one
    if len(points) > 1 and not drawing:
        segments.append(
            classes.Segment(classes.Point(points[-1].x, points[-1].y), classes.Point(points[0].x, points[0].y)))

    # Draw the segments of the current polygon
    polygon = classes.Polygon(segments)
    polygon.draw(window, polygon.color())


    # Draw points
    for p in unconnected_points:
        pygame.draw.circle(window, polygon.color_point(p), (p.x, p.y), 2)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
