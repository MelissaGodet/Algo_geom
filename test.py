import math
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
n = 10  # Number of points
radius_point = 3  # Radius for the points
# List of points considered by jarvis march
jarvis_points = []
# List of segments considered by the edges algorithm
edges_algo_segments = []
# List of points considered by graham
graham_points = []


# Function for n random points
def generate_points(n):
    points = []
    for _ in range(n):
        x = random.randint(0, width)
        y = random.randint(0, height)
        points.append(classes.Point(x, y))
    return points


def angle(p, current_point):
    v_unit = (1, 0)
    v = (p.x - current_point.x, p.y - current_point.y)
    norme = math.sqrt((p.x - current_point.x) ** 2 + (p.y - current_point.y) ** 2)
    if norme == 0:
        return 0.0  # Évitez une division par zéro
    angle = math.acos((v[0] * v_unit[0] + v[1] * v_unit[1]) / norme)
    return angle


def lowest_point_index(points):
    lowest_index = 0
    for i in range(len(points)):
        if points[i].y < points[lowest_index].y:
            lowest_index = i
    return lowest_index


def orientation(p, q, r):
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val == 0:
        return 0
    return 1 if val > 0 else 2


def edges_algo(points):
    n = len(points)
    segments = []
    for i in range(n):
        for j in range(n):
            positive_count = 0
            negative_count = 0
            for k in range(n):
                if classes.cross_product(points[i], points[j], points[k]) > 0:
                    positive_count += 1
                else:
                    negative_count += 1
            # verify if evry cross product have the same sign
            if positive_count == 0 or negative_count == 0:
                segments.append(classes.Segment(points[i], points[j]))
                edges_algo_segments.clear()
                edges_algo_segments.extend(segments)
                # Clear the screen
                window.fill((255, 255, 255))

                # Draw the menu
                display_menu()

                # Draw the points
                for point in points:
                    pygame.draw.circle(window, "black", (point.x, point.y), radius_point)

                # Draw the current convex hull
                for s in segments:
                    pygame.draw.line(window, "green", (s.point1.x, s.point1.y), (s.point2.x, s.point2.y), 2)

                # Update the display
                pygame.display.flip()
                pygame.time.delay(200)  # Delay to slow down the animation

    convex_hull = classes.Polygon(segments)

    return convex_hull


def jarvis_march(points):
    n = len(points)
    if n < 3:
        # Convex hull is not possible with less than 3 points.
        return classes.Polygon([classes.Segment(points[i], points[i + 1]) for i in range((n) - 1)])
    # Points of the convex hull
    convex_hull_points = []
    # lowest point to start with
    lowest_index = lowest_point_index(points)
    # Initialized
    current_index = lowest_index
    k = 0

    while k < n:
        k += 1
        # Update the points currently considered by Graham Scan
        jarvis_points.clear()
        jarvis_points.extend(convex_hull_points)

        # Clear the screen
        window.fill((255, 255, 255))

        # Draw the menu
        display_menu()

        # Draw the points
        for point in points:
            pygame.draw.circle(window, "black", (point.x, point.y), radius_point)

        # Add the next point
        convex_hull_points.append(points[current_index])
        next_index = (current_index + 1) % n

        # Find the biggest angle
        for i in range(n):
            # Find if there a point with a biggest angle then the point before
            if orientation(points[current_index], points[i], points[next_index]) == 2:
                next_index = i

        current_index = next_index

        # Draw the convex hull
        if len(convex_hull_points) > 2:
            pygame.draw.polygon(window, "green", [(p.x, p.y) for p in convex_hull_points], 1)

        # Update the display
        pygame.display.flip()
        pygame.time.delay(200)  # Delay to slow down the animation

        # The convex hull is complete
        if current_index == lowest_index:
            break

    # Add the last Point to close the polygon
    convex_hull_points.append(points[lowest_index])

    # Polygon creation
    convex_hull = classes.Polygon(
        [classes.Segment(convex_hull_points[i], convex_hull_points[i + 1]) for i in range(len(convex_hull_points) - 1)])

    return convex_hull


