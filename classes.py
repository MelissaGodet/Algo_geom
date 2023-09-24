import math
from typing import List

import pygame


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        return self.y < other.y

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False

    def angle(self):
        return math.atan2(self.y, self.x)

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def print(self):
        print("(" + str(self.x) + ", " + str(self.y) + ")")


def lowest_point(points):
    lowest_p = points[0]
    n = len(points)
    for i in range(n):
        if points[i].y < lowest_p.y:
            lowest_p = points[i]
    return lowest_p


def cross_product(p1, p2, p3):
    return (p2.x - p1.x) * (p3.y - p2.y) - (p2.y - p1.y) * (p3.x - p2.x)


class Segment:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2


class Polygon:
    def __init__(self, segments):
        self.segments = segments

    def draw(self, window, color):
        for segment in self.segments:
            pygame.draw.line(window, color, (segment.point1.x, segment.point1.y),
                             (segment.point2.x, segment.point2.y), 1)

    def color(self):
        n = len(self.segments)
        color = "black"
        if n > 1:
            positive_count = 0
            negative_count = 0

            for i in range(n):
                p1 = self.segments[i].point1
                p2 = self.segments[i].point2
                p3 = self.segments[(i + 1) % n].point2  # Le point suivant

                cp = cross_product(p1, p2, p3)

                if cp > 0:
                    positive_count += 1
                elif cp < 0:
                    negative_count += 1

            if positive_count == 0 or negative_count == 0:
                color = "green"
            else:
                color = "red"
        return color

    def inside_convex(self, p: Point):
        is_inside = True
        positive_count = 0
        negative_count = 0
        for s in self.segments:
            if cross_product(s.point1, s.point2, p) >= 0:
                positive_count += 1
            else:
                negative_count += 1
        if negative_count > 0 and positive_count > 0:
            is_inside = False
        return is_inside

    def inside_concave(self, p: Point):
        intersection_count = 0
        for s in self.segments:
            p1, p2 = s.point1, s.point2
            if p1.y <= p.y <= p2.y or p2.y <= p.y <= p1.y:
                if p1.y != p2.y:
                    x = p1.x + (p.y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y)
                    if p.x < x:
                        intersection_count += 1
        print(intersection_count)
        return intersection_count % 2 == 1

    def color_point(self, p):
        color = "black"
        if self.color() == "green":
            is_inside = self.inside_convex(p)
        else:
            is_inside = self.inside_concave(p)
        if is_inside:
            color = "yellow"
        return color

    def triangulation(self, window, color):
        lt = []
        n = len(self.segments)
        for i in range(2, n - 1):
            t = Triangle(self.segments[0].point1, self.segments[i].point1, self.segments[i].point2)
            t.draw(window, color)
            lt.append(t)
            pygame.display.flip()
            pygame.time.delay(500)  # Delay to slow down the animation
        return Triangulation(lt)


