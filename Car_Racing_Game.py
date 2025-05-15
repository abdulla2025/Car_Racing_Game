#MADE BY 21201729, 21101231
#CSE423

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import time
import random

# Game variables
last_collision_time = 0
headlights_on = False 
game_paused = False  
xp = -0.55
crspeed = 60
crmove = 4
y11 = -3.3
zp = 2
tpx = 0.15 # 
carpos = 0
view = 10.0
score = 0
totalMeter = 0
carspeed = 45
sky_red = 0
sky_green = 0.8
sky_blue = 1.0
roadlight = 50
lives = 3
free_camera_mode = False
camera_rotation_angle = 0.0
camera_height = 2.0  # Adjustable camera height
rain_mode = False
rain_drops = []
rain_speed = 5.0
rain_density = 8000  # Number of raindrops
first_person = False
camera_distance = 7.0
camera_angle = 0.0
cheat_mode = False
cheat_vision = False
handbrake_active = False
handbrake_timer = 0
debug_info = False
auto_avoid = False
avoid_timer = 0
target_x = -0.55 
car_speed_x = 0.0 
lane_change_speed = 0.03 


def sprint(x, y, st):
    glColor3f(0.0, 0.0, 0.0)
    glRasterPos2f(x, y)
    for c in st:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

def handleResize(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w) / float(h), 1.0, 200.0)

def keyboardown(key, x, y):
    global xp, carpos, crspeed, carspeed, handbrake_active, handbrake_timer, target_x
    
    if game_paused:
        return
        
    if key == GLUT_KEY_RIGHT:
        target_x = 0.55
        carpos = 1
    elif key == GLUT_KEY_LEFT:
        target_x = -0.55 
        carpos = 0
    elif key == GLUT_KEY_UP:
        if crspeed > 5:
            crspeed -= 5
            carspeed += 5
    elif key == GLUT_KEY_DOWN:
        if crspeed < 60:
            crspeed += 5
            carspeed -= 5
    elif key == GLUT_KEY_PAGE_UP:
        global camera_angle
        camera_angle += 5.0
    elif key == GLUT_KEY_PAGE_DOWN:
        camera_angle -= 5.0

def keyboard(key, x, y):
    global sky_red, sky_green, sky_blue, roadlight, first_person, camera_distance
    global cheat_mode, cheat_vision, debug_info, auto_avoid, score, crspeed, carspeed
    global free_camera_mode, camera_rotation_angle, camera_height
    global rain_mode, game_paused 
            
    try:
        key = key.decode('utf-8').lower()  
    except:
        key = key.lower()  
    if key == '\x1b':  # ESC key
        glutLeaveMainLoop()
        return
    if key == 'n':  # Night mode
        sky_red = 0
        sky_green = 0.2
        sky_blue = 0.25
        roadlight = 255
        
    elif key == 'd':
        sky_red = 0
        sky_green = 0.8
        sky_blue = 1.0
        roadlight = 50
    elif key == 'e':
        sys.exit(1)
    elif key == 't':
        first_person = not first_person
        if first_person:
            free_camera_mode = False  # Disable free camera if switching to FP
    elif key == 'i':
        camera_distance = max(3.0, camera_distance - 0.5)
    elif key == 'o':
        camera_distance = min(15.0, camera_distance + 0.5)
    elif key == 'c':
        cheat_mode = not cheat_mode
        if cheat_mode:
            crspeed = 40
            carspeed = 65
        else:
            crspeed = 60
            carspeed = 45
            cheat_vision = False
    elif key == 'v':
        if cheat_mode:
            cheat_vision = not cheat_vision

    elif key == 'r':
        reset_game()
    elif key == 'p':
        debug_info = not debug_info
    elif key == 'm':
        free_camera_mode = not free_camera_mode
        if free_camera_mode:
            first_person = False 
    elif key == 'a':
        if free_camera_mode:
            camera_rotation_angle += 5.0
    elif key == 's':
        if free_camera_mode:
            camera_rotation_angle -= 5.0
    elif key == 'k':
        if free_camera_mode:
            camera_height = max(1.0, camera_height - 0.5)
    elif key == 'l':
        if free_camera_mode:
            camera_height = min(5.0, camera_height + 0.5)
    elif key == 'w':  # Toggle rain mode
        rain_mode = not rain_mode
        if rain_mode:
            init_rain()
        # Darken the sky for rain effect
            sky_red = 0.2
            sky_green = 0.3
            sky_blue = 0.4
            roadlight = 100  # Reduce road light in rain
        else:
        # Restore original sky colors
         sky_red = 0
         sky_green = 0.8
         sky_blue = 1.0
         roadlight = 50
    elif key == ' ':  # Space to pause/unpause
        game_paused = not game_paused
        if not game_paused:
            glutTimerFunc(25, update, 0)  # Restart the game loop if unpausing

