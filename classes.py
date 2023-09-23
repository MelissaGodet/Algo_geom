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
                             (segment.point2.x, segment.point2.y), 2)

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

    def triangulation(self):
        lt = []
        n = len(self.segments)
        for i in range(2, n - 1):
            t = Triangle(self.segments[0].point1, self.segments[i].point1, self.segments[i].point2)
            lt.append(t)
        return Triangulation(lt)


class Triangle:
    def __init__(self, p1: Point, p2: Point, p3: Point):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.n1_index = None
        self.n2_index = None
        self.n3_index = None

    def __eq__(self, other):
        if isinstance(other, Triangle):
            return (self.p1 == other.p1 and self.p2 == other.p2 and self.p3 == other.p3) or \
                (self.p1 == other.p1 and self.p2 == other.p3 and self.p3 == other.p2) or \
                (self.p1 == other.p2 and self.p2 == other.p1 and self.p3 == other.p3) or \
                (self.p1 == other.p2 and self.p2 == other.p3 and self.p3 == other.p1) or \
                (self.p1 == other.p3 and self.p2 == other.p1 and self.p3 == other.p2) or \
                (self.p1 == other.p3 and self.p2 == other.p2 and self.p3 == other.p1)
        return False

    def add_a_neighbor1(self, t):
        self.n1_index = t

    def add_a_neighbor2(self, t):
        self.n2_index = t

    def add_a_neighbor3(self, t):
        self.n3_index = t

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

    def print(self):
        print("p1 : (" + str(self.p1.x) + ", " + str(self.p1.y) + ")\n")
        print("p2 : (" + str(self.p2.x) + ", " + str(self.p2.y) + ")\n")
        print("p3 : (" + str(self.p3.x) + ", " + str(self.p3.y) + ")\n")
        if self.n1_index is not None:
            print("1st neighbor has the index : " + str(self.n1_index))
        if self.n2_index is not None:
            print("2nd neighbor has the index : " + str(self.n2_index))
        if self.n3_index is not None:
            print("3rd neighbor has the index : " + str(self.n3_index))

    def draw(self, window):
        pygame.draw.line(window, (0, 0, 0), (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), 2)
        pygame.draw.line(window, (0, 0, 0), (self.p2.x, self.p2.y), (self.p3.x, self.p3.y), 2)
        pygame.draw.line(window, (0, 0, 0), (self.p3.x, self.p3.y), (self.p1.x, self.p1.y), 2)