def graham_scan(points):
    if len(points) < 3:
        return None

    # Lowest point
    lowest = classes.lowest_point(points)

    # Sorted point from the smallest to the biggest with the horizontal
    sorted_points = sorted(points, key=lambda p: angle(p, lowest))

    # Points of the hull initialized
    stack = [lowest, sorted_points[0], sorted_points[1]]

    for i in range(2, len(sorted_points)):
        #Withdraw the segment that shouldn't be in the convex hull
        while len(stack) > 1 and classes.cross_product(stack[-2], stack[-1], sorted_points[i]) <= 0:
            stack.pop()
        #Add the next point
        stack.append(sorted_points[i])

        # Update the points currently considered by Graham Scan
        graham_points.clear()
        graham_points.extend(stack)

        # Clear the screen
        window.fill((255, 255, 255))

        # Draw the menu
        display_menu()

        # Draw the points
        for point in points:
            pygame.draw.circle(window, "black", (point.x, point.y), radius_point)

        # Draw the current convex hull
        if len(stack) > 2:
            pygame.draw.polygon(window, "green", [(p.x, p.y) for p in stack], 1)

        # Update the display
        pygame.display.flip()
        pygame.time.delay(200)  # Delay to slow down the animation

    # Add the last point to close the polygon
    stack.append(lowest)

    # Creation of the polygon
    convex_hull = classes.Polygon([classes.Segment(stack[i], stack[i + 1]) for i in range(len(stack) - 1)])

    return convex_hull


# generate n points
points = generate_points(n)  # Function to display the menu
for p in points:
    print("[" + str(p.x) + ", '" + str(p.y) + "]")

# Initialize convex_hull as None
convex_hull = None


# Function to display the menu
def display_menu():
    font = pygame.font.Font(None, 30)
    graham_scan_text = font.render("Graham Scan", True, (0, 0, 0))
    edges_algo_text = font.render("Edges Algorithm", True, (0, 0, 0))
    jarvis_march_text = font.render("Jarvis March", True, (0, 0, 0))

    # Position the menu items
    menu_x = 20
    graham_scan_y = 20
    edges_algo_y = 60
    jarvis_march_y = 100

    window.blit(graham_scan_text, (menu_x, graham_scan_y))
    window.blit(edges_algo_text, (menu_x, edges_algo_y))
    window.blit(jarvis_march_text, (menu_x, jarvis_march_y))


# Function to determine the convex hull based on user input
def determine_convex_hull(algorithm, points):
    if algorithm == "graham_scan":
        return graham_scan(points)
    elif algorithm == "edges_algo":
        return edges_algo(points)
    elif algorithm == "jarvis_march":
        return jarvis_march(points)
    else:
        return None


# Initial choice of algorithm
selected_algorithm = None

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                # Check if the user clicked on the menu items
                if 20 <= x <= 220 and 20 <= y <= 50:
                    selected_algorithm = "graham_scan"
                    # Recalculate the convex hull based on the selected algorithm
                    convex_hull = determine_convex_hull(selected_algorithm, points)
                elif 20 <= x <= 220 and 60 <= y <= 90:
                    selected_algorithm = "edges_algo"
                    # Recalculate the convex hull based on the selected algorithm
                    convex_hull = determine_convex_hull(selected_algorithm, points)
                elif 20 <= x <= 220 and 100 <= y <= 130:
                    selected_algorithm = "jarvis_march"
                    # Recalculate the convex hull based on the selected algorithm
                convex_hull = determine_convex_hull(selected_algorithm, points)

    # Clear the screen
    window.fill((255, 255, 255))

    # Draw the menu
    display_menu()

    # Draw the points
    for point in points:
        if point == max(points, key=lambda p: (p.y, p.x)):
            pygame.draw.circle(window, "blue", (point.x, point.y), radius_point)
        else:
            pygame.draw.circle(window, "black", (point.x, point.y), radius_point)

    # Draw the convex hull if it's not None
    if convex_hull is not None:
        convex_hull.draw(window, "green")

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