class Triangle:
    def __init__(self, p1: Point, p2: Point, p3: Point):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.n1 = None
        self.n2 = None
        self.n3 = None

    def __eq__(self, other):
        if isinstance(other, Triangle):
            return (self.p1 == other.p1 and self.p2 == other.p2 and self.p3 == other.p3) or \
                (self.p1 == other.p1 and self.p2 == other.p3 and self.p3 == other.p2) or \
                (self.p1 == other.p2 and self.p2 == other.p1 and self.p3 == other.p3) or \
                (self.p1 == other.p2 and self.p2 == other.p3 and self.p3 == other.p1) or \
                (self.p1 == other.p3 and self.p2 == other.p1 and self.p3 == other.p2) or \
                (self.p1 == other.p3 and self.p2 == other.p2 and self.p3 == other.p1)
        return False

    def area(self):
        a = self.p1.distance(self.p2)
        b = self.p2.distance(self.p3)
        c = self.p3.distance(self.p1)

        s = (a + b + c) / 2

        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        return area

    def get_neighbors(self):
        neighbors = []
        if self.n1 is not None:
            neighbors.append(self.n1)
        if self.n2 is not None:
            neighbors.append(self.n2)
        if self.n3 is not None:
            neighbors.append(self.n3)
        return neighbors

    def add_a_neighbour1(self, t):
        self.n1 = t

    def add_a_neighbour2(self, t):
        self.n2 = t

    def add_a_neighbour3(self, t):
        self.n3 = t

    def add_a_neighbour(self, t):
        if self.n1 is None:
            self.add_a_neighbour1(t)
        elif self.n2 is None:
            self.add_a_neighbour2(t)
        elif self.n3 is None:
            self.add_a_neighbour3(t)
        else:
            raise ValueError("All the neighbors are already defined")

    def contains(self, p):
        contains = False
        cp1, cp2, cp3 = cross_product(self.p1, self.p2, p), cross_product(self.p2, self.p3, p), cross_product(self.p3,
                                                                                                              self.p1,
                                                                                                              p)

        if (cp1 >= 0 and cp2 >= 0 and cp3 >= 0) or (cp1 <= 0 and cp2 <= 0 and cp3 <= 0):
            contains = True
        return contains

    def circumcenter(self):
        m1 = Point((self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2)
        m2 = Point((self.p2.x + self.p3.x) / 2, (self.p2.y + self.p3.y) / 2)

        v = Point(self.p2.y - self.p1.y, self.p1.x - self.p2.x)
        w = Point(self.p3.y - self.p2.y, self.p2.x - self.p3.x)
        det = v.x * w.y - v.y * w.x
        delta_x = m2.x - m1.x
        delta_y = m2.y - m1.y
        t = (delta_x * w.y - delta_y * w.x) / det

        center_x = m1.x + t * v.x
        center_y = m1.y + t * v.y

        return Point(center_x, center_y)

    def delaunay_test(self, p):
        is_inside_the_circle = False
        center = self.circumcenter()
        d = math.sqrt((center.x - p.x) ** 2 + (center.y - p.y) ** 2)
        radius = math.sqrt((self.p1.x - center.x) ** 2 + (self.p1.y - center.y) ** 2)
        if d < radius:
            is_inside_the_circle = True
        return is_inside_the_circle

    def print(self, is_original_triangle: bool = True):
        print("p1 : (" + str(self.p1.x) + ", " + str(self.p1.y) + ")\n")
        print("p2 : (" + str(self.p2.x) + ", " + str(self.p2.y) + ")\n")
        print("p3 : (" + str(self.p3.x) + ", " + str(self.p3.y) + ")\n")
        if self.n1 is not None and is_original_triangle:
            print("1st neighbor is : ")
            self.n1.print(False)
        if self.n2 is not None and is_original_triangle:
            print("2nd neighbor is : ")
            self.n2.print(False)
        if self.n3 is not None and is_original_triangle:
            print("3rd neighbor is : ")
            self.n3.print(False)

    def draw(self, window, color):
        pygame.draw.line(window, color, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), 1)
        pygame.draw.line(window, color, (self.p2.x, self.p2.y), (self.p3.x, self.p3.y), 1)
        pygame.draw.line(window, color, (self.p3.x, self.p3.y), (self.p1.x, self.p1.y), 1)


def intersection(list1, list2):
    return [value for value in list1 if value in list2]


def difference(list1, list2):
    return [value for value in list1 if value not in list2] + [value for value in list2 if value not in list1]


