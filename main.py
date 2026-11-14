
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import sys

# ==========================================================
# 3D SMART DOLL HOUSE
# ==========================================================

WIDTH, HEIGHT = 1200, 950

day_mode = True
light_on = True
fan_on = True

# CAMERA VIEW
# 1 = Front, 2 = Left, 3 = Right, 4 = Top, 5 = Original 3D
camera_view = 5

fan_angle = 0.0
door_angle = 0.0
door_target = 0.0

table_x = -2.0
table_z = 0.65

group_offsets = {
    "bedroom": [0.0, 0.0, 0.0],
    "bathroom": [0.0, 0.0, 0.0],
    "living": [0.0, 0.0, 0.0],
    "kitchen": [0.0, 0.0, 0.0],
    "swing": [0.0, 0.0, 0.0],
}

selected_group = None
pick_centers = {}
dragging = False
drag_plane_y = 0.15
drag_last_world = None

swing_angle = 0.0
swing_direction = 1.0

# COLORS
WHITE = (0.96, 0.94, 0.90)
WALL = (0.91, 0.82, 0.82)
FLOOR = (0.91, 0.82, 0.72)

ORANGE = (0.85, 0.29, 0.10)
ROOF_LIGHT = (1.0, 0.59, 0.40)

WOOD = (0.48, 0.25, 0.14)
WOOD_LIGHT = (0.72, 0.43, 0.25)

PINK = (0.94, 0.58, 0.68)
TEAL = (0.04, 0.48, 0.43)
BLUE = (0.48, 0.79, 0.90)
YELLOW = (0.96, 0.76, 0.38)

GREEN = (0.25, 0.70, 0.12)
DARK_GREEN = (0.12, 0.43, 0.10)

GRAY = (0.58, 0.58, 0.58)
BLACK = (0.08, 0.10, 0.13)


# ==========================================================
# BASIC OBJECTS
# ==========================================================

def box(x, y, z, w, h, d, color):
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(w, h, d)
    glutSolidCube(1)
    glPopMatrix()


def sphere(x, y, z, radius, color):
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glutSolidSphere(radius, 24, 20)
    glPopMatrix()


def cylinder(x, y, z, radius, height, color):
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)

    q = gluNewQuadric()
    gluCylinder(q, radius, radius, height, 24, 8)
    gluDisk(q, 0, radius, 24, 1)

    glTranslatef(0, 0, height)
    gluDisk(q, 0, radius, 24, 1)

    gluDeleteQuadric(q)
    glPopMatrix()


# ==========================================================
# HOUSE STRUCTURE
# ==========================================================

def draw_structure():

    box(0, 0.0, 0, 12, 0.25, 5.5, FLOOR)
    box(0, 4.05, 0, 12, 0.25, 5.5, WHITE)

    box(0, 2.1, -2.65, 12, 4.0, 0.18, WALL)
    box(0, 6.3, -2.65, 12, 4.2, 0.18, WALL)

    box(-5.95, 6.3, 0, 0.18, 4.2, 5.5, WHITE)
    box(5.95, 6.3, 0, 0.18, 4.2, 5.5, WHITE)

    # Left lower wall with side entrance opening
    box(-5.95, 2.1, -1.75, 0.18, 4.0, 2.0, WHITE)
    box(-5.95, 2.1, 2.05, 0.18, 4.0, 1.40, WHITE)
    box(-5.95, 3.10, 0.35, 0.18, 2.0, 1.60, WHITE)

    box(5.95, 2.1, 0, 0.18, 4.0, 5.5, WHITE)
    box(0, 4.1, 0, 0.16, 8.1, 5.5, WHITE)

    box(0, 4.05, 2.76, 12, 0.22, 0.18, WHITE)
    box(-5.95, 4.1, 2.76, 0.18, 8.1, 0.18, WHITE)
    box(5.95, 4.1, 2.76, 0.18, 8.1, 0.18, WHITE)


# ==========================================================
# ROOF
# ==========================================================

def draw_gable():

    glColor3f(*WALL)
    glBegin(GL_TRIANGLES)
    glVertex3f(-5.85, 8.25, 2.70)
    glVertex3f(5.85, 8.25, 2.70)
    glVertex3f(0, 11.15, 2.70)
    glEnd()


