import pyglet
from pyglet.gl import *
from math import tan, radians, sqrt

class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def dot(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x*scalar, self.y*scalar, self.z*scalar)

    @property
    def length(self):
        return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    @property
    def normal(self):
        return self * (1.0/self.length)

window = pyglet.window.Window(width=400, height=400)

vertices = [
    Vector(0, 0, -5),
    Vector(0, 0, -5),
    Vector(1, 0, -10),
    Vector(1, 1, -5),
    Vector(0, 1, -25),
    Vector(-1, 1, -3),
    Vector(0, -1, -4),
]

mouse_direction = Vector(0, 0, 0)
hilight_index = None

glClearColor(0.2, 0.4, 0.5, 1.0)
glPointSize(12.0)
glEnable(GL_POINT_SMOOTH)

fovy = 50
aspect = float(window.width) / window.height

def set_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, aspect, 1, 25)
    glMatrixMode(GL_MODELVIEW)

def unproject(x, y):
    x = 2 * (float(x) / window.width) - 1
    y = 2 * (float(y) / window.height) - 1

    tangent = tan(radians(fovy) / 2)
    dx = aspect * tangent * x
    dy = tangent * y
    dz = -1.0
    return Vector(dx, dy, dz).normal

def pick_nearest():
    """
    Picks the vertex that has the shortest distance
    to the ray.
    
    There are some things with dot product
    that allow you to determine the distance
    from a ray if you need to know.
    You have ray's direction and a vertex. Ray starts
    from origo (0, 0, 0). To get the distance, you can
    project the vector to the ray. The projected point
    is the nearest point at vertex picked from the ray.
    Take their difference and calculate it's length.
    here's some math for you. 
    Projection of A to the B: B * (A.dot(B) / B.dot(B))
    When B is normalized, you can just do: B.dot(B)
    because x*x+y*y+z*z of a normalized vector is 1.

    Intuition on dot product: If it is zero, the angle
    between vectors is 90 degrees. If it is positive,
    then that's less than 90 degrees. If negative,
    then more than 90 degrees.
    """
    global hilight_index
    p = Vector(0, 0, 0) # mouse ray position in scene
    nearest = 0.5
    nearest_index = None
    for index, vertex in enumerate(vertices):
        dp = mouse_direction.dot((vertex - p).normal)
        if dp > nearest:
            nearest = dp
            nearest_index = index
    hilight_index = nearest_index

'''@window.event
def on_mouse_motion(x, y, rx, ry):
    global mouse_direction
    mouse_direction = unproject(x, y)
    pick_nearest()'''

@window.event
def on_mouse_release(x, y, button, modifiers):
    global mouse_direction
    if button == pyglet.window.mouse.LEFT:
        mouse_direction = unproject(x, y)
        pick_nearest()
    else:
        pass

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    set_projection()

    glBegin(GL_POINTS)

    glColor3f(0, 0, 0)

    for index, vertex in enumerate(vertices):
        glVertex3f(*vertex)

    if hilight_index != None:
        glColor3f(1, 1, 1)
        glVertex3f(*vertices[hilight_index])

    glColor3f(0.8, 0.2, 0.2)

    dx, dy, dz = mouse_direction
    glVertex3f(dx*25, dy*25, dz*25)

    glEnd()

pyglet.app.run()
