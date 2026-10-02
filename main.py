import math
import random
import pygame

# REVERTED TO ORIGINAL RESOLUTION
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500

PLAYER_START_X = 37
PLAYER_START_Y = 38

# Balance Configurations for 800x500
BULLET_SPEED = 99
FIRE_COOLDOWN = 8       
COLLISION_DISTANCE = 27 
PLAYER_HIT_DISTANCE = 35 

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

background = pygame.image.load('istockphoto.jpg')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("The Last Eclipse")
icon = pygame.image.load('max-removebg-preview.png')
pygame.display.set_icon(icon)

# Player Base Image & Settings
playerImg_original = pygame.image.load('max-removebg-preview.png')
playerImg_original = pygame.transform.scale(playerImg_original, (64, 64)) 
playerImg_original = pygame.transform.rotate(playerImg_original, 180) 

playerX = PLAYER_START_X
playerY = PLAYER_START_Y
player_angle = 0  
PLAYER_SPEED = 5       
ROTATION_SPEED = 4

# Enemy Config
enemyImg = []
enemyX = []
enemyY = []
enemy_angle = []        
ENEMY_SPEED = 3.5 
num_of_enemies = 6     

def reset_enemies():
    global enemyX, enemyY, enemy_angle, enemyImg
    enemyImg = []
    enemyX = []
    enemyY = []
    enemy_angle = []
    for _i in range(num_of_enemies):
        raw_enemy = pygame.image.load('images-removebg-preview.png')
        scaled_enemy = pygame.transform.scale(raw_enemy, (64, 64))
        enemyImg.append(scaled_enemy)
        enemyX.append(random.randint(50, SCREEN_WIDTH - 50))
        enemyY.append(random.randint(40, 200))
        enemy_angle.append(random.uniform(0, 2 * math.pi)) 

reset_enemies()

# Bullet Configuration
bulletImg = pygame.image.load('istockphoto-1317164844-612x612-removebg-preview.png')
bulletImg = pygame.transform.scale(bulletImg, (16, 16))

bullets = [] 
fire_timer = 0

# UI/Stats Setup
score_value = 0
player_lives = 3 
font = pygame.font.Font('Angel wish.otf', 32) 
textX = 10
textY = 10
over_font = pygame.font.Font('Black Mustang.ttf', 64)

game_over = False

def show_stats(x, y):
    score_text = font.render(f"Score : {score_value}", True, (255, 255, 255))
    lives_text = font.render(f"Lives : {player_lives}", True, (255, 50, 50) if player_lives == 1 else (50, 255, 50))
    screen.blit(score_text, (x, y))
    screen.blit(lives_text, (x, y + 35))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"Score: {score_value} | Press 'R' to Restart", True, (255, 255, 255))
    screen.blit(over_text, (200, 200))
    screen.blit(score_text, (190, 280))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def isCollision(x1, y1, x2, y2, threshold):
    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance < threshold

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                score_value = 0
                player_lives = 3
                playerX = PLAYER_START_X
                playerY = PLAYER_START_Y
                player_angle = 0
                bullets.clear()
                reset_enemies()
                game_over = False

    if not game_over:
        keys = pygame.key.get_pressed()

        # Turning Handling
        if keys[pygame.K_a]:
            player_angle += ROTATION_SPEED
        if keys[pygame.K_d]:
            player_angle -= ROTATION_SPEED

        # 4-Way Movement
        if keys[pygame.K_LEFT]:
            playerX -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            playerX += PLAYER_SPEED
        if keys[pygame.K_UP]:
            playerY -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            playerY += PLAYER_SPEED

        playerX = max(0, min(playerX, SCREEN_WIDTH - 64))
        playerY = max(0, min(playerY, SCREEN_HEIGHT - 64))

        # Submachine Gun Trigger
        if fire_timer > 0:
            fire_timer -= 1

        if keys[pygame.K_SPACE] and fire_timer == 0:
            rad = math.radians(player_angle + 90)
            b_speed_x = math.cos(rad) * BULLET_SPEED
            b_speed_y = -math.sin(rad) * BULLET_SPEED 
            
            spawn_x = playerX + 32
            spawn_y = playerY + 32
            bullets.append([spawn_x, spawn_y, b_speed_x, b_speed_y])
            fire_timer = FIRE_COOLDOWN  

        # Translate Projectiles (Fixed vector tracking)
        for bullet in bullets[:]:
            bullet[0] += bullet[2]  
            bullet[1] += bullet[3]  
            screen.blit(bulletImg, (int(bullet[0] - 8), int(bullet[1] - 8)))
            if bullet[0] < 0 or bullet[0] > SCREEN_WIDTH or bullet[1] < 0 or bullet[1] > SCREEN_HEIGHT:
                bullets.remove(bullet)

        # Omnidirectional Enemy Behavior
        for i in range(num_of_enemies):
            enemyX[i] += math.cos(enemy_angle[i]) * ENEMY_SPEED
            enemyY[i] += math.sin(enemy_angle[i]) * ENEMY_SPEED

            # Edge Bouncing Deflection Logic
            if enemyX[i] <= 0 or enemyX[i] >= SCREEN_WIDTH - 64:
                enemy_angle[i] = math.pi - enemy_angle[i] 
            if enemyY[i] <= 0 or enemyY[i] >= SCREEN_HEIGHT - 64:
                enemy_angle[i] = -enemy_angle[i]          

            # Bullet vs Enemy Threat Intersection
            for bullet in bullets[:]:
                if isCollision(enemyX[i] + 32, enemyY[i] + 32, bullet[0], bullet[1], COLLISION_DISTANCE):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    score_value += 1
                    enemyX[i] = random.randint(50, SCREEN_WIDTH - 50)
                    enemyY[i] = random.randint(40, 200)
                    enemy_angle[i] = random.uniform(0, 2 * math.pi)

            # Enemy vs Player Intersection Damage
            if isCollision(enemyX[i] + 32, enemyY[i] + 32, playerX + 32, playerY + 32, PLAYER_HIT_DISTANCE):
                player_lives -= 1
                bullets.clear() 
                if player_lives <= 0:
                    game_over = True
                else:
                    playerX = PLAYER_START_X
                    playerY = PLAYER_START_Y
                    player_angle = 0
                    enemyX[i] = random.randint(50, SCREEN_WIDTH - 50)
                    enemyY[i] = random.randint(40, 200)

            enemy(enemyX[i], enemyY[i], i)

        # Render Rotated Character Surface
        rotated_playerImg = pygame.transform.rotate(playerImg_original, player_angle)
        new_rect = rotated_playerImg.get_rect(center=playerImg_original.get_rect(topleft=(playerX, playerY)).center)
        screen.blit(rotated_playerImg, new_rect.topleft)
        
        show_stats(textX, textY)
    else:
        game_over_text()

    pygame.display.update()
    clock.tick(60)