def draw_roof():

    length = math.sqrt(6.0**2 + 3.0**2)
    angle = math.degrees(math.atan2(3.0, 6.0))

    glPushMatrix()
    glTranslatef(-3.0, 9.65, 0)
    glRotatef(angle, 0, 0, 1)
    box(0, 0, 0, length + 0.55, 0.38, 6.0, ROOF_LIGHT)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(3.0, 9.65, 0)
    glRotatef(-angle, 0, 0, 1)
    box(0, 0, 0, length + 0.55, 0.38, 6.0, ROOF_LIGHT)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-3.0, 9.65, 0)
    glRotatef(angle, 0, 0, 1)
    box(0, 0, -0.02, length, 0.25, 5.85, ORANGE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(3.0, 9.65, 0)
    glRotatef(-angle, 0, 0, 1)
    box(0, 0, -0.02, length, 0.25, 5.85, ORANGE)
    glPopMatrix()

    box(0, 11.15, 0, 0.20, 0.20, 6.1, ORANGE)


# ==========================================================
# WINDOW OUTSIDE SCENERY
# ==========================================================

def draw_window_scenery(x, y, w, h, z):

    lighting_was_on = glIsEnabled(GL_LIGHTING)

    glDisable(GL_LIGHTING)

    if day_mode:
        sky = (0.35, 0.72, 0.95)
        hill1 = (0.20, 0.58, 0.22)
        hill2 = (0.12, 0.42, 0.16)
        ground = (0.20, 0.52, 0.15)
        sun_color = (1.0, 0.85, 0.12)
        tree_color = (0.10, 0.42, 0.12)
    else:
        sky = (0.025, 0.045, 0.17)
        hill1 = (0.035, 0.15, 0.10)
        hill2 = (0.025, 0.10, 0.075)
        ground = (0.025, 0.12, 0.055)
        sun_color = (0.88, 0.90, 1.0)
        tree_color = (0.025, 0.13, 0.055)

    left = x - w / 2
    right = x + w / 2
    bottom = y - h / 2
    top = y + h / 2

    # Sky background
    glColor3f(*sky)
    glBegin(GL_QUADS)
    glVertex3f(left, bottom, z)
    glVertex3f(right, bottom, z)
    glVertex3f(right, top, z)
    glVertex3f(left, top, z)
    glEnd()

    # Sun / Moon
    glColor3f(*sun_color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(x + w * 0.29, y + h * 0.25, z - 0.015)

    for i in range(33):
        angle = 2.0 * math.pi * i / 32
        glVertex3f(
            x + w * 0.29 + math.cos(angle) * w * 0.095,
            y + h * 0.25 + math.sin(angle) * w * 0.095,
            z - 0.015
        )
    glEnd()

    # Night stars
    if not day_mode:
        glColor3f(1.0, 1.0, 0.85)
        glPointSize(3)
        glBegin(GL_POINTS)

        for sx, sy in [
            (-0.30, 0.30), (-0.12, 0.38),
            (0.05, 0.22), (0.34, 0.05),
            (-0.38, -0.02), (0.12, 0.40)
        ]:
            glVertex3f(x + sx * w, y + sy * h, z - 0.02)

        glEnd()

    # Distant hills
    glColor3f(*hill1)
    glBegin(GL_TRIANGLES)

    glVertex3f(left, bottom + h * 0.35, z - 0.025)
    glVertex3f(x - w * 0.12, bottom + h * 0.70, z - 0.025)
    glVertex3f(x + w * 0.18, bottom + h * 0.35, z - 0.025)

    glVertex3f(x - w * 0.10, bottom + h * 0.35, z - 0.025)
    glVertex3f(x + w * 0.30, bottom + h * 0.68, z - 0.025)
    glVertex3f(right, bottom + h * 0.35, z - 0.025)

    glEnd()

    # Ground
    glColor3f(*ground)
    glBegin(GL_QUADS)

    glVertex3f(left, bottom, z - 0.03)
    glVertex3f(right, bottom, z - 0.03)
    glVertex3f(right, bottom + h * 0.30, z - 0.03)
    glVertex3f(left, bottom + h * 0.30, z - 0.03)

    glEnd()

    # Small trees
    for tx in [-0.34, 0.02, 0.36]:

        tree_x = x + tx * w
        tree_y = bottom + h * 0.30

        glColor3f(0.30, 0.16, 0.07)
        glBegin(GL_QUADS)

        glVertex3f(tree_x - w * 0.018, tree_y, z - 0.045)
        glVertex3f(tree_x + w * 0.018, tree_y, z - 0.045)
        glVertex3f(tree_x + w * 0.018, tree_y + h * 0.22, z - 0.045)
        glVertex3f(tree_x - w * 0.018, tree_y + h * 0.22, z - 0.045)

        glEnd()

        glColor3f(*tree_color)
        glBegin(GL_TRIANGLES)

        glVertex3f(tree_x - w * 0.12, tree_y + h * 0.12, z - 0.05)
        glVertex3f(tree_x, tree_y + h * 0.48, z - 0.05)
        glVertex3f(tree_x + w * 0.12, tree_y + h * 0.12, z - 0.05)

        glEnd()

    if lighting_was_on:
        glEnable(GL_LIGHTING)


def draw_window(x, y, z):

    draw_window_scenery(x, y, 1.45, 1.30, z - 0.035)

    # Wooden frame
    box(x, y + 0.68, z + 0.05, 1.60, 0.09, 0.09, WOOD_LIGHT)
    box(x, y - 0.68, z + 0.05, 1.60, 0.09, 0.09, WOOD_LIGHT)

    box(x - 0.77, y, z + 0.05, 0.09, 1.40, 0.09, WOOD_LIGHT)
    box(x + 0.77, y, z + 0.05, 0.09, 1.40, 0.09, WOOD_LIGHT)

    box(x, y, z + 0.08, 0.06, 1.30, 0.08, WOOD_LIGHT)
    box(x, y, z + 0.08, 1.45, 0.06, 0.08, WOOD_LIGHT)


def draw_bathroom_window():

    x, y, z = 3.15, 6.80, -2.50

    draw_window_scenery(x, y, 1.25, 0.65, z - 0.035)

    box(3.15, 7.15, -2.43, 1.38, 0.07, 0.08, WHITE)
    box(3.15, 6.45, -2.43, 1.38, 0.07, 0.08, WHITE)

    box(2.49, 6.80, -2.43, 0.07, 0.75, 0.08, WHITE)
    box(3.81, 6.80, -2.43, 0.07, 0.75, 0.08, WHITE)

    box(3.15, 6.80, -2.40, 0.05, 0.62, 0.04, WHITE)


def draw_windows():

    draw_window(-3.0, 6.65, -2.50)
    draw_bathroom_window()
    draw_window(-2.80, 1.75, -2.50)


# ==========================================================
# BEDROOM
# ==========================================================

def draw_bedroom():

    box(-3.15, 4.42, 0.15, 2.4, 0.38, 2.55, WOOD)
    box(-3.15, 4.67, 0.15, 2.35, 0.18, 2.45, WHITE)
    box(-3.15, 4.79, 0.75, 2.28, 0.10, 1.15, TEAL)
    box(-3.15, 4.82, -0.93, 1.15, 0.14, 0.48, WHITE)
    box(-3.15, 5.05, -1.18, 2.50, 0.95, 0.15, WOOD_LIGHT)

    # Wardrobe
    box(-5.10, 5.10, -1.65, 1.0, 1.85, 0.95, WOOD_LIGHT)
    box(-5.10, 5.10, -1.14, 0.90, 1.70, 0.06, (0.80, 0.61, 0.49))

    sphere(-5.30, 5.10, -1.08, 0.055, GRAY)
    sphere(-4.90, 5.10, -1.08, 0.055, GRAY)

    # Bedside drawer
    box(-1.62, 4.50, 0.55, 0.65, 0.65, 0.65, WOOD_LIGHT)
    box(-1.62, 4.52, 0.90, 0.55, 0.42, 0.04, WOOD)

    # Reading table
    box(-0.95, 5.10, -0.90, 1.15, 0.12, 0.85, WOOD_LIGHT)

    for x in [-1.42, -0.48]:
        for z in [-1.23, -0.57]:
            box(x, 4.64, z, 0.07, 0.92, 0.07, WOOD)

    # Chair
    box(-0.95, 4.55, 0.10, 0.65, 0.15, 0.65, WHITE)
    box(-0.95, 4.95, 0.40, 0.65, 0.75, 0.12, WHITE)

    for x in [-1.22, -0.68]:
        for z in [-0.15, 0.35]:
            box(x, 4.375, z, 0.07, 0.40, 0.07, WOOD_LIGHT)

    # Lamp
    cylinder(-0.95, 5.18, -0.90, 0.12, 0.04, GRAY)
    cylinder(-0.95, 5.20, -0.90, 0.025, 0.23, GRAY)
    sphere(-0.95, 5.48, -0.90, 0.15, YELLOW)


# ==========================================================
# BATHROOM
# ==========================================================

def draw_bathroom():

    # Bathtub
    box(3.15, 4.22, -0.35, 2.85, 0.06, 1.85, PINK)
    box(3.15, 4.65, -0.35, 2.55, 0.60, 1.25, WHITE)
    box(3.15, 4.94, -0.35, 2.25, 0.06, 0.95, BLUE)
    box(3.15, 4.96, 0.28, 2.65, 0.12, 0.12, WHITE)

    for x in [2.10, 4.20]:
        for z in [-0.85, 0.15]:
            box(x, 4.36, z, 0.10, 0.25, 0.10, GRAY)

    # Washing machine
    box(0.90, 4.725, -1.65, 0.85, 1.10, 0.85, PINK)
    sphere(0.90, 4.70, -1.20, 0.29, BLUE)
    box(0.90, 5.32, -1.65, 0.90, 0.10, 0.90, WHITE)

    # Shower
    cylinder(4.85, 4.35, -1.75, 0.05, 1.45, GRAY)
    sphere(4.85, 5.90, -1.75, 0.17, GRAY)

    # Toilet
    cylinder(4.80, 4.30, 1.30, 0.36, 0.35, WHITE)
    sphere(4.80, 4.65, 1.30, 0.40, WHITE)
    box(4.80, 4.82, 1.30, 0.75, 0.10, 0.75, WHITE)
    box(4.80, 5.18, 0.70, 0.72, 0.90, 0.30, WHITE)

    # Shelf
    box(3.10, 6.15, -2.28, 1.65, 0.12, 0.40, WOOD_LIGHT)

    for x, color in [
        (2.55, BLUE),
        (3.10, GREEN),
        (3.65, PINK)
    ]:
        box(x, 6.40, -2.22, 0.22, 0.38, 0.20, color)

    # Towel
    box(1.50, 6.10, -2.25, 0.95, 0.06, 0.06, GRAY)
    box(1.50, 5.68, -2.20, 0.65, 0.78, 0.08, PINK)
    box(1.50, 5.29, -2.14, 0.65, 0.04, 0.09, WHITE)


# ==========================================================
# LIVING ROOM
# ==========================================================

def draw_living_room():

    # Sofa
    box(-3.55, 0.58, 0.85, 1.45, 0.48, 1.65, (0.91, 0.82, 0.61))
    box(-4.22, 1.10, 0.85, 0.20, 0.95, 1.65, (0.91, 0.82, 0.61))

    box(-3.55, 0.90, 1.72, 1.45, 0.70, 0.18, WHITE)
    box(-3.55, 0.90, -0.02, 1.45, 0.70, 0.18, WHITE)

    box(-3.50, 0.86, 0.38, 0.95, 0.14, 0.68, WHITE)
    box(-3.50, 0.86, 1.30, 0.95, 0.14, 0.68, (0.90, 0.83, 0.68))

    box(-4.08, 1.32, 0.38, 0.12, 0.60, 0.70, WHITE)
    box(-4.08, 1.32, 1.30, 0.12, 0.60, 0.70, (0.90, 0.83, 0.68))

    # Pink rug
    box(table_x, 0.13, table_z, 2.15, 0.12, 1.85, PINK)
    box(table_x, 0.20, table_z, 1.95, 0.05, 1.65, WHITE)

    # Coffee table
    box(table_x, 0.85, table_z, 1.35, 0.15, 0.95, WOOD_LIGHT)

    for x in [table_x - 0.55, table_x + 0.55]:
        for z in [table_z - 0.38, table_z + 0.38]:
            box(x, 0.53, z, 0.09, 0.62, 0.09, WOOD)

    sphere(table_x, 1.02, table_z, 0.12, BLUE)

    # TV cabinet
    box(-0.48, 0.80, 0.65, 0.65, 1.20, 2.25, WOOD_LIGHT)
    box(-0.48, 1.43, 0.65, 0.78, 0.12, 2.40, WOOD)
    box(-0.48, 0.20, 0.65, 0.72, 0.12, 2.30, WOOD)

    box(-0.10, 0.80, 0.10, 0.06, 0.85, 0.75, WOOD)
    box(-0.10, 0.80, 1.20, 0.06, 0.85, 0.75, WOOD)

    sphere(-0.055, 0.85, 0.10, 0.045, GRAY)
    sphere(-0.055, 0.85, 1.20, 0.045, GRAY)

    # TV
    box(-0.12, 2.15, 0.65, 0.16, 1.35, 2.15, BLACK)
    box(-0.025, 2.15, 0.65, 0.035, 1.15, 1.95, (0.07, 0.10, 0.16))
    box(-0.25, 1.48, 0.65, 0.35, 0.10, 0.70, BLACK)

    # Plant
    cylinder(-1.25, 0.20, -1.55, 0.18, 0.32, YELLOW)

    sphere(-1.25, 0.68, -1.55, 0.22, GREEN)
    sphere(-1.45, 0.63, -1.55, 0.16, DARK_GREEN)
    sphere(-1.05, 0.63, -1.55, 0.16, GREEN)


# ==========================================================
# KITCHEN
# ==========================================================

def draw_kitchen():

    box(3.20, 0.90, -2.0, 4.85, 1.40, 0.85, PINK)
    box(3.20, 1.65, -1.95, 4.95, 0.14, 0.95, WHITE)

    box(2.85, 2.75, -2.20, 3.65, 0.95, 0.55, (0.94, 0.67, 0.61))

    for x in [1.65, 2.85, 4.05]:
        box(x, 2.75, -1.90, 0.05, 0.80, 0.06, WOOD_LIGHT)

    for x in [2.25, 3.45]:
        sphere(x, 2.70, -1.82, 0.05, GRAY)

    # Sink
    box(1.55, 1.78, -1.45, 0.80, 0.08, 0.58, GRAY)
    cylinder(1.55, 1.82, -1.90, 0.04, 0.40, GRAY)

    # Stove
    box(4.65, 1.78, -1.45, 0.90, 0.12, 0.70, BLACK)

    for x in [4.40, 4.90]:
        for z in [-1.65, -1.25]:
            cylinder(x, 1.85, z, 0.11, 0.04, GRAY)

    # Refrigerator
    box(5.10, 1.75, 0.10, 1.05, 3.25, 0.95, WHITE)
    box(5.10, 2.0, 0.59, 0.98, 0.06, 0.06, GRAY)

    box(5.45, 2.85, 0.64, 0.06, 0.72, 0.06, GRAY)
    box(5.45, 1.20, 0.64, 0.06, 0.60, 0.06, GRAY)

    # Dining table
    box(2.80, 1.05, 1.15, 1.95, 0.14, 1.20, WOOD_LIGHT)

    for x in [1.95, 3.65]:
        for z in [0.70, 1.60]:
            box(x, 0.55, z, 0.10, 0.95, 0.10, WOOD)

    # Chair 1
    box(2.80, 0.78, 0.42, 0.62, 0.15, 0.62, WOOD_LIGHT)
    box(2.80, 1.20, 0.13, 0.62, 0.85, 0.12, WOOD_LIGHT)

    for x in [2.55, 3.05]:
        for z in [0.18, 0.65]:
            box(x, 0.40, z, 0.07, 0.70, 0.07, WOOD)

    # Chair 2
    box(2.80, 0.78, 1.88, 0.62, 0.15, 0.62, WOOD_LIGHT)
    box(2.80, 1.20, 2.17, 0.62, 0.85, 0.12, WOOD_LIGHT)

    for x in [2.55, 3.05]:
        for z in [1.65, 2.12]:
            box(x, 0.40, z, 0.07, 0.70, 0.07, WOOD)

    sphere(2.45, 1.20, 1.10, 0.12, BLUE)
    sphere(3.05, 1.20, 1.10, 0.12, GREEN)


# ==========================================================
# STAIRCASE
# ==========================================================

def draw_staircase():

    stair_x = -4.85

    for i in range(8):
        y = 0.18 + i * 0.43
        z = 1.95 - i * 0.43

        box(stair_x, y, z, 0.95, 0.20, 0.52, WOOD_LIGHT)
        box(stair_x, y + 0.115, z + 0.02, 0.97, 0.035, 0.54, WOOD)

    for i in range(4):
        y = 0.55 + i * 0.86
        z = 1.45 - i * 0.86
        box(-5.37, y, z, 0.07, 0.78, 0.07, WOOD)

    box(-5.37, 2.05, -0.05, 0.09, 0.10, 3.10, WOOD_LIGHT)


# ==========================================================
# FANS
# ==========================================================

def draw_fan(x, ceiling_y, z):

    glPushMatrix()
    glTranslatef(x, ceiling_y, z)
    glRotatef(fan_angle, 0, 1, 0)

    cylinder(0, -0.55, 0, 0.04, 0.45, GRAY)
    sphere(0, -0.62, 0, 0.15, GRAY)

    for i in range(4):
        glPushMatrix()
        glRotatef(i * 90, 0, 1, 0)
        box(0.62, -0.66, 0, 1.0, 0.06, 0.24, WOOD_LIGHT)
        glPopMatrix()

    glPopMatrix()


# ==========================================================
# SIDE ENTRANCE DOOR
# ==========================================================

def draw_door():

    door_x = -6.07
    door_z = 0.35

    box(door_x, 1.08, door_z - 0.78, 0.16, 2.16, 0.12, WOOD)
    box(door_x, 1.08, door_z + 0.78, 0.16, 2.16, 0.12, WOOD)
    box(door_x, 2.16, door_z, 0.16, 0.12, 1.65, WOOD_LIGHT)

    box(-6.38, 0.02, door_z, 0.75, 0.16, 1.85, FLOOR)

    glPushMatrix()
    glTranslatef(door_x - 0.06, 0.05, door_z - 0.70)
    glRotatef(door_angle, 0, 1, 0)

    box(0, 0.91, 0.70, 0.09, 1.82, 1.40, WOOD)
    box(-0.05, 1.38, 0.70, 0.025, 0.55, 1.05, WOOD_LIGHT)
    box(-0.05, 0.48, 0.70, 0.025, 0.55, 1.05, WOOD_LIGHT)
    sphere(-0.12, 0.95, 1.18, 0.065, YELLOW)

    glPopMatrix()


# ==========================================================
# GARDEN TREES
# ==========================================================

def draw_tree(x, z, scale=1.0):

    cylinder(x, -0.575, z, 0.16 * scale, 2.0 * scale, WOOD)

    sphere(x, 1.0 * scale, z, 0.85 * scale, GREEN)
    sphere(x - 0.40 * scale, 0.80 * scale, z, 0.58 * scale, DARK_GREEN)
    sphere(x + 0.40 * scale, 0.90 * scale, z, 0.62 * scale, (0.40, 0.80, 0.14))


# ==========================================================
# SWING
# ==========================================================

def draw_swing():

    glPushMatrix()
    glTranslatef(7.0, 0.0, 0.0)

    swing_z = 5.10

    # Mattress under swing
    box(0.0, -0.47, swing_z, 2.35, 0.16, 1.60, PINK)
    box(0.0, -0.375, swing_z, 2.20, 0.035, 1.45, WHITE)

    # Frame
    box(-1.0, 0.80, swing_z, 0.16, 2.70, 0.16, WOOD)
    box(1.0, 0.80, swing_z, 0.16, 2.70, 0.16, WOOD)
    box(0.0, 2.20, swing_z, 2.35, 0.18, 0.22, WOOD_LIGHT)

    # Moving seat
    glPushMatrix()
    glTranslatef(0.0, 2.10, swing_z)
    glRotatef(swing_angle, 1.0, 0.0, 0.0)

    cylinder(-0.48, -1.55, 0.0, 0.035, 1.55, GRAY)
    cylinder(0.48, -1.55, 0.0, 0.035, 1.55, GRAY)

    box(0.0, -1.72, 0.0, 1.20, 0.16, 0.48, WOOD_LIGHT)
    box(0.0, -1.61, 0.0, 1.10, 0.08, 0.40, YELLOW)

    box(-0.55, -1.58, 0.0, 0.10, 0.35, 0.50, WOOD)
    box(0.55, -1.58, 0.0, 0.10, 0.35, 0.50, WOOD)

    glPopMatrix()
    glPopMatrix()


# ==========================================================
# GARDEN
# ==========================================================

def draw_garden():

    box(0, -0.75, 3.8, 22, 0.35, 5.0, GREEN)
    box(0, -0.52, 4.0, 3.3, 0.08, 2.6, (0.75, 0.69, 0.56))

    draw_tree(-8.0, 3.0, 1.25)
    draw_tree(8.0, 3.0, 1.25)
    draw_tree(-7.0, 4.2, 0.70)
    draw_tree(7.0, 4.2, 0.70)

    for x in [-9, -7, -5, 5, 7, 9]:
        sphere(x, -0.15, 4.15, 0.48, GREEN)

    for x in [-6.0, -4.0, 4.0, 6.0]:
        sphere(x, -0.10, 4.0, 0.30, (0.45, 0.82, 0.16))


# ==========================================================
# MOVABLE GROUPS
# ==========================================================

def draw_movable_group(name, draw_function):

    off = group_offsets[name]

    glPushMatrix()
    glTranslatef(off[0], off[1], off[2])
    draw_function()
    glPopMatrix()


# ==========================================================
# COMPLETE HOUSE
# ==========================================================

def draw_house():

    draw_garden()
    draw_structure()

    # Hide gable in Top View
    if camera_view != 4:
        draw_gable()

    draw_windows()

    draw_movable_group("bedroom", draw_bedroom)
    draw_movable_group("bathroom", draw_bathroom)
    draw_movable_group("living", draw_living_room)

    draw_staircase()

    draw_movable_group("kitchen", draw_kitchen)
    draw_movable_group("swing", draw_swing)

    draw_fan(-3.0, 8.25, 0)
    draw_fan(-3.0, 3.92, 0)

    # Hide roof in Top View
    if camera_view != 4:
        draw_roof()

    draw_door()


# ==========================================================
# MOUSE PICKING
# ==========================================================

GROUP_PICK_POINTS = {
    "bedroom": (-3.2, 5.0, 0.0),
    "bathroom": (3.1, 5.0, 0.0),
    "living": (-3.2, 1.0, 0.0),
    "kitchen": (3.2, 1.2, 0.0),
    "swing": (7.0, 1.0, 5.1),
}


def update_pick_centers():

    model = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)

    pick_centers.clear()

    for name, point in GROUP_PICK_POINTS.items():

        off = group_offsets[name]

        try:
            sx, sy, depth = gluProject(
                point[0] + off[0],
                point[1] + off[1],
                point[2] + off[2],
                model,
                projection,
                viewport
            )

            pick_centers[name] = (sx, HEIGHT - sy, depth)

        except Exception:
            pass


def screen_to_world(mx, my, plane_y):

    viewport = glGetIntegerv(GL_VIEWPORT)
    model = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)

    win_y = viewport[3] - my

    near = gluUnProject(mx, win_y, 0.0, model, projection, viewport)
    far = gluUnProject(mx, win_y, 1.0, model, projection, viewport)

    dy = far[1] - near[1]

    if abs(dy) < 1e-8:
        return None

    t = (plane_y - near[1]) / dy

    return (
        near[0] + t * (far[0] - near[0]),
        near[2] + t * (far[2] - near[2])
    )