def init_rain():
    global rain_drops
    rain_drops = []
    for _ in range(rain_density):
        rain_drops.append([
            random.uniform(-5, 5),        # x position (across road)
            random.uniform(10, 25),       # y position (height) - increased initial height
            random.uniform(0, 100),       # z position (distance along road)
            random.uniform(1.5, 3.0)      # speed - increased speed range
        ])

def update_rain():
    if not rain_mode or game_paused:  # Don't update rain when paused
        return
        
    for drop in rain_drops:
        # Move raindrop downward with increased speed
        drop[1] -= drop[3] * rain_speed * 0.2  # Increased multiplier for faster fall
        
        # Reset raindrop when it hits the ground (y < 0)
        if drop[1] < 0:
            drop[0] = random.uniform(-5, 5)       # Random x position
            drop[1] = random.uniform(15, 30)      # Increased reset height
            drop[2] = random.uniform(0, 100)      # Random z position
            drop[3] = random.uniform(1.5, 3.0)    # Increased speed range

def draw_rain():
    if not rain_mode:
        return
        
    glPushMatrix()
    glTranslatef(0.0, crmove, 0.0)  # Move with the road
    glRotatef(80, -1.0, 0.0, 0.0)   # Match road perspective
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_LINES)
    glColor4f(0.7, 0.7, 1.0, 0.6)  # Slightly more opaque
    
    for drop in rain_drops:
        # Draw longer raindrops (increased length from 0.3 to 0.6)
        glVertex3f(drop[0], drop[1], drop[2])
        glVertex3f(drop[0], drop[1]-0.6, drop[2]+0.2)  # Longer and more diagonal
        
    glEnd()
    glDisable(GL_BLEND)
    glPopMatrix()

def reset_game():
    global xp, crspeed, crmove, y11, zp, tpx, carpos, view, score, totalMeter
    global carspeed, sky_red, sky_green, sky_blue, roadlight, first_person
    global camera_distance, camera_angle, cheat_mode, cheat_vision, handbrake_active
    global handbrake_timer, debug_info, auto_avoid, avoid_timer, lives, game_paused
    global last_collision_time

    last_collision_time = 0
    game_paused = False  # Ensure game is unpaused when reset
    lives = 3
    xp = -0.55
    crspeed = 60
    crmove = 4
    y11 = -3.3
    zp = 2
    tpx = 0.15
    carpos = 0
    view = 10.0
    score = 0
    totalMeter = 0
    carspeed = 45
    sky_red = 0
    sky_green = 0.8
    sky_blue = 1.0
    roadlight = 50
    first_person = False
    camera_distance = 7.0
    camera_angle = 0.0
    cheat_mode = False
    cheat_vision = False
    handbrake_active = False
    handbrake_timer = 0
    debug_info = False
    auto_avoid = False
    avoid_timer = 0

