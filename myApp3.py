import sys
import random
import pygame

import classes

# Pygame initialization
pygame.init()

# Window parameters
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Convex hull")

# Points Parameters
n = 5  # Number of points
radius_point = 3  # Radius for the points


def generate_points(n):
    points = []
    for _ in range(n):
        x = random.randint(0, width)
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


'''
def slow_delaunay2(points):
    triangulation = naive_triangulation(points)
    triangulation = triangulation.add_neighbors()
    triangulation.draw(window)

    n = len(triangulation.triangles)
    for i in range(n):
        print("Triangle :" + str(i))
        triangulation = triangulation.recursive_lawson_flip(i)
    return triangulation
'''


def slow_delaunay(points):
    triangulation = naive_triangulation(points)
    triangulation = triangulation.add_neighbors()
    n = len(triangulation.triangles)
    for i in range(n):
        queue = [i]
        while len(queue) > 0:
            triangulation.print()
            current_index = queue[0]
            n1, n2, n3 = triangulation.triangles[current_index].n1_index, triangulation.triangles[
                current_index].n2_index, triangulation.triangles[current_index].n3_index
            l = [n1, n2, n3]
            not_fipped = True
            for k in l:
                if not_fipped and k is not None:
                    tk = triangulation.triangles[k]
                    l_neighbors_k = [tk.n1_index, tk.n2_index, tk.n3_index]
                    triangulation, flip = triangulation.lawson_flip(i, k)
                    if flip:
                        not_fipped = False
                        l_neighbors = [n1, n2, n3] + l_neighbors_k
                        for j in range(len(l_neighbors)):
                            if l_neighbors[j] is not None and l_neighbors[j] != current_index and l_neighbors[j] != k:
                                queue.append(l_neighbors[j])
            queue.pop(0)

    return triangulation


'''
def slow_delaunay(points):
    triangulation = naive_triangulation(points)
    triangulation = triangulation.add_neighbors()
    triangulation.draw(window)
    n = len(triangulation.triangles)
    for i in range(n):
        stack = [i]
        while len(stack) > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            current_index = stack[0]
            n1, n2, n3 = triangulation.triangles[current_index].n1_index, triangulation.triangles[
                current_index].n2_index, triangulation.triangles[current_index].n3_index
            l = [n1, n2, n3]
            not_fipped = True
            for k in l:
                if not_fipped and k is not None:
                    triangulation, flip = triangulation.lawson_flip(i, k)
                    if flip:
                        not_fipped = False
                        l_neighbors = [n1, n2, n3, triangulation.triangles[k].n1_index,
                                       triangulation.triangles[k].n2_index, triangulation.triangles[k].n3_index]
                        for j in range(len(l_neighbors)):
                            if l_neighbors[j] is not None and l_neighbors[j] != current_index and l_neighbors[j] != k:
                                stack.append(l_neighbors[j])
            stack.pop(0)

            # Dessinez et mettez à jour la fenêtre Pygame à chaque étape
            window.fill((255, 255, 255))
            triangulation.draw(window)
            pygame.display.flip()
            pygame.time.delay(500)  # Ajoutez une pause de 500 millisecondes (0.5 secondes) entre les étapes

    return triangulation
'''

# generate n points
points = generate_points(n)
'''
# triangulation = naive_triangulation(points)
t1 = classes.Triangle(classes.Point(200, 200), classes.Point(600, 200), classes.Point(400, 400))
t2 = classes.Triangle(classes.Point(200, 200), classes.Point(600, 200), classes.Point(400, 100))
t3 = classes.Triangle(classes.Point(800, 200), classes.Point(600, 200), classes.Point(400, 100))
points2 = [classes.Point(200, 200), classes.Point(600, 200), classes.Point(400, 400), classes.Point(400, 100),
           classes.Point(800, 200)]
triangulation = classes.Triangulation([t1, t2, t3])
# triangulation.lawson_flip(0, 1)
'''
triangulation = slow_delaunay(points)
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
    '''
    pygame.draw.circle(window, "black", (200, 200), 2)
    pygame.draw.circle(window, "black", (600, 200), 2)
    pygame.draw.circle(window, "black", (400, 400), 2)
    pygame.draw.circle(window, "black", (400, 100), 2)
    #triangulation.draw(window)
    '''

    triangulation.draw(window)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