def mouse(button, state, x, y):

    global selected_group
    global dragging, drag_plane_y, drag_last_world

    if button != GLUT_LEFT_BUTTON:
        return

    if state == GLUT_DOWN:

        update_pick_centers()

        best_name = None
        best_distance = 1e9

        for name, (sx, sy, depth) in pick_centers.items():

            distance = math.hypot(x - sx, y - sy)

            if distance < best_distance and distance < 145:
                best_name = name
                best_distance = distance

        if best_name is not None:

            selected_group = best_name

            if best_name in ("bedroom", "bathroom"):
                drag_plane_y = 4.2
            else:
                drag_plane_y = 0.15

            drag_last_world = screen_to_world(x, y, drag_plane_y)
            dragging = drag_last_world is not None

        else:
            selected_group = None
            dragging = False

    else:
        dragging = False
        drag_last_world = None

    glutPostRedisplay()


def motion(x, y):

    global drag_last_world

    if not dragging or selected_group is None:
        return

    current = screen_to_world(x, y, drag_plane_y)

    if current is None or drag_last_world is None:
        return

    group_offsets[selected_group][0] += current[0] - drag_last_world[0]
    group_offsets[selected_group][2] += current[1] - drag_last_world[1]

    drag_last_world = current
    glutPostRedisplay()