def enemy_car(x, y, z, color):
    """Draws an enemy car at the specified position with given color"""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Adjust the car to match road perspective (100 degree tilt)
    glRotatef(100, 1.0, 0.0, 0.0)
    
    # Main car body
    glPushMatrix()
    glScalef(0.8, 0.4, 1.6)  # More realistic car proportions
    glColor3fv(color)
    glutSolidCube(0.5)
    glPopMatrix()
    
    # Roof/cabin area
    glPushMatrix()
    glTranslatef(0.0, 0.1, 0.0)
    glScalef(0.7, 0.3, 1.2)
    glColor3fv([c*0.8 for c in color])  # Slightly darker shade for roof
    glutSolidCube(0.5)
    glPopMatrix()
    
    # Wheels - properly positioned at bottom of car
    wheel_positions = [
        (0.25, -0.15, 0.25),   # Front right
        (0.25, -0.15, -0.25),  # Rear right
        (-0.25, -0.15, 0.25),  # Front left
        (-0.25, -0.15, -0.25)  # Rear left
    ]
    
    for pos in wheel_positions:
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        glRotatef(90, 0.0, 1.0, 0.0)  # Rotate wheels to face forward
        glColor3f(0.1, 0.1, 0.1)      # Black tires
        glutSolidTorus(0.05, 0.1, 10, 10)  # More realistic wheel size
        glPopMatrix()
    
    # Front bumper/grill
    glPushMatrix()
    glTranslatef(0.0, -0.05, 0.4)
    glScalef(0.7, 0.2, 0.2)
    glColor3f(0.2, 0.2, 0.2)  # Dark gray
    glutSolidCube(0.5)
    glPopMatrix()
    
    # Headlights
    glPushMatrix()
    glTranslatef(0.2, -0.05, 0.4)
    glColor3f(1.0, 1.0, 0.8)  # Bright yellow-white
    glutSolidSphere(0.04, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-0.2, -0.05, 0.4)
    glColor3f(1.0, 1.0, 0.8)
    glutSolidSphere(0.04, 10, 10)
    glPopMatrix()
    
    glPopMatrix()  # End of car

def collision():
    global y11, score, crspeed, carspeed, lives, last_collision_time

    # Collision cooldown of 1.5 seconds
    current_time = time.time()
    if current_time - last_collision_time < 1.5:
        return False

    # In cheat mode with auto-avoid, prevent collisions
    if cheat_mode and auto_avoid:
        return False

    # Check if a collision happens
    hit = False
    if -0.8 < (crmove - y11) < 0.2 and carpos == 1:
        hit = True
    elif -0.8 < (crmove - (y11 - 10)) < 0.2 and carpos == 0:
        hit = True
    elif -0.8 < (crmove - (y11 - 20)) < 0.2 and carpos == 0:
        hit = True
    elif -0.8 < (crmove - (y11 - 30)) < 0.2 and carpos == 1:
        hit = True

    if hit:
        last_collision_time = current_time  # Start cooldown timer

        if cheat_mode:
            score -= 1
            crspeed += 2
            carspeed -= 2
            return False  # Do not end game in cheat mode
        else:
            lives -= 1
            print("Collision! Lives left:", lives)
            if lives <= 0:
                return True  # Trigger game over
            else:
                return False  # Continue playing

    # Special case that moves the obstacles down
    if -0.8 < (crmove - (y11 - 30)) < 0.2 and carpos == 0:
        y11 -= 40
        return False

    return False

def auto_avoid_obstacles():
    global carpos, xp, auto_avoid, avoid_timer, y11, crmove, target_x
    
    # Only activate auto-avoid if cheat mode is on
    if not cheat_mode:
        auto_avoid = False
        return
        
    current_time = time.time()
    
    # Check if we're approaching an obstacle and need to avoid
    if (-2 < (crmove - y11) < 2 and carpos == 1) or \
       (-2 < (crmove - (y11 - 10)) < 2 and carpos == 0) or \
       (-2 < (crmove - (y11 - 20)) < 2 and carpos == 0) or \
       (-2 < (crmove - (y11 - 30)) < 2 and carpos == 1):
        
        # Only initiate avoidance if not already avoiding
        if not auto_avoid:
            auto_avoid = True
            avoid_timer = current_time
            # Set target position for smooth lane change
            if carpos == 0:
                target_x = 0.55  # Move right
                carpos = 1
            else:
                target_x = -0.55  # Move left
                carpos = 0
    
    # Turn off auto-avoid after 1 second (but keep smooth movement)
    if auto_avoid and current_time - avoid_timer > 1.0:
        auto_avoid = False

