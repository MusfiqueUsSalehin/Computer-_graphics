from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
animation_time=1
#Cam stuff
camera_pos = (0,500,500)
fovY = 120

#PLATFORM
chunk_size = 2500
platform_width=500
visible_chunks = 7  #Platforms visible at a time
chunks = []  #Stores platform chunks

#PLAYER POS and movement
player_x_position = 0  # Player's pos along the X #changes in keyboard
x_movement_speed = 14  
player_y_position = 0  #Player's pos along the Y #updated in idle func
min_speed = 0.5  
max_speed = 1.8 
player_speed = min_speed

# Jump
is_jumping = False
jump_height = 300
jump_speed = 0.8
current_jump_height = 0
gravity = 0.9
player_z_position = 0


# OBSTACLES
obstacles = []  # List to store obstacle information
obstacles_per_chunk = 4  # Number of obstacles to spawn in each chunk
# ENEMIES
enemy_speed_hor = 1

# ATTACK SYSTEM
is_attacking = False
attack_animation_time = 0 #will increase this until it reaches atk duration
attack_range = 200
attack_duration = 20  

score = 0

scored_chunks = set()  # To track which chunks have been scored 

coin = 0


health = 100

scored_enemies = set()  # To track which enemies have been scored

def initialize_chunks():  #This func is called at the very begining in the main loop
    global chunks
    chunks.clear() # clearing the list first. Altho it's already cleared
    obstacles.clear()
    for i in range(visible_chunks):
        chunk_y = player_y_position + i * chunk_size #staring y of chunks
        chunks.append(chunk_y) #list now has 5 platform's starting y pos. We will draw plats using this coord in draw_platform func

        # Create obstacles for each initial chunk
        create_obstacles_for_chunk(chunk_y)


def update_chunks():  #This func is being run inside idle func
    global chunks
    # Remove chunks that are far behind and add new ones ahead
    offset=chunk_size*.5
    if player_y_position > chunks[0] + chunk_size + offset: #offset na dile vanishing dekha jai
        chunks.pop(0) #deleting the 1st platform start coord because it will vanish first
        new_chunk_y = chunks[-1] + chunk_size #appending a new start cord. This cord= last chunk jeikhane shuru hoise + chunk_size{So we getting the cord where the last chunk ends }
        chunks.append(new_chunk_y)

        # when chunk is updated, obstacles for that chunk is also created
        create_obstacles_for_chunk(new_chunk_y)
       
#============================================================
def create_obstacles_for_chunk(chunk_y): # chunk_y=start y coord of chunk .Creating obstacles for every chunk #called inside update_chunks and initialize chunks
    for i in range(obstacles_per_chunk):

        obstacle_type_rand = random.choice(["wall", "enemy", "coin"])

        if obstacle_type_rand == "wall":  # 50% chance for wall
            obstacle_type = "wall"
            obstacle_y = chunk_y + random.randint(100, chunk_size - 100)# Placing within chunk length
            obstacle_x = random.randint(-400, 400)#spawn point
            obstacle_height = random.randint(jump_height-200, jump_height-100)
            obstacle_width = random.randint(200, 800)#Horizontal length

        elif obstacle_type_rand == "enemy":  # 50% chance for enemy
            obstacle_type = "enemy"
            obstacle_y = chunk_y + random.randint(100, chunk_size - 100)
            obstacle_x = random.randint(-400, 400)
            obstacle_height = 50 
            obstacle_width = 50  

        elif obstacle_type_rand== "coin":
            # Coins are smaller, floating above ground
            obstacle_type = "coin"
            obstacle_y = chunk_y + random.randint(100, chunk_size - 100)
            obstacle_x = random.randint(-400, 400)
            obstacle_height = 30
            obstacle_width = 30 
        
        obstacles.append({  #Storing the infos in a ditionary
            "type": obstacle_type,
            "x": obstacle_x,
            "y": obstacle_y,
            "width": obstacle_width,
            "height": obstacle_height,
            "collected": False  })