# ==========================================================
# SPECIAL KEYBOARD
# ==========================================================

def special_keyboard(key, x, y):

    if selected_group is None:
        return

    step = 0.15

    if key == GLUT_KEY_LEFT:
        group_offsets[selected_group][0] -= step

    elif key == GLUT_KEY_RIGHT:
        group_offsets[selected_group][0] += step

    elif key == GLUT_KEY_UP:
        group_offsets[selected_group][2] -= step

    elif key == GLUT_KEY_DOWN:
        group_offsets[selected_group][2] += step

    glutPostRedisplay()


# ==========================================================
# DISPLAY
# ==========================================================

def display():

    if day_mode:
        glClearColor(0.55, 0.80, 0.94, 1.0)
    else:
        glClearColor(0.04, 0.06, 0.16, 1.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # CAMERA VIEWS

    if camera_view == 1:
        # FRONT VIEW
        gluLookAt(
          0.0, 7.0, 25.0,
          0.0, 4.5, 0.5,
          0.0, 1.0, 0.0
         )

    elif camera_view == 2:
        # LEFT SIDE VIEW
        gluLookAt(
            -32.0, 8.0, 1.5,
            0.0, 4.5, 1.5,
            0.0, 1.0, 0.0
        )

    elif camera_view == 3:
        # RIGHT SIDE VIEW
        gluLookAt(
            32.0, 8.0, 1.5,
            0.0, 4.5, 1.5,
            0.0, 1.0, 0.0
        )

    elif camera_view == 4:
        # TOP VIEW
        gluLookAt(
            0.0, 35.0, 1.5,
            0.0, 3.5, 1.5,
            0.0, 0.0, -1.0
        )

    else:
        # ORIGINAL 3D VIEW
        gluLookAt(
            -13.5, 10.0, 24.0,
            0.0, 4.5, 0.5,
            0.0, 1.0, 0.0
        )

    # LIGHTING
    if light_on:

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glColorMaterial(
            GL_FRONT_AND_BACK,
            GL_AMBIENT_AND_DIFFUSE
        )

        if day_mode:
            ambient = (0.75, 0.75, 0.75, 1)
            diffuse = (0.70, 0.70, 0.70, 1)
        else:
            ambient = (0.45, 0.45, 0.55, 1)
            diffuse = (0.50, 0.50, 0.60, 1)

        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 12, 10, 1))

    else:
        glDisable(GL_LIGHTING)

    draw_house()
    update_pick_centers()

    glutSwapBuffers()