def GameScore():
    global score, totalMeter
    
    if game_paused:  
        return False
        
    if (0 > (crmove - y11) and -1 < (crmove - y11) and carpos == 0):
        score += 1
    elif (0 > (crmove - (y11 - 10)) and -1 < (crmove - (y11 - 10)) and carpos == 1):
        score += 1
    elif (0 > (crmove - (y11 - 20)) and -1 < (crmove - (y11 - 20)) and carpos == 1):
        score += 1
    elif (0 > (crmove - (y11 - 30)) and -1 < (crmove - (y11 - 30)) and carpos == 0):
        if cheat_mode:
            score += 20  # Bonus in cheat mode
        else:
            score += 10
    elif (0 > (crmove - (y11 - 35)) and -1 < (crmove - (y11 - 35)) and carpos == 0):
        if cheat_mode:
            score += 20
        else:
            score += 10
        return True
    else:
        totalMeter += 1
        return False

_angle = 0.0
_cameraAngle = 0.0
_ang_tri = 0.0

def gamercar():
    """Draws the player car with same structure as enemy cars but in white color"""
    glPushMatrix()
    glTranslatef(xp, -1.0, 3.5) 
    
    # Adjust the car to match road perspective (10 degree tilt)
    glRotatef(10, 1.0, 0.0, 0.0)
    
    # Main car body - white color
    glPushMatrix()
    glScalef(0.8, 0.4, 1.6)  # Same proportions as enemy cars
    glColor3f(1.0, 1.0, 1.0)  # White color for player car
    glutSolidCube(0.5)
    glPopMatrix()
    
    # Roof/cabin area - slightly off-white
    glPushMatrix()
    glTranslatef(0.0, 0.1, 0.0)
    glScalef(0.7, 0.3, 1.2)
    glColor3f(0.9, 0.9, 0.9)  # Light gray for roof
    glutSolidCube(0.5)
    glPopMatrix()
    
    # Wheels - same as enemy cars
    wheel_positions = [
        (0.25, -0.15, 0.25),   # Front right
        (0.25, -0.15, -0.25),  # Rear right
        (-0.25, -0.15, 0.25),  # Front left
        (-0.25, -0.15, -0.25)  # Rear left
    ]
    
    for pos in wheel_positions:
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        glRotatef(90, 0.0, 1.0, 0.0)  # Rotate wheels to face forward
        glColor3f(0.1, 0.1, 0.1)      # Black tires
        glutSolidTorus(0.05, 0.1, 10, 10)
        glPopMatrix()
    
    # Front bumper/grill - dark gray
    glPushMatrix()
    glTranslatef(0.0, -0.05, 0.4)
    glScalef(0.7, 0.2, 0.2)
    glColor3f(0.2, 0.2, 0.2)  # Dark gray
    glutSolidCube(0.5)
    glPopMatrix()
    
    # Headlights - yellow-white
    glPushMatrix()
    glTranslatef(0.2, -0.05, 0.4)
    glColor3f(1.0, 1.0, 0.8)  # Yellow-white
    glutSolidSphere(0.05, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-0.2, -0.05, 0.4)
    glColor3f(1.0, 1.0, 0.8)
    glutSolidSphere(0.05, 10, 10)
    glPopMatrix()
    
    # Add some chrome details to enhance the white car
    glPushMatrix()
    glTranslatef(0.0, 0.05, 0.3)
    glScalef(0.3, 0.1, 0.1)
    glColor3f(0.8, 0.8, 0.8)  # Chrome/silver stripe
    glutSolidCube(0.5)
    glPopMatrix()
    
    # Chrome side mirrors
    glPushMatrix()
    glTranslatef(0.35, 0.05, 0.2)
    glScalef(0.1, 0.05, 0.1)
    glColor3f(0.7, 0.7, 0.7)
    glutSolidCube(0.5)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-0.35, 0.05, 0.2)
    glScalef(0.1, 0.05, 0.1)
    glColor3f(0.7, 0.7, 0.7)
    glutSolidCube(0.5)
    glPopMatrix()
    
    glPopMatrix()  # End of car