class Triangulation:
    def __init__(self, triangles):
        self.triangles = triangles

    def who_contains(self, p):
        triangle_founded = False
        right_triangle = None
        n = len(self.triangles)
        i = 0
        while not triangle_founded and i < n:
            triangle_founded = self.triangles[i].contains(p)
            if triangle_founded:
                right_triangle = i
            i += 1
        return right_triangle

    def insert_a_point(self, p):
        n = len(self.triangles)
        right_triangle_index = self.who_contains(p)
        if right_triangle_index is not None:
            right_triangle = self.triangles[right_triangle_index]
            t1 = Triangle(p, right_triangle.p1, right_triangle.p2)
            t2 = Triangle(p, right_triangle.p2, right_triangle.p3)
            t3 = Triangle(p, right_triangle.p3, right_triangle.p1)
            self.triangles.append(t1)
            self.triangles.append(t2)
            self.triangles.append(t3)
            self.triangles.pop(right_triangle_index)
        return self

    def lawson_flip(self, t1_index, t2_index):
        flip = False
        t1 = self.triangles[t1_index]
        t2 = self.triangles[t2_index]
        l1 = [t1.p1, t1.p2, t1.p3]
        l2 = [t2.p1, t2.p2, t2.p3]

        # Variables pour les indices des sommets
        p1_common_index, p2_common_index, p_index_1, p_index_2 = None, None, None, None

        # Recherche des indices des sommets communs et des autres sommets
        for i in range(3):
            if l2[i] in l1:
                if p1_common_index is None:
                    p1_common_index = i
                else:
                    p2_common_index = i
            else:
                p_index_2 = i
            if l1[i] not in l2:
                p_index_1 = i

        # Vérification du test de Delaunay
        if p1_common_index is not None and p2_common_index is not None and p_index_1 is not None and p_index_2 is not None and p1_common_index != p2_common_index:
            if t1.delaunay_test(l2[p_index_2]) or t2.delaunay_test(l1[p_index_1]):
                flip = True
                new_t1 = Triangle(l1[p1_common_index], l2[p_index_1], l1[p_index_2])
                new_t2 = Triangle(l1[p2_common_index], l2[p_index_1], l1[p_index_2])

                nl1 = [t1.n1_index, t1.n2_index, t1.n3_index]
                nl2 = [t2.n1_index, t2.n2_index, t2.n3_index]

                # Mise à jour des triangles dans la liste
                self.triangles[t1_index] = new_t1
                self.triangles[t2_index] = new_t2

                # Mise à jour des indices des voisins
                for j in range(3):
                    if nl1[j] is not None:
                        self.update_neighbors(nl1[j])
                    if nl2[j] is not None:
                        self.update_neighbors(nl2[j])

        return self, flip
    '''
    def lawson_flip(self, t1_index, t2_index):
        n = 3
        flip = False
        t1 = self.triangles[t1_index]
        t2 = self.triangles[t2_index]
        l1 = [t1.p1, t1.p2, t1.p3]
        l2 = [t2.p1, t2.p2, t2.p3]
        for i in range(3):
            p1_common_index, p2_common_index, p_index_1, p_index_2 = None, None, None, None
            if not flip:
                if l2[i] in l1:
                    if p1_common_index is None:
                        p1_common_index = i
                    else:
                        p2_common_index = i
                else:
                    p_index_2 = i
                if l1[i] not in l2:
                    p_index_1 = i
                if p1_common_index != None and p2_common_index != None and p_index_1 != None and p_index_2 != None and p1_common_index != p2_common_index:
                    if t1.delaunay_test(l2[p_index_2]) or t2.delaunay_test(l1[p_index_1]):
                        flip = True
                        new_t1 = Triangle(l1[p1_common_index], l2[p_index_1], l1[p_index_2])
                        new_t2 = Triangle(l1[p2_common_index], l2[p_index_1], l1[p_index_2])
                        nl1 = [t1.n1_index, t1.n2_index, t1.n3_index]
                        nl2 = [t2.n1_index, t2.n2_index, t2.n3_index]
                        for j in range(3):
                            nt1 = self.triangles[nl1[j]]
                            nt2 = self.triangles[nl2[j]]
                            if nt1 != t2:
                                self.update_neighbors(nl1[j])
                            if nt2 != t1:
                                self.update_neighbors(nl2[j])
                        self.triangles[t1_index] = new_t1
                        self.triangles[t2_index] = new_t2
                        self.update_neighbors(t1_index)
                        self.update_neighbors(t2_index)
        return self, flip
'''
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

    def is_neighbors(self, i, j):
        is_neighbors = False
        tri_i = self.triangles[i]
        tri_j = self.triangles[j]
        tri_i_points = [tri_i.p1, tri_i.p2, tri_i.p3]
        tri_j_points = [tri_j.p1, tri_j.p2, tri_j.p3]
        if (tri_i_points[0] in tri_j_points and tri_i_points[1] in tri_j_points and tri_i_points[2] not in tri_j_points) or (tri_i_points[0] in tri_j_points and tri_i_points[2] in tri_j_points and tri_i_points[1] not in tri_j_points) or (tri_i_points[2] in tri_j_points and tri_i_points[1] in tri_j_points and tri_i_points[0] not in tri_j_points):
            is_neighbors = True
        return is_neighbors

    def update_neighbors(self, ind):
        tri = self.triangles[ind]
        n = len(self.triangles)
        c = 0
        for i in range(n):
            if self.is_neighbors(ind, i):
                c += 1
                if c == 1:
                    tri.add_a_neighbor1(i)
                if c == 2:
                    tri.add_a_neighbor2(i)
                if c == 3:
                    tri.add_a_neighbor3(i)
        for i in range(c, 3):
            if c == 1:
                tri.add_a_neighbor1 = None
            if c == 2:
                tri.add_a_neighbor2 = None
            if c == 3:
                tri.add_a_neighbor3 = None






    def add_neighbors(self):
        n = len(self.triangles)
        for t1 in self.triangles:
            for i in range(n):
                t2 = self.triangles[i]
                l1 = [t1.p1, t1.p2, t1.p3]
                l2 = [t2.p1, t2.p2, t2.p3]
                if (l1[0] in l2 and l1[1] in l2 and l1[2] not in l2) or (l1[0] in l2 and l1[2] in l2 and l1[1] not in l2) or (l1[2] in l2 and l1[1] in l2 and l1[0] not in l2):
                    if t1.n1_index is None:
                        t1.n1_index = i
                    elif t1.n2_index is None:
                        t1.n2_index = i
                    else:
                        t1.n3_index = i
        return self

    def draw(self, window):
        for t in self.triangles:
            t.draw(window)


    def recursive_lawson_flip(self, i):
        n = 3
        triangulation = self
        l = [self.triangles[i].n1_index, self.triangles[i].n2_index, self.triangles[i].n3_index]
        for k in range(n):
            if l[k] is not None:
                triangulation, flip = self.lawson_flip(i, l[k])
                if flip:
                    l1 = [self.triangles[i].n1_index, self.triangles[i].n2_index, self.triangles[i].n3_index]
                    l2 = [self.triangles[l[k]].n1_index, self.triangles[l[k]].n2_index, self.triangles[l[k]].n3_index]
                    for j in range(n):
                        if l1[j] is not None and l1[j] not in l2:
                            triangulation = triangulation.recursive_lawson_flip(l1[j])
                        if l2[j] is not None and l2[j] not in l1:
                            triangulation = triangulation.recursive_lawson_flip(l2[j])
        return triangulation


'''
        flip1, flip2, flip3 = False, False, False
        triangulation = self
        i1, i2, i3 = self.triangles[i].n1_index, self.triangles[i].n2_index, self.triangles[i].n3_index
        if i1 is not None:
            triangulation, flip1 = self.lawson_flip(i, i1)
            if not flip1:
                triangulation = triangulation.recursive_lawson_flip(i1)
        if i2 is not None:
            triangulation, flip2 = triangulation.lawson_flip(i, i2)
            if not flip2:
                triangulation = triangulation.recursive_lawson_flip(i2)
        if i3 is not None:
            triangulation, flip3 = triangulation.lawson_flip(i, i3)
            if not flip3:
                triangulation = triangulation.recursive_lawson_flip(i3)

        if not flip1 and not flip2 and not flip3:
            return triangulation
'''


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
triangulation1 = Triangulation([t1])
p = Point(0, 3)
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