# ==========================================================
# ANIMATION
# ==========================================================

def update(value):

    global fan_angle, door_angle
    global swing_angle, swing_direction

    # Swing animation
    swing_angle += 0.65 * swing_direction

    if swing_angle >= 18.0:
        swing_angle = 18.0
        swing_direction = -1.0

    elif swing_angle <= -18.0:
        swing_angle = -18.0
        swing_direction = 1.0

    # Fan animation
    if fan_on:
        fan_angle = (fan_angle + 4.0) % 360

    # Door animation
    if door_angle < door_target:
        door_angle = min(door_angle + 3.0, door_target)

    elif door_angle > door_target:
        door_angle = max(door_angle - 3.0, door_target)

    glutPostRedisplay()
    glutTimerFunc(30, update, 0)


# ==========================================================
# KEYBOARD CONTROLS
# ==========================================================

def keyboard(key, x, y):

    global table_x, table_z
    global door_target
    global day_mode, light_on, fan_on
    global camera_view

    step = 0.15

    # CAMERA CONTROLS
    if key == b'5':
        camera_view = 1

    elif key == b'6':
        camera_view = 2

    elif key == b'7':
        camera_view = 3

    elif key == b'8':
        camera_view = 4

    elif key == b'9':
        camera_view = 5

    # Move selected object or coffee table
    elif key in (b'w', b'W'):

        if selected_group:
            group_offsets[selected_group][2] -= step
        else:
            table_z -= step

    elif key in (b's', b'S'):

        if selected_group:
            group_offsets[selected_group][2] += step
        else:
            table_z += step

    elif key in (b'a', b'A'):

        if selected_group:
            group_offsets[selected_group][0] -= step
        else:
            table_x -= step

    elif key in (b'd', b'D'):

        if selected_group:
            group_offsets[selected_group][0] += step
        else:
            table_x += step

    elif key in (b'q', b'Q') and selected_group:
        group_offsets[selected_group][1] -= step

    elif key in (b'e', b'E') and selected_group:
        group_offsets[selected_group][1] += step

    # Swing movement
    elif key in (b'j', b'J'):
        group_offsets["swing"][0] -= step

    elif key in (b'k', b'K'):
        group_offsets["swing"][0] += step

    elif key in (b'n', b'N'):
        group_offsets["swing"][2] -= step

    elif key in (b'm', b'M'):
        group_offsets["swing"][2] += step

    # Reset coffee table
    elif key in (b'r', b'R'):
        table_x = -2.0
        table_z = 0.65

    # Open side door
    elif key in (b'o', b'O'):
        door_target = -90.0

    # Close side door
    elif key in (b'c', b'C'):
        door_target = 0.0

    # Day mode
    elif key == b'1':
        day_mode = True

    # Night mode
    elif key == b'2':
        day_mode = False

    # Fan
    elif key in (b'f', b'F'):
        fan_on = not fan_on

    # Lights
    elif key in (b'l', b'L'):
        light_on = not light_on

    # Exit
    elif key == b'\x1b':
        sys.exit(0)

    glutPostRedisplay()


# ==========================================================
# RESHAPE
# ==========================================================

def reshape(width, height):

    global WIDTH, HEIGHT

    WIDTH = max(width, 1)
    HEIGHT = max(height, 1)

    glViewport(0, 0, WIDTH, HEIGHT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(
        42,
        WIDTH / HEIGHT,
        0.1,
        150
    )

    glMatrixMode(GL_MODELVIEW)


# ==========================================================
# MAIN
# ==========================================================

def main():

    glutInit(sys.argv)

    glutInitDisplayMode(
        GLUT_DOUBLE |
        GLUT_RGB |
        GLUT_DEPTH
    )

    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(50, 30)

    glutCreateWindow(
        b"Smart Doll House - Multi Camera View"
    )

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)

    glShadeModel(GL_SMOOTH)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    glColorMaterial(
        GL_FRONT_AND_BACK,
        GL_AMBIENT_AND_DIFFUSE
    )

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keyboard)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)

    glutTimerFunc(30, update, 0)

    glutMainLoop()


if __name__ == "__main__":
    main()
