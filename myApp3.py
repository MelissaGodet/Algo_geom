import math
import sys
import random
import pygame
import pylab as p

import classes

# Pygame initialization
pygame.init()

# Window parameters
width, height = 1000, 800

window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Convex hull")

# Points Parameters
n = 10  # Number of points
radius_point = 3  # Radius for the points


def generate_points(n, width, height):
    points = []

    for _ in range(n):
        x = random.randint(width, 2 * width)
        y = random.randint(0, height)
        points.append(classes.Point(x, y))

    return points


def naive_triangulation(points):
    convex_hull = classes.graham_scan_without_drawing(points)
    triangulation = convex_hull.triangulation()
    triangulation_points = triangulation.get_points()
    for p in points:
        if p not in triangulation_points:
            triangulation.insert_a_point(p)
    return triangulation


def slow_delaunay(points):
    triangulation = naive_triangulation(points)
    triangulation = triangulation.add_neighbors()
    triangle_list = triangulation.triangles.copy()
    while len(triangle_list) != 0:
        triangle: classes.Triangle = triangle_list[0]
        neighbors = triangle.get_neighbors()
        flip = False
        for neighbour in neighbors:
            triangulation, flip = triangulation.lawson_flip(triangle, neighbour)
            if flip:
                triangle_list = triangulation.triangles.copy()
                break
        if not flip:
            triangle_list.pop(0)

    return triangulation


def incremental_delaunay(points, width, height, window):
    l = max(width, height)
    big_triangle_points = classes.Point(0, 0), classes.Point(3 * l, 0), classes.Point(1.5 * l, 2 * l)
    big_triangle = classes.Triangle(big_triangle_points[0], big_triangle_points[1], big_triangle_points[2])
    triangulation = classes.Triangulation([big_triangle])
    for p in points:
        t = triangulation.who_contains(p)
        neighbors = t.get_neighbors()
        triangulation, new_triangles = triangulation.insert_a_point2(p)
        print(len(triangulation.triangles))
        for triangle in new_triangles:
            new_neighbors = triangle.get_neighbors()
            for neighbour in classes.intersection(neighbors, new_neighbors):
                triangulation = triangulation.rec_lawson_flip(triangle, neighbour)

    for p in big_triangle_points:
       triangulation.remove_point(p)
    return triangulation


w, h = math.ceil(width / 3), math.ceil(height / 3)
points = generate_points(n, w, h)

# triangulation = slow_delaunay(n, width, height)
# Main loop

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    window.fill((255, 255, 255))

    # Draw the points
    for point in points:
        pygame.draw.circle(window, "black", (point.x, point.y), radius_point)

    triangulation = incremental_delaunay(points, w, h, window)

    '''
    for triangle in triangulation.triangles:
        center = triangle.circumcenter()
        radius = math.sqrt((triangle.p1.x - center.x) ** 2 + (triangle.p1.y - center.y) ** 2)
        pygame.draw.circle(window, "red", (center.x, center.y), radius, 2)
    '''
    triangulation.draw(window)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