def update_obstacles(): #run inside idle
    global obstacles
    
    # Move obstacles towards the player and then more for specific obstacles
    for i in obstacles: #i is a dictionary, obstacles is a list of these dictionaries
        i["y"] -= player_speed #(y) key of the dictionary

        # Enemies be left-right left-right
        if i["type"] == "enemy":
            if "move_right" not in i: #making this key if it's not already made
                i["move_right"] = random.choice([True, False])  # rand ini. direc.
            
            # Move enemy horizontally
            if i["move_right"]: #if move_right's val is true then go right
                i["x"] += enemy_speed_hor
                # go left after hitting border {toggle bool}
                if i["x"] > platform_width-50:
                    i["move_right"] = False
            else:
                i["x"] -= enemy_speed_hor #if move_right's val is false then go left
                if i["x"] < -(platform_width-50):
                    i["move_right"] = True
    
    # Remove obstacles that are far behind the player
    new_obstacles = []
    for obs in obstacles:
        if obs["y"] > player_y_position - chunk_size: #if obobstacles gula isn't 1 chunk behind player==>keep it
            new_obstacles.append(obs) #keeping the in range obstacles gula
    obstacles = new_obstacles

def draw_obstacles():  # Runs inside showscreen
    # Sort based on obstacle's y, draw closer obstacles 1st
    sorted_obstacles = sorted(obstacles, key=lambda obs: obs["y"], reverse=True) #lambda arguments: expression
    
    for obstacle in sorted_obstacles:
        if obstacle["type"] == "wall":
            glPushMatrix()
            glTranslatef(obstacle["x"], obstacle["y"], 0)
            
            # Draw solid wall first (no transparency)
            glColor3f(0.8, 0.2, 0.2)  # Solid red color for main wall
            
            glBegin(GL_QUADS)
            # Front face
            glVertex3f(-obstacle["width"]/2, 0, 0)
            glVertex3f(obstacle["width"]/2, 0, 0)
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            
            # Back face
            glVertex3f(-obstacle["width"]/2, -10, 0)
            glVertex3f(obstacle["width"]/2, -10, 0)
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            
            # Top face
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            
            # Right face
            glVertex3f(obstacle["width"]/2, 0, 0)
            glVertex3f(obstacle["width"]/2, -10, 0)
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            
            # Left face
            glVertex3f(-obstacle["width"]/2, 0, 0)
            glVertex3f(-obstacle["width"]/2, -10, 0)
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            glEnd()
            
            # Draw border around the wall
            glColor3f(0.0, 0.0, 0.0)  # Black color for border
            glLineWidth(3.0)  # Thicker lines for border
            
            # Front border - using individual line segments
            glBegin(GL_LINES)
            glVertex3f(-obstacle["width"]/2, 0, 0)
            glVertex3f(obstacle["width"]/2, 0, 0)
            
            glVertex3f(obstacle["width"]/2, 0, 0)
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, 0, 0)
            glEnd()
            
            # Back border - using individual line segments
            glBegin(GL_LINES)
            glVertex3f(-obstacle["width"]/2, -10, 0)
            glVertex3f(obstacle["width"]/2, -10, 0)
            
            glVertex3f(obstacle["width"]/2, -10, 0)
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, -10, 0)
            glEnd()
            
            # Top border - using individual line segments
            glBegin(GL_LINES)
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            glEnd()
            
            # Right border - using individual line segments
            glBegin(GL_LINES)
            glVertex3f(obstacle["width"]/2, 0, 0)
            glVertex3f(obstacle["width"]/2, -10, 0)
            
            glVertex3f(obstacle["width"]/2, -10, 0)
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            
            glVertex3f(obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            
            glVertex3f(obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(obstacle["width"]/2, 0, 0)
            glEnd()
            
            # Left border - using individual line segments
            glBegin(GL_LINES)
            glVertex3f(-obstacle["width"]/2, 0, 0)
            glVertex3f(-obstacle["width"]/2, -10, 0)
            
            glVertex3f(-obstacle["width"]/2, -10, 0)
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            
            glVertex3f(-obstacle["width"]/2, -10, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            
            glVertex3f(-obstacle["width"]/2, 0, obstacle["height"])
            glVertex3f(-obstacle["width"]/2, 0, 0)
            glEnd()
            
            glLineWidth(1.0)  # Reset line width to default
            glPopMatrix()
#***************************************************************************************************
        elif obstacle["type"] == "enemy":
            glPushMatrix()
            glTranslatef(obstacle["x"], obstacle["y"], 0)
            
            # Draw black border first (slightly larger than main body)
            glColor3f(0.0, 0.0, 0.0)  # Black border
            glLineWidth(2.0)
            
            # Border for head
            glPushMatrix()
            glTranslatef(0, 0, obstacle["height"] * 0.8)
            glutSolidSphere(obstacle["width"]/2 + 1, 20, 20)
            glPopMatrix()
            
            # Border for torso
            glPushMatrix()
            glTranslatef(0, 0, obstacle["height"] * 0.4)
            glScalef(1.0, 1.0, 1.2)
            glutSolidSphere(obstacle["width"]/2 * 0.8 + 1, 20, 20)
            glPopMatrix()
            
            # Border for left foot
            glPushMatrix()
            glTranslatef(-obstacle["width"]/4, 0, obstacle["height"] * 0.1)
            glutSolidSphere(obstacle["width"]/4 + 1, 15, 15)
            glPopMatrix()
            
            # Border for right foot
            glPushMatrix()
            glTranslatef(obstacle["width"]/4, 0, obstacle["height"] * 0.1)
            glutSolidSphere(obstacle["width"]/4 + 1, 15, 15)
            glPopMatrix()
            
            # Main ghost body
            glColor3f(0.6, 0.2, 0.8)  # Purple color
            
            # Head (sphere)
            glPushMatrix()
            glTranslatef(0, 0, obstacle["height"] * 0.8)
            glutSolidSphere(obstacle["width"]/2, 20, 20)
            glPopMatrix()
            
            # Torso
            glPushMatrix()
            glTranslatef(0, 0, obstacle["height"] * 0.4)
            glScalef(1.0, 1.0, 1.2)
            glutSolidSphere(obstacle["width"]/2 * 0.8, 20, 20)
            glPopMatrix()
            
            # Left foot
            glPushMatrix()
            glTranslatef(-obstacle["width"]/4, 0, obstacle["height"] * 0.1)
            glutSolidSphere(obstacle["width"]/4, 15, 15)
            glPopMatrix()
            
            # Right foot
            glPushMatrix()
            glTranslatef(obstacle["width"]/4, 0, obstacle["height"] * 0.1)
            glutSolidSphere(obstacle["width"]/4, 15, 15)
            glPopMatrix()
            
            # Ghost eyes (white with black pupils)
            glColor3f(1.0, 1.0, 1.0)  # White eyes
            
            # Left eye
            glPushMatrix()
            glTranslatef(-obstacle["width"]/4, obstacle["width"]/3, obstacle["height"] * 0.8)
            glutSolidSphere(obstacle["width"]/6, 10, 10)
            
            # Pupil
            glColor3f(0.0, 0.0, 0.0)
            glTranslatef(0, 0.5, obstacle["width"]/12)
            glutSolidSphere(obstacle["width"]/12, 8, 8)
            glPopMatrix()
            
            # Right eye
            glColor3f(1.0, 1.0, 1.0)
            glPushMatrix()
            glTranslatef(obstacle["width"]/4, obstacle["width"]/3, obstacle["height"] * 0.8)
            glutSolidSphere(obstacle["width"]/6, 10, 10)
            
            # Pupil
            glColor3f(0.0, 0.0, 0.0)
            glTranslatef(0, 0.5, obstacle["width"]/12)
            glutSolidSphere(obstacle["width"]/12, 8, 8)
            glPopMatrix()
            
            glLineWidth(1.0)
            glPopMatrix()

#***************************************************************************************************
        elif obstacle["type"] == "coin" and not obstacle.get("collected", False): # Only draw if not collected
            glPushMatrix()
            glTranslatef(obstacle["x"], obstacle["y"], obstacle["height"])
            glColor3f(1.0, 0.84, 0.0)  # shiny gold

            # Make the coin flatter (like a disc) instead of a ball
            glPushMatrix()
            glScalef(1.0, 0.2, 1.0)  # squash sphere into a flat coin
            glutSolidSphere(obstacle["width"], 30, 30)
            glPopMatrix()

            glPopMatrix()

def draw_attack(): # ran in showscreen
    global is_attacking, attack_animation_time, attack_range
    
    if is_attacking == False: #false hole nicher code hobe na
        return
        
    # attack_progress determines size based on attack er kotodur holo
    attack_progress = attack_animation_time / attack_duration
    attack_size = attack_range * (1 - attack_progress)  # attack shrink kortese
    
    glPushMatrix()
    glTranslatef(player_x_position, player_y_position, player_z_position + 30)
    
    # Draw a circular attack effect using quads
    glColor3f(1.0, 1.0, 0.0)  # Solid yellow color
    
    # Draw the attack as a series of quads forming a circle
    num_segments = 36
    for i in range(num_segments):
        angle1 = i * 10 * math.pi / 180
        angle2 = (i + 1) * 10 * math.pi / 180
        
        x1 = math.cos(angle1) * attack_size
        y1 = math.sin(angle1) * attack_size
        x2 = math.cos(angle2) * attack_size
        y2 = math.sin(angle2) * attack_size
        
        # Draw a quad segment (triangle would work too)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)  # Center point
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(0, 0, 0)  # Back to center to complete the quad
        glEnd()
    
    # Draw border using individual line segments instead of LINE_LOOP
    glColor3f(1.0, 0.5, 0.0)  # Orange border
    glLineWidth(2.0)
    
    # Draw the border as individual line segments
    for i in range(num_segments):
        angle1 = i * 10 * math.pi / 180
        angle2 = (i + 1) * 10 * math.pi / 180
        
        x1 = math.cos(angle1) * attack_size
        y1 = math.sin(angle1) * attack_size
        x2 = math.cos(angle2) * attack_size
        y2 = math.sin(angle2) * attack_size
        
        glBegin(GL_LINES)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        glEnd()
    
    glLineWidth(1.0)
    
    glPopMatrix()     



def check_collisions(): #Runs in idle 
    global player_y_position, player_x_position, player_z_position, is_jumping, current_jump_height, coin , health
    player_size = 10  # Approximate player size
    
    for obstacle in obstacles:
        if (obstacle["type"] == "wall" and 
            abs(player_x_position - obstacle["x"]) < (player_size + obstacle["width"]/2) and  #player center---wall center < p.size+half of wall
            abs(player_y_position - obstacle["y"]) < (player_size + 10) and #distance < player size + 10(wall depth)
            player_z_position < obstacle["height"]):
            
            # Wall Collision detected
            reset_game()
            break

        elif (obstacle["type"] == "enemy" and 
            abs(player_x_position - obstacle["x"]) < (player_size + obstacle["width"]/2) and
            abs(player_y_position - obstacle["y"]) < (player_size + 10) and
            abs(player_z_position - obstacle["height"]/2) < (player_size + obstacle["height"]/2)):

            health -= 10

            print(f"Health: {health}")
            obstacles.remove(obstacle)

            
            # Enemy collision detected
            #make a global health variable. oita theke minus korba and print that on screen
            if health <= 0:
                print("Game Over!")
                reset_game()
            break

        elif obstacle["type"] == "coin" and not obstacle.get("collected", False) and \
            abs(player_x_position - obstacle["x"]) < (player_size + obstacle["width"]/2) and \
            abs(player_y_position - obstacle["y"]) < (player_size + 10) and \
            abs(player_z_position - obstacle["height"]) < (player_size + obstacle["height"]):
            
            # Coin collection detected
            obstacle["collected"] = True
            coin += 10  # Add points for collecting a coin
            print(f"Coin collected!: {coin}")



def update_score():
    global score, chunks, player_y_position, scored_chunks, scored_ememies,  obstacles
    
    # Check if player has crossed a chunk boundary (wall position)
    for chunk_y in chunks:
        # If player has just passed a chunk boundary and it hasn't been scored yet
        if (player_y_position > chunk_y + chunk_size/2 and 
            chunk_y not in scored_chunks and 
            chunk_y > 0):  # Don't score the initial chunk
            
            scored_chunks.add(chunk_y)
            score += 20
            print(f"Wall crossed! Score: {score}")
    
    # Check if player has passed any enemies
    for obstacle in obstacles:
        if (obstacle["type"] == "enemy" and 
            player_y_position > obstacle["y"] and  # Player has passed the enemy
            id(obstacle) not in scored_enemies):  # This enemy hasn't been scored yet
            
            scored_enemies.add(id(obstacle))
            score += 50
            print(f"Enemy avoided! +50 points! Score: {score}")

#============================================================

def keyboardListener(key, x, y):
    global player_speed, player_x_position, is_jumping, current_jump_height

    if key == b'w':
        player_speed = min(max_speed, player_speed + 0.05)

    if key == b's':
        player_speed = max(min_speed, player_speed - 0.05)

    if key == b'a':
        player_x_position -= x_movement_speed


    if key == b'd':
        player_x_position += x_movement_speed


    if key == b' ' and not is_jumping:
        is_jumping = True
        current_jump_height = 0

    # Reset the game if R key is pressed
    if key == b'r':
        reset_game()


def specialKeyListener(key, x, y):
    pass


    # Move camera up (UP arrow key)
    # if key == GLUT_KEY_UP:

    # # Move camera down (DOWN arrow key)
    # if key == GLUT_KEY_DOWN:

    # moving camera left (LEFT arrow key)
    #if key == GLUT_KEY_LEFT:
       # x -= 1  # Small angle decrement for smooth movement

    # moving camera right (RIGHT arrow key)
    #if key == GLUT_KEY_RIGHT:
       # x += 1  # Small angle increment for smooth movement

def reset_game():
    global player_y_position, player_x_position, player_z_position, is_jumping, current_jump_height, player_speed,chunks, obstacles, score , coin , scored_chunks, health , scored_ememies
    
    # Resetting variables
    player_y_position = 0
    player_x_position = 0
    player_z_position = 0
    is_jumping = False
    current_jump_height = 0
    player_speed = min_speed
    score = 0

    coin = 0

    health = 100

    scored_chunks = set()  #reseting scored chunks

    scored_ememies = set()  #reseting scored enemies    
    
    # Clearing chunks and obstacles
    chunks.clear()
    obstacles.clear()
    #Reinitializing chunk and obs generation
    for i in range(visible_chunks):
        chunk_y = player_y_position + i * chunk_size
        chunks.append(chunk_y)
        create_obstacles_for_chunk(chunk_y)

def check_attack_hit():
    global obstacles
    
    new_obstacles = [] # For obstacles that aren't hit, includes walls by default
    
    for i in obstacles: #i is a dictionary
        if i["type"] == "enemy":
            # player---enemy
            dist_x = abs(player_x_position - i["x"])
            dist_y = abs(player_y_position - i["y"])
            
            # attack range check
            if dist_x < attack_range and dist_y < attack_range:
                # enemy hit hole restart loo[. This Enemy hit hole append kortesina
                continue
                
        # Unhit obsticles append kore dichi
        new_obstacles.append(i)
    
    obstacles = new_obstacles # making it the main obstacle to be drawn list

def mouseListener(button, state, x, y):
    global is_attacking, attack_animation_time
    
    # Left mouse button fires an attack
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not is_attacking:
        is_attacking = True
        attack_animation_time = 0
        check_attack_hit()


def setupCamera(): #This func is ran inside showScreen

    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix

    gluPerspective(fovY, 1600/900, 0.1, 10000)  # (field of view, aspect ratio, near clip, far clip)
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Camera position and look at coord moves as the player moves
    camera_distance = 200  #cam dist behind player
    camera_height = 200 #  camera jumps too==> + player_z_position   #cam height above player
    gluLookAt(player_x_position, player_y_position - camera_distance, camera_height,  #camera pos
              player_x_position, player_y_position + 500, 0,  #camera will look at this cord (it will look 500 pixels in front of the player)
              0, 0, 1)        # Up vector (z-axis)


def idle(): #This func is being called as idle func from the main loop
    global  player_speed,is_jumping, jump_height, current_jump_height,player_x_position, player_y_position, player_z_position, is_attacking, attack_animation_time

    player_y_position += player_speed  #Player pos is updating constantly
    update_chunks() #chunks er position has to be updated constantly. Therefore it is called in idle func
    update_obstacles()  # Update obstacle positions
    check_collisions()  # Check for collisions
    update_score()  # Update score based on chunks crossed

    #Attack animation
    if is_attacking:
        attack_animation_time += 1 # will increase this until it reaches atk duration
        if attack_animation_time >= attack_duration: 
            is_attacking = False #duration porjonto gele off kore dibo animation

    #Border collision
    border_width = platform_width  # Same as platform width
    if abs(player_x_position) > border_width:
        reset_game()

    # Jumping Physics
    if is_jumping: #Will only happen if is_jumping==True
        if current_jump_height < jump_height:#rising until reaching jump_height
            player_z_position += jump_speed #rising
            current_jump_height += jump_speed #storing the rise
        else: #Fall when jump_height reached
            player_z_position -= gravity #falling
           
            # Check landing
            if player_z_position <= 0: #enter when player reaches z=0
                player_z_position = 0 #beshi niche jodi chole jai
                is_jumping = False #off kore dilam naile uporer boro loop cholte thakbe
                current_jump_height = 0 #reseting

    glutPostRedisplay()

def draw_player():
    global animation_time
    
    animation_time += 0.005  # will give circling sine values
    
    glTranslatef(player_x_position, 0, 0)
    glTranslatef(0, player_y_position, 0)
    glTranslatef(0, 0, player_z_position)

    leg_swing = math.sin(animation_time) * 15  # Front-back leg movement
    arm_swing = math.sin(animation_time + math.pi) * 20  # Opposite of legs
    
    # Additional subtle movements for more realism
    body_bob = math.sin(animation_time * 2) * 3  
    leg_lift = abs(math.sin(animation_time)) * 5 
    
    # Apply body bobbing
    glTranslatef(0, 0, body_bob)

    # Minecraft Steve body parts (cube-based)
    glColor3f(0.0, 0.0, 1.0)  # Blue shirt
   
    # Body (main cube) - slightly bobs up and down
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glScalef(20, 10, 30)
    glutSolidCube(1)
    glPopMatrix()
   
    # Head (cube) - moves with body bob
    glColor3f(0.8, 0.6, 0.4)  # Skin tone for head
    glPushMatrix()
    glTranslatef(0, 0, 45 + body_bob/2)
    glScalef(20, 20, 20)
    glutSolidCube(1)
    glPopMatrix()

    # Hair (brown quad on top of head)
    glColor3f(0.2, 0.2, 0.2)  # Dark brown color
    glPushMatrix()
    glTranslatef(0, 0, 55 + body_bob/2)  # Position on top of head
    glScalef(22, 22, 5)  # Slightly larger than head but flat
    glutSolidCube(1)
    glPopMatrix()
   
    # Arms - more dynamic movement with rotation
    glColor3f(0.6, 0.4, 0.2)  # Brown arms
    
    # Right arm - swings forward and back with rotation
    glPushMatrix()
    glTranslatef(15, 0, 15)
    glRotatef(arm_swing, 1, 0, 0)  # Rotate arm forward/back
    glTranslatef(0, 0, arm_swing/3)  # Additional forward/back movement
    glScalef(8, 8, 30)
    glutSolidCube(1)
    glPopMatrix()
   
    # Left arm - opposite movement from right arm
    glPushMatrix()
    glTranslatef(-15, 0, 15)
    glRotatef(-arm_swing, 1, 0, 0)  # Opposite rotation
    glTranslatef(0, 0, -arm_swing/3)  # Opposite movement
    glScalef(8, 8, 30)
    glutSolidCube(1)
    glPopMatrix()
   
    # Legs - more dynamic movement with lifting effect
    glColor3f(0.3, 0.2, 0.1)  # Dark brown pants
    
    # Right leg - swings with lifting effect
    glPushMatrix()
    glTranslatef(7, 0, -15)
    if leg_swing > 0:  # Only lift when swinging forward
        glTranslatef(0, 0, leg_lift)
    glRotatef(leg_swing, 1, 0, 0)  # Rotate leg forward/back
    glScalef(8, 8, 30)
    glutSolidCube(1)
    glPopMatrix()
   
    # Left leg - opposite movement from right leg
    glPushMatrix()
    glTranslatef(-7, 0, -15)
    if leg_swing < 0:  # Only lift when swinging forward
        glTranslatef(0, 0, leg_lift)
    glRotatef(-leg_swing, 1, 0, 0)  # Opposite rotation
    glScalef(8, 8, 30)
    glutSolidCube(1)
    glPopMatrix()


# def draw_platform_pattern(chunk_start, chunk_end):
#     pattern_spacing = 50  # Space between pattern lines
#     pattern_width = 10    # Width of each pattern line
   
#     glColor3f(0.7, 0.7, 0.7)  # Light gray pattern
   
#     for y in range(chunk_start, chunk_end, pattern_spacing): #y is the starting coord of pattern quad at every iteration
#         glBegin(GL_QUADS)
#         glVertex3f(-500, y, 0.1)
#         glVertex3f(-500, y + pattern_width, 0.1)
#         glVertex3f(500, y + pattern_width, 0.1)
#         glVertex3f(500, y, 0.1)
#         glEnd()


def draw_platform(): #This func is being ran inside showScreen
    global platform_width
    plat_width = platform_width
    glColor3f(0.5, 0.5, 0.5)

    for chunk_start in chunks:
        glBegin(GL_QUADS)
       
        #Platform er shudhu y constantly update hoche. y er value chunks list theke pabo, whih is chunk_start. 5 ta chunk draw hobe.
        #chunks list e shudhu 5 ta platform er starting y coord dewa.These coords will update in update_chunks() func
        glVertex3f(-plat_width, chunk_start, 0) # start-left
        glVertex3f(plat_width, chunk_start, 0)  # start-right
        glVertex3f(plat_width, chunk_start + chunk_size, 0)  # end-right
        glVertex3f(-plat_width, chunk_start + chunk_size, 0) # end-left  
        glEnd()


        #draw_platform_pattern(chunk_start, chunk_start + chunk_size)



def render_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1.0, 1.0, 1.0)):
    # Save current matrices
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1600, 0, 900)  # Match your window size
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(*color)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(font, ord(character))
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_coin_icon(x, y, size=15):
    # Save current matrices
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1600, 0, 900)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1.0, 0.84, 0.0)  # Gold color
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + size, y)
    glVertex2f(x + size, y + size)
    glVertex2f(x, y + size)
    glEnd()
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)




def showScreen():
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1600, 900)  # Set viewport size #Drawing area inside window

    setupCamera()  # Cam config

    draw_platform()
    draw_obstacles()
    draw_attack()

    # Origin line (Z-axis)
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)  # Red color
    glVertex3f(0, player_y_position, 100)  #new: Position relative to player
    glVertex3f(0, player_y_position, -100)  #new: Position relative to player
    glEnd()

    glPushMatrix()  # Save current transformation matrix    
    draw_player()
    glPopMatrix()   # Restore transformation matrix

    # Display coin count in top LEFT corner (simpler version without background)
    draw_coin_icon(20, 850)
    render_text(50, 850, f"Coins: {coin}")

    glutSwapBuffers()

    
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1600, 900)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"JumpQuest")  # Create the window

    initialize_chunks()  #Initialized first because the lvl needs to generate

    glutDisplayFunc(showScreen)  
    glutKeyboardFunc(keyboardListener)  
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # This func is being called repeatedly

    glutMainLoop()

if __name__ == "__main__":
    main()  