class Triangulation:
    def __init__(self, triangles: list):
        self.triangles = triangles

    def who_contains(self, p):
        triangle_founded = False
        right_triangle = None
        n = len(self.triangles)
        i = 0
        while not triangle_founded and i < n:
            triangle_founded = self.triangles[i].contains(p)
            if triangle_founded:
                right_triangle = self.triangles[i]
            i += 1

        if right_triangle is None:
            raise ValueError("The point must be inside the triangulation")
        return right_triangle

    def remove_triangle(self, t: Triangle):
        for i in range(len(self.triangles)):
            if self.triangles[i] == t:
                self.triangles.pop(i)
                break

    def remove_point(self, point_to_remove: Point):
        triangles_to_remove = []
        for t in self.triangles:
            triangle_points = [t.p1, t.p2, t.p3]
            if point_to_remove in triangle_points:
                triangles_to_remove.append(t)

        for t in triangles_to_remove:
            self.remove_triangle(t)

    def insert_a_point(self, p: Point):
        right_triangle = self.who_contains(p)
        t1 = Triangle(p, right_triangle.p1, right_triangle.p2)
        t2 = Triangle(p, right_triangle.p2, right_triangle.p3)
        t3 = Triangle(p, right_triangle.p3, right_triangle.p1)
        self.remove_triangle(right_triangle)
        self.triangles.append(t1)
        self.triangles.append(t2)
        self.triangles.append(t3)

        return self

    def insert_a_point2(self, p: Point):
        right_triangle = self.who_contains(p)
        t1 = Triangle(p, right_triangle.p1, right_triangle.p2)
        t2 = Triangle(p, right_triangle.p2, right_triangle.p3)
        t3 = Triangle(p, right_triangle.p3, right_triangle.p1)
        neighbors = right_triangle.get_neighbors()
        self.remove_triangle(right_triangle)
        self.triangles.append(t1)
        self.triangles.append(t2)
        self.triangles.append(t3)
        self.update_neighbors(t1)
        self.update_neighbors(t2)
        self.update_neighbors(t3)
        for neighbour in neighbors:
            self.update_neighbors(neighbour)
        return self, [t1, t2, t3]

    def lawson_flip(self, t1: Triangle, t2: Triangle):
        flip = False
        l1 = [t1.p1, t1.p2, t1.p3]
        l2 = [t2.p1, t2.p2, t2.p3]
        common_points = intersection(l1, l2)
        opposite_points = difference(l1, l2)
        neighbors = difference([t1.n1, t1.n2, t1.n3, t2.n1, t2.n2, t2.n3], [t1, t2])
        flip = t1.delaunay_test(opposite_points[1]) or t2.delaunay_test(opposite_points[0])
        if flip:
            self.remove_triangle(t1)
            self.remove_triangle(t2)
            new_t1 = Triangle(common_points[0], opposite_points[0], opposite_points[1])
            new_t2 = Triangle(common_points[1], opposite_points[0], opposite_points[1])
            self.update_neighbors(new_t1)
            self.update_neighbors(new_t2)
            new_t1.add_a_neighbour(new_t2)
            new_t2.add_a_neighbour(new_t1)
            self.triangles.append(new_t1)
            self.triangles.append(new_t2)
            for neighbour in neighbors:
                if neighbour is not None:
                    self.update_neighbors(neighbour)
        return self, flip

    def rec_lawson_flip(self, t1: Triangle, t2: Triangle):
        triangulation, flip = self.lawson_flip(t1, t2)
        neighbors = t2.get_neighbors()
        if flip:
            new_t1 = triangulation.triangles[-2]
            new_t2 = triangulation.triangles[-1]
            new_triangles = [new_t1, new_t2]
            for new_triangle in new_triangles:
                new_neighbors = new_triangle.get_neighbors()
                neighbour = intersection(neighbors, new_neighbors)
                if neighbour:
                    triangulation = triangulation.rec_lawson_flip(new_triangle, neighbour[0])
            return triangulation
        else:
            return triangulation

    def get_points(self):
        n = len(self.triangles)
        points = []
        for i in range(n):
            if self.triangles[i].p1 not in points:
                points.append(self.triangles[i].p1)
            if self.triangles[i].p2 not in points:
                points.append(self.triangles[i].p2)
            if self.triangles[i].p3 not in points:
                points.append(self.triangles[i].p3)

        return points

    def print(self):
        n = len(self.triangles)
        for i in range(n):
            t = self.triangles[i]
            print("Triangle :" + str(i))
            t.print()

    def is_neighbour(self, t1: Triangle, t2: Triangle):
        is_neighbour = False
        t1_points = [t1.p1, t1.p2, t1.p3]
        t2_points = [t2.p1, t2.p2, t2.p3]
        if len(intersection(t1_points, t2_points)) == 2:
            is_neighbour = True
        return is_neighbour

    def update_neighbors(self, t: Triangle):
        c = 0
        for triangle in self.triangles:
            if self.is_neighbour(t, triangle):
                c += 1
                if c == 1:
                    t.add_a_neighbour1(triangle)
                if c == 2:
                    t.add_a_neighbour2(triangle)
                if c == 3:
                    t.add_a_neighbour3(triangle)
        if c == 1:
            t.add_a_neighbour2(None)
            t.add_a_neighbour3(None)
        if c == 2:
            t.add_a_neighbour3(None)

    def add_neighbors(self):
        for t1 in self.triangles:
            for t2 in self.triangles:
                l1 = [t1.p1, t1.p2, t1.p3]
                l2 = [t2.p1, t2.p2, t2.p3]
                if len(intersection(l1, l2)) == 2:
                    if t1.n1 is None:
                        t1.n1 = t2
                    elif t1.n2 is None:
                        t1.n2 = t2
                    else:
                        t1.n3 = t2
        return self

    def draw(self, window, color):
        for t in self.triangles:
            t.draw(window, color)