def sky():
    glBegin(GL_QUADS)
    glColor3f(sky_red, 0, sky_blue)
    glVertex3f(-4.0, 1.5, 0)
    glVertex3f(4.0, 1.5, 0)
    glVertex3f(8.0, 3, 0)
    glVertex3f(-8.0, 3, 0)
    glEnd()

def roadside():
    # Trees and poles on the left side
    for z in range(-38, 400, 4):
        # Pole
        glPushMatrix()
        glColor3ub(200, 200, 200)
        glTranslatef(-1.20, z, 0.40)
        glScalef(0.2, 0.2, 3)
        glutSolidCube(0.4)
        glPopMatrix()
        
        # Horizontal bar
        glPushMatrix()
        glColor3ub(200, 200, 200)
        glTranslatef(-0.84, z, 1.0)
        glScalef(2, 0.2, 0.2)
        glutSolidCube(0.4)
        glPopMatrix()
        
        # Light - only show if not in day mode (roadlight > 50)
        if roadlight > 50:
            glPushMatrix()
            glColor4ub(255, 255, 255, roadlight)
            glTranslatef(-0.44, z, 0.70)
            glutSolidCone(0.2, 0.3, 15, 20)
            glPopMatrix()
    
    # Grass areas
    glBegin(GL_QUADS)
    glColor3ub(0, 155, 20)
    glVertex3f(-5.0, -10, 0)
    glVertex3f(-1.0, -10, 0)
    glVertex3f(-1.0, 400, 0)
    glVertex3f(-5.0, 400, 0)
    glEnd()
    
    glBegin(GL_QUADS)
    glColor3ub(0, 155, 20)
    glVertex3f(1.0, -10, 0)
    glVertex3f(5.0, -10, 0)
    glVertex3f(5.0, 400, 0)
    glVertex3f(1.0, 400, 0)
    glEnd()
    
def house():
    for z in range(-40, 400, 5):
        # Left houses
        glPushMatrix()
        glColor3ub(70, 61, 46)  # Dark brown color for the wall
        glTranslatef(-3.0, z, 0.20)  # Position the left wall at X = -3.0, Z = z, and height 0.20
        glScalef(0.90, 1.0, 1.0)  # Narrow the wall along the X-axis (0.90 scale)
        glutSolidCube(1)  # Draw the main house wall
        glPopMatrix()

        glPushMatrix()
        glColor3ub(255, 255, 255)  # White color for window
        glTranslatef(-2.55, z, 0.40)  # Position the left window
        glutSolidCube(0.2)  # Small window
        glPopMatrix()

        glPushMatrix()
        glColor3ub(255, 255, 255)  # White color for door/base
        glTranslatef(-2.9, z-0.5, 0.2)  # Position the left door/base
        glScalef(0.6, 0.2, 1)  # Stretch the door to make it flat
        glutSolidCube(0.5)  # Draw the door
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, 1, 1)  # Cyan color for the roof
        glTranslatef(-3.0, z, 0.70)  # Position the cone roof above the left house
        glutSolidCone(1, 1, 4, 6)  # Draw the cone-shaped roof
        glPopMatrix()

        # Right houses
        glPushMatrix()
        glColor3f(1, 1, 1)  # White color for the wall
        glTranslatef(3.0, z, 0.40)  # Position the right wall at X = 3.0, Z = z, and height 0.40
        glScalef(0.90, 1.0, 1.0)  # Narrow the wall along the X-axis (0.90 scale)
        glutSolidCube(1)  # Draw the right house wall
        glPopMatrix()

        glPushMatrix()
        glColor3ub(0, 0, 0)  # Black color for window
        glTranslatef(2.55, z, 0.50)  # Position the right window
        glutSolidCube(0.2)  # Small window
        glPopMatrix()

        glPushMatrix()
        glColor3ub(0, 0, 0)  # Black color for door/base
        glTranslatef(2.9, z-0.5, 0.2)  # Position the right door/base
        glScalef(0.6, 0.2, 1)  # Stretch the door to make it flat
        glutSolidCube(0.5)  # Draw the door
        glPopMatrix()

        glPushMatrix()
        glColor3ub(70, 61, 46)  # Dark brown color for the roof
        glTranslatef(3.0, z, 0.80)  # Position the cone roof higher (increase Z value to raise roof)
        glutSolidCone(1, 1, 4, 6)  # Draw the cone-shaped roof
        glPopMatrix()