pygame.quit
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shadow Knight 2D")
clock = pygame.time.Clock()

# Colors (Dark shadow theme)
BACKGROUND_COLOR = (15, 15, 20)
GROUND_COLOR = (30, 30, 40)
SILHOUETTE_WHITE = (240, 240, 240)
ENEMY_SHADOW = (60, 20, 20)
SLASH_BLUE = (0, 255, 255)
HEALTH_RED = (200, 30, 30)

# Environment setup
platforms = [
    pygame.Rect(0, 520, SCREEN_WIDTH, 80),        # Main Ground
    pygame.Rect(250, 400, 300, 20),                # Floating Platform
]

# Player configuration
player = pygame.Rect(100, 400, 40, 60)
player_vel_x = 5
player_vel_y = 0
is_grounded = False
is_attacking = False
attack_timer = 0
attack_rect = pygame.Rect(0, 0, 0, 0)
facing_right = True

# Enemy configuration
enemy = pygame.Rect(600, 460, 40, 60)
enemy_speed = 2
enemy_health = 100

# Main Game Loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)
    
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and is_grounded:
                player_vel_y = -19  # Jump impulse
                is_grounded = False
            if event.key == pygame.K_SPACE and not is_attacking:
                is_attacking = True
                attack_timer = 10  # Duration of the slash in frames

    # 2. Player Input & Movement
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_LEFT]:
        dx = -player_vel_x
        facing_right = False
    if keys[pygame.K_RIGHT]:
        dx = player_vel_x
        facing_right = True

    # Apply Gravity
    player_vel_y += 0.8  # Gravity acceleration
    if player_vel_y > 15:
        player_vel_y = 15

    # Move Player and Handle Collisions X/Y
    player.x += dx
    for platform in platforms:
        if player.colliderect(platform):
            if dx > 0: player.right = platform.left
            if dx < 0: player.left = platform.right

    player.y += player_vel_y
    is_grounded = False
    for platform in platforms:
        if player.colliderect(platform):
            if player_vel_y > 0:
                player.bottom = platform.top
                player_vel_y = 0
                is_grounded = True
            elif player_vel_y < 0:
                player.top = platform.bottom
                player_vel_y = 0

    # 3. Enemy AI and Combat Processing
    # Basic tracking AI
    if enemy_health > 0:
        if enemy.x < player.x:
            enemy.x += enemy_speed
        elif enemy.x > player.x:
            enemy.x -= enemy_speed

    # Attack Hitbox Logic
    if is_attacking:
        if facing_right:
            attack_rect = pygame.Rect(player.right, player.y + 15, 45, 30)
        else:
            attack_rect = pygame.Rect(player.left - 45, player.y + 15, 45, 30)
            
        # Hit detection
        if attack_rect.colliderect(enemy) and enemy_health > 0:
            enemy_health -= 2  # Deal continuous damage during active slash frames
            
        attack_timer -= 1
        if attack_timer <= 0:
            is_attacking = False

    # 4. Rendering everything
    # Draw Static Environment
    for platform in platforms:
        pygame.draw.rect(screen, GROUND_COLOR, platform)

    # Draw Enemy Health Bar & Body
    if enemy_health > 0:
        pygame.draw.rect(screen, ENEMY_SHADOW, enemy)
        # Health Bar tracking above head
        pygame.draw.rect(screen, HEALTH_RED, (enemy.x, enemy.y - 15, int(enemy.width * (enemy_health / 100)), 6))

    # Draw Player Silhouette
    pygame.draw.rect(screen, SILHOUETTE_WHITE, player)
    
    # Draw Visual Neon Attack Slash
    if is_attacking:
        pygame.draw.rect(screen, SLASH_BLUE, attack_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()