class Voronoi:
    def __init__(self, triangulation: Triangulation):
        self.triangulation = triangulation

    def draw(self, window, color):
        self.triangulation.draw(window, color)


def angle(p, current_point):
    v_unit = (1, 0)
    v = (p.x - current_point.x, p.y - current_point.y)
    norme = math.sqrt((p.x - current_point.x) ** 2 + (p.y - current_point.y) ** 2)
    if norme == 0:
        return 0.0  # Évitez une division par zéro
    angle = math.acos((v[0] * v_unit[0] + v[1] * v_unit[1]) / norme)
    return angle


def graham_scan_without_drawing(points):
    if len(points) < 3:
        return None

    # Lowest point
    lowest = lowest_point(points)

    # Sorted point from the smallest to the biggest with the horizontal
    sorted_points = sorted(points, key=lambda p: angle(p, lowest))

    # Points of the hull initialized
    stack = [lowest, sorted_points[0], sorted_points[1]]

    for i in range(2, len(sorted_points)):
        # Withdraw the segment that shouldn't be in the convex hull
        while len(stack) > 1 and cross_product(stack[-2], stack[-1], sorted_points[i]) <= 0:
            stack.pop()
        # Add the next point
        stack.append(sorted_points[i])

    # Add the last point to close the polygon
    stack.append(lowest)

    segments = [Segment(stack[i], stack[i + 1]) for i in range(len(stack) - 1)]

    # Creation of the polygon
    convex_hull = Polygon(segments)

    return convex_hull


t1 = Triangle(Point(0, 0), Point(4, 0), Point(2, 2))
t2 = Triangle(Point(0, 0), Point(4, 0), Point(2, -1))
triangulation1 = Triangulation([t1, t2])
triangulation1.add_neighbors()
p = Point(1, 1)
p2 = Point(1.5, 1.5)
triangulation1.insert_a_point2(p)
triangulation1.insert_a_point2(p2)
triangulation1.print()
'''
b = triangulation1.who_contains(p)
print("who : " + str(b))
radius = t1.circumcenter()
print("radius: " + str(radius))
c = t1.delaunay_test(p)
print(c)
triangulation2 = Triangulation([t1, t2])
triangulation2.print()
triangulation3 = triangulation2.lawson_flip(0, 1)
triangulation3[0].print()
'''