def tree():
    for z in range(-40, 400, 4):
        # Left trees
        glPushMatrix()
        glColor3f(0, 1, 0)
        glTranslatef(-1.20, z, 0.45)
        glutSolidCone(0.2, 0.4, 20, 10)
        glPopMatrix()
        
        glPushMatrix()
        glColor3ub(102, 51, 0)
        glTranslatef(-1.20, z, 0.25)
        glScalef(0.2, 0.2, 1)
        glutSolidCube(0.4)
        glPopMatrix()
        
        # Right trees
        glPushMatrix()
        glColor3f(0, 1, 0)
        glTranslatef(1.20, z, 0.50)
        glutSolidCone(0.2, 0.4, 20, 10)
        glPopMatrix()
        
        glPushMatrix()
        glColor3ub(102, 51, 0)
        glTranslatef(1.20, z, 0.30)
        glScalef(0.2, 0.2, 1)
        glutSolidCube(0.4)
        glPopMatrix()

def road():
    # Road markings
    for z in range(-10, 400, 1):
        glPushMatrix()
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex3f(-0.03, z, 0)
        glVertex3f(0.03, z, 0)
        glVertex3f(0.03, z+0.5, 0)
        glVertex3f(-0.03, z+0.5, 0)
        glEnd()
        glPopMatrix()
    
    # Road surface
    glPushMatrix()
    glColor3ub(0, 0, 0)
    glTranslatef(0.0, 0.0, -0.50)
    glBegin(GL_QUADS)
    glVertex3f(-1.3, -10, 0)
    glVertex3f(1.3, -10, 0)
    glVertex3f(1.3, 400, 0)
    glVertex3f(-1.3, 400, 0)
    glEnd()
    glPopMatrix()

def obstacle_cars():
    """Draws enemy cars as obstacles on the road"""
    car_colors = [
        (1, 0, 0),    # Red
        (0, 0, 1),    # Blue
        (1, 1, 0),    # Yellow
        (1, 0, 1),    # Purple
        (0, 1, 1),    # Cyan
    ]
    
    for zp in range(-20, 400, 40):
        # Left lane cars
        enemy_car(-0.50, zp, -0.1, car_colors[0])
        enemy_car(-0.50, zp+30, -0.1, car_colors[1])
        
        # Right lane cars
        enemy_car(0.50, zp+10, -0.1, car_colors[2])
        enemy_car(0.50, zp+20, -0.1, car_colors[3])

def winner(a):
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 500)
    glutCreateWindow(b"GAME OVER")
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glLineWidth(3)
    glutDisplayFunc(gameOverDisplay)
    glutReshapeFunc(handleResize)
    glutIdleFunc(timeTick)

def gameOverDisplay():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0.0, 30.0, 100.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    RenderToDisplay()
    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.0, 1.0, 3200)
    glMatrixMode(GL_MODELVIEW)

UpwardsScrollVelocity = -1.0
view = 10.0

