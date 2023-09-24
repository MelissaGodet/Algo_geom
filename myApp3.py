import math
import sys
import random
import pygame
import classes

# Pygame initialization
pygame.init()

# Window parameters
width, height = 1000, 800

window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Triangulation")

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


def naive_triangulation(points, color):
    # Calculer la coque convexe
    convex_hull = classes.graham_scan_without_drawing(points)
    convex_hull.draw(window, color)

    triangulation = convex_hull.triangulation(window, color)
    triangulation_points = triangulation.get_points()

    # Draw the first triangulation
    triangulation.draw(window, color)

    for p in points:
        if p not in triangulation_points:
            # Insert the point in the triangulation
            triangulation.insert_a_point(p)

            # Draw the triangulation
            triangulation.draw(window, color)

            # Refresh
            pygame.display.flip()
            pygame.time.delay(500)  # Delay to slow down the animation

    return triangulation


def naive_triangulation2(points, color):
    convex_hull = classes.graham_scan_without_drawing(points)
    triangulation = convex_hull.triangulation(window, color)
    triangulation_points = triangulation.get_points()
    for p in points:
        if p not in triangulation_points:
            triangulation.insert_a_point(p)
    return triangulation

def slow_delaunay(points, color):
    triangulation = naive_triangulation(points, color)
    triangulation = triangulation.add_neighbors()
    triangle_list = triangulation.triangles.copy()

    while len(triangle_list) != 0:
        window.fill((255, 255, 255))  # Effacez l'écran
        draw_points(points)
        display_menu()
        for triangle in triangulation.triangles:
            triangle.draw(window, color)
        pygame.display.flip()

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

        pygame.time.delay(200)

    return triangulation

def slow_delaunay2(points):
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

def incremental_delaunay(points, width, height):

    l = max(width, height)
    big_triangle_points = classes.Point(0, 0), classes.Point(3 * l, 0), classes.Point(1.5 * l, 2 * l)
    big_triangle = classes.Triangle(big_triangle_points[0], big_triangle_points[1], big_triangle_points[2])
    triangulation = classes.Triangulation([big_triangle])

    running = True
    for p in points:
        t = triangulation.who_contains(p)
        neighbors = t.get_neighbors()
        triangulation, new_triangles = triangulation.insert_a_point2(p)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        window.fill((255, 255, 255))  # Effacez l'écran
        display_menu()

        for triangle in triangulation.triangles:
            triangle.draw(window, "black")
        pygame.display.flip()

        for triangle in new_triangles:
            new_neighbors = triangle.get_neighbors()
            for neighbour in classes.intersection(neighbors, new_neighbors):
                triangulation = triangulation.rec_lawson_flip(triangle, neighbour)

        pygame.time.delay(500)  # Attendez 500 millisecondes avant de passer à l'étape suivante

    for p in big_triangle_points:
       triangulation.remove_point(p)

    window.fill((255, 255, 255))  # Effacez l'écran
    display_menu()

    return triangulation

def incremental_delaunay2(points, width, height):
    l = max(width, height)
    big_triangle_points = classes.Point(0, 0), classes.Point(3 * l, 0), classes.Point(1.5 * l, 2 * l)
    big_triangle = classes.Triangle(big_triangle_points[0], big_triangle_points[1], big_triangle_points[2])
    triangulation = classes.Triangulation([big_triangle])
    for p in points:
        t = triangulation.who_contains(p)
        neighbors = t.get_neighbors()
        triangulation, new_triangles = triangulation.insert_a_point2(p)
        for triangle in new_triangles:
            new_neighbors = triangle.get_neighbors()
            for neighbour in classes.intersection(neighbors, new_neighbors):
                triangulation = triangulation.rec_lawson_flip(triangle, neighbour)

    for p in big_triangle_points:
       triangulation.remove_point(p)
    return triangulation


def voronoi(points):
    triangulation = slow_delaunay(points, "black")
    voronoi_point = []
    for triangle in triangulation.triangles:
        center = triangle.circumcenter()
        voronoi_point.append(center)
        pygame.draw.circle(window, "red", (center.x, center.y), 2)
    triangulation_voronoi = slow_delaunay(voronoi_point, "blue")
    return classes.Voronoi(triangulation_voronoi)


def draw_points(points):
    window.fill((255, 255, 255))  # Clear the screen

    display_menu()  # Draw the menu

    # Draw the points
    for point in points:
        pygame.draw.circle(window, "black", (point.x, point.y), radius_point)

def display_menu():
    font = pygame.font.Font(None, 30)
    naive_triangulation_text = font.render("Naive Triangulation", True, (0, 0, 0))
    slow_delaunay_text = font.render("Slow Delaunay", True, (0, 0, 0))
    incremental_delaunay_text = font.render("Incremental Delaunay", True, (0, 0, 0))
    voronoi_text = font.render("Voronoi", True, (0, 0, 0))

    # Position the menu items
    menu_x = 20
    naive_triangulation_y = 20
    slow_delaunay_y = 60
    incremental_delaunay_y = 100
    voronoi_y = 140

    window.blit(naive_triangulation_text, (menu_x, naive_triangulation_y))
    window.blit(slow_delaunay_text, (menu_x, slow_delaunay_y))
    window.blit(incremental_delaunay_text, (menu_x, incremental_delaunay_y))
    window.blit(voronoi_text, (menu_x, voronoi_y))

def determine_triangulation_algorithm(algorithm, points):
    if algorithm == "naive_triangulation":
        naive_triangulation(points)
    elif algorithm == "slow_delaunay":
        slow_delaunay(points, "black")
    elif algorithm == "incremental_delaunay":
        incremental_delaunay(points, w, h)
    elif algorithm == "voronoi":
        voronoi(points)
    else:
        return None



w, h = math.ceil(width / 3), math.ceil(height / 3)
points = generate_points(n, w, h)


# Initialize a flag to keep track of algorithm change
algorithm_changed = False

# Main loop
running = True
draw_points(points)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                if 20 <= x <= 220 and 20 <= y <= 50:
                    selected_algorithm = "naive_triangulation"
                    algorithm_changed = True
                elif 20 <= x <= 220 and 60 <= y <= 90:
                    selected_algorithm = "slow_delaunay"
                    algorithm_changed = True
                elif 20 <= x <= 220 and 100 <= y <= 130:
                    selected_algorithm = "incremental_delaunay"
                    algorithm_changed = True
                elif 20 <= x <= 220 and 140 <= y <= 170:
                    selected_algorithm = "voronoi"
                    algorithm_changed = True


    # Check if the algorithm was changed
    if algorithm_changed:
        draw_points(points)
        # Recalculate and draw the convex hull based on the selected algorithm
        convex_hull = determine_triangulation_algorithm(selected_algorithm, points)
        algorithm_changed = False

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