def timeTick():
    global UpwardsScrollVelocity, view
    
    if UpwardsScrollVelocity < -1:
        view -= 0.0011
    if view < 0:
        view = 2
        UpwardsScrollVelocity = -1.0
    UpwardsScrollVelocity -= 0.2
    glutPostRedisplay()

numberOfQuotes = 5
quotes = [b"Nirapod Sorok Chai", b"Game Over", b"", b"", b""]

def RenderToDisplay():
    # Setup orthogonal projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)  # Match your window size
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Disable depth test for 2D rendering
    glDisable(GL_DEPTH_TEST)
    
    # Set large yellow text color
    glColor3f(1.0, 1.0, 0.0)  # Bright yellow
    
    # Render each quote with different sizes
    for i, text in enumerate(quotes):
        if not text:
            continue
            
        # Calculate centered position
        x_pos = 400 - (len(text) * 15)  # Approximate centering
        y_pos = 400 - (i * 150)         # Vertical spacing
        
        # First line (Bengali) - Extra large
        if i == 0:
            glPushMatrix()
            glTranslatef(x_pos, y_pos, 0)
            glScalef(0.2, 0.2, 0.2)  # Large scale
            for char in text:
                glutStrokeCharacter(GLUT_STROKE_ROMAN, char)
            glPopMatrix()
        
        # Second line (English) - Large
        else:
            glPushMatrix()
            glTranslatef(x_pos, y_pos, 0)
            glScalef(0.15, 0.15, 0.15)  # Slightly smaller
            for char in text:
                glutStrokeCharacter(GLUT_STROKE_ROMAN, char)
            glPopMatrix()
    
    # Restore GL state
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def drawScene():
    global crmove, _angle, _ang_tri, handbrake_active, handbrake_timer, carspeed
    global camera_rotation_angle

    if game_paused:  # Skip game logic when paused
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Draw paused screen overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 800, 0, 500)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Semi-transparent overlay
        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(800, 0)
        glVertex2f(800, 500)
        glVertex2f(0, 500)
        glEnd()
        
        # Paused text
        glColor3f(1, 1, 1)
        sprint(350, 250, "GAME PAUSED")
        sprint(300, 220, "Press SPACE to continue")
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glutSwapBuffers()
        return

    # Normal game logic when not paused
    if handbrake_active and time.time() - handbrake_timer > 1.0:
        handbrake_active = False
        crspeed += 15
        carspeed -= 15

    if cheat_mode:
        auto_avoid_obstacles()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # ==================== CAMERA SETUP =====================
    if first_person:
        # First-person camera positioned inside the car
        eye_x = xp  # Same X position as car
        eye_y = -1.0  # Slightly above road level
        eye_z = 3.5  # Positioned at car's front
        
        # Looking slightly downward and forward
        center_x = -xp
        center_y = 1.5  # Look slightly downward
        center_z = -10.0  # Look far ahead
        
        gluLookAt(eye_x, eye_y, eye_z, 
                 center_x, center_y, center_z, 
                 0.0, 0.0, 1.0)  # Up vector
        
        # Draw car interior/windshield frame
        glPushMatrix()
        glTranslatef(xp, -1.0, 3.5)
        glColor3f(0.1, 0.1, 0.1)
        
        # Windshield frame
        glPushMatrix()
        glTranslatef(0.0, 0.1, 0.0)
        glScalef(1.2, 0.05, 0.05)
        glutSolidCube(0.5)
        glPopMatrix()
        
        # Dashboard
        glPushMatrix()
        glTranslatef(0.0, -0.05, -0.2)
        glScalef(1.0, 0.1, 0.5)
        glutSolidCube(0.5)
        glPopMatrix()
        
        glPopMatrix()

    elif free_camera_mode:
        camera_x = xp + camera_distance * math.sin(math.radians(camera_rotation_angle))
        camera_z = 3.5 + camera_distance * math.cos(math.radians(camera_rotation_angle))
        gluLookAt(
            camera_x, camera_height, camera_z,
            xp, -1.0, 3.5,
            0.0, 1.0, 0.0
        )
    else:
        # Default third-person view
        glRotatef(-camera_angle, 0.0, 1.0, 0.0)
        glTranslatef(0.0, 0.0, -camera_distance)
        gamercar()  # Draw player car in third-person view

    # =================== GAME WORLD ========================
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    glRotatef(80, -1.0, 0.0, 0.0)

    glPushMatrix()
    glTranslatef(0.0, crmove, 0.0)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    road()
    obstacle_cars()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, crmove, 0.0)
    tree()
    house()
    roadside()
    obstacle_cars()
    GameScore()
    if debug_info:
        print(f"Score: {score}, Distance: {totalMeter}, Speed: {carspeed}, Lives: {lives}")
    glPopMatrix()
    glPopMatrix()
        
    update_rain()
    draw_rain()

    # =================== UI OVERLAY ========================
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 500)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)  # White text for better visibility
    sprint(20, 460, f"Score: {score}")
    sprint(20, 435, f"Distance: {totalMeter}")
    sprint(20, 410, f"Speed: {carspeed}")
    sprint(20, 385, f"Lives: {lives}")

    if cheat_mode:
        glColor3f(1, 0, 0)  # Red
        sprint(20, 360, "CHEAT MODE: ON")
        if cheat_vision:
            sprint(20, 340, "CHEAT VISION: ON")

    if first_person:
        glColor3f(0, 0.5, 1)  # Blue
        sprint(20, 315, "FIRST-PERSON VIEW")

    if handbrake_active:
        glColor3f(1, 0.5, 0)  # Orange
        sprint(20, 290, "HANDBRAKE: ACTIVE")

    # Add crosshair in first-person mode
    if first_person:
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        glVertex2f(400 - 10, 250)
        glVertex2f(400 + 10, 250)
        glVertex2f(400, 250 - 10)
        glVertex2f(400, 250 + 10)
        glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glClearColor(sky_red, sky_green, sky_blue, 1.0)

    if collision():
        winner('a')

    glutSwapBuffers()

def update(value):
    global crmove, _angle, _ang_tri, xp, car_speed_x
    
    if not game_paused:
        # Smooth lane changing
        if abs(xp - target_x) > 0.01:  # If not close enough to target
            car_speed_x = (target_x - xp) * lane_change_speed
            xp += car_speed_x
        else:
            xp = target_x  # Snap to final position when close
            car_speed_x = 0.0
            
        crmove -= 0.1
        _angle += 2.0
        if _angle > 360:
            _angle -= 360
        
        _ang_tri += 0.7
        if _ang_tri > 80:
            _ang_tri = 0
    
    glutPostRedisplay()
    if not game_paused:
        glutTimerFunc(crspeed, update, 0)
def initRendering():
    glEnable(GL_DEPTH_TEST)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 500)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Enhanced Racing Game")
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    initRendering()
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glutDisplayFunc(drawScene)
    glutReshapeFunc(handleResize)
    glutTimerFunc(25, update, 0)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(keyboardown)

    print("\n=== CONTROLS ===")
    print("General Controls:")
    print("  ESC: Exit game immediately")
    print("  SPACE: Pause/Unpause")
    print("Movement:")
    print("  LEFT/RIGHT Arrow: Change lanes")
    print("  UP/DOWN Arrow: Adjust speed")
    print("\nCamera Controls (Press M first):")
    print("  A: Rotate left | D: Rotate right")
    print("  K: Lower camera | L: Raise camera")
    print("  I/O: Zoom in/out")
    print("\nGame Features:")
    print("  SPACE: Handbrake boost | T: Toggle views")
    print("  C: Cheat mode ")
    print("  N: Night mode | D: Day mode")
    print("  R: Reset game ")
    print("\nWeather Effects:")
    print("  W: Toggle rain mode")
    print("=============================")

    glutMainLoop()

if __name__ == "__main__":
    main()