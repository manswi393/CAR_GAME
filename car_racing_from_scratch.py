# car_racing_from_scratch.py
import pygame, sys, random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing — From Scratch")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
ROAD = (45,45,45)
NEON = (255,200,0)
TREE = (20,120,20)
RED = (200,30,30)
BLUE = (40,120,255)
YELLOW = (255,215,0)
GREY = (110,110,110)

# Fonts
title_font = pygame.font.SysFont("Arial", 56, bold=True)
menu_font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 20)

# Game states
STATE_MENU = "menu"
STATE_CAR_SELECT = "car_select"
STATE_PLAY = "play"
STATE_GAME_OVER = "game_over"
state = STATE_MENU

# Car options (colors)
car_options = [RED, BLUE, YELLOW]
selected_car_color = RED

# Player car rect (x will change)
player_w, player_h = 50, 90
player_x = WIDTH // 2 - player_w // 2
player_y = HEIGHT - player_h - 30
player_rect = pygame.Rect(player_x, player_y, player_w, player_h)

# Enemy car (auto)
enemy_w, enemy_h = 50, 90
enemy_rect = pygame.Rect(WIDTH//2 - 150, -200, enemy_w, enemy_h)
enemy_speed = 6

# Obstacles (list of rects)
obstacles = []
obs_w, obs_h = 50, 50
for i in range(4):
    rx = random.randint(200, WIDTH-200)
    ry = random.randint(-1200, -100)
    obstacles.append(pygame.Rect(rx, ry, obs_w, obs_h))

# Controls / dynamics
side_speed = 8            # how fast player moves left-right
player_speed = 0.0        # our 'forward' influence (affects obstacle/enemy falling speed)
player_max_speed = 12.0
player_min_speed = 0.0

nitro_boost = 6.0
nitro_cooldown_frames = FPS * 2  # 2 seconds cooldown
nitro_available = True
nitro_timer = 0

# Score
score = 0.0

# Buttons helper
def button(rect, color, text, text_color=WHITE):
    pygame.draw.rect(screen, color, rect)
    t = menu_font.render(text, True, text_color)
    screen.blit(t, (rect.x + (rect.w - t.get_width())//2, rect.y + (rect.h - t.get_height())//2))

# Drawing road & decorations
def draw_road(scroll_offset=0):
    screen.fill((10,10,16))  # night sky
    road_x, road_w = 150, WIDTH - 300
    pygame.draw.rect(screen, ROAD, (road_x, 0, road_w, HEIGHT))
    # center dashed line
    dash_h = 30
    gap = 20
    center_x = WIDTH//2 - 5
    for y in range(- (scroll_offset % (dash_h+gap)), HEIGHT, dash_h+gap):
        pygame.draw.rect(screen, NEON, (center_x, y, 10, dash_h))
    # side trees (simple)
    for y in range(-200 + (scroll_offset//2 % 80), HEIGHT, 80):
        pygame.draw.rect(screen, TREE, (50, y, 24, 48))
        pygame.draw.rect(screen, TREE, (WIDTH-74, y+30, 24, 48))

# Menu screen
def draw_menu():
    draw_road()
    title = title_font.render("CAR RACING", True, NEON)
    screen.blit(title, ((WIDTH-title.get_width())//2, 120))
    play_btn = pygame.Rect((WIDTH//2 - 120, 260, 240, 60))
    car_btn = pygame.Rect((WIDTH//2 - 120, 340, 240, 60))
    button(play_btn, BLUE, "PLAY")
    button(car_btn, GREY, "CAR SELECT", BLACK)
    instr = small_font.render("Use ← → to steer, ↑ ↓ to change speed, SPACE for nitro", True, WHITE)
    screen.blit(instr, ((WIDTH-instr.get_width())//2, 430))
    return play_btn, car_btn

# Car select screen
def draw_car_select():
    draw_road()
    title = title_font.render("Choose Your Car", True, NEON)
    screen.blit(title, ((WIDTH-title.get_width())//2, 60))
    boxes = []
    for i, c in enumerate(car_options):
        bx = 200 + i*140
        rect = pygame.Rect(bx, 220, 100, 180)
        pygame.draw.rect(screen, c, rect)
        if c == selected_car_color:
            pygame.draw.rect(screen, WHITE, rect, 5)
        boxes.append(rect)
    back = pygame.Rect(20, 20, 100, 40)
    button(back, GREY, "MENU", BLACK)
    return boxes, back

# Game over screen
def draw_game_over():
    draw_road()
    ov = title_font.render("YOU CRASHED!", True, RED)
    scr = menu_font.render(f"Final score: {int(score)}", True, WHITE)
    retry = pygame.Rect((WIDTH//2 - 110, 340, 220, 55))
    screen.blit(ov, ((WIDTH-ov.get_width())//2, 160))
    screen.blit(scr, ((WIDTH-scr.get_width())//2, 240))
    button(retry, BLUE, "RETRY")
    return retry

# Game Loop
running = True
scroll_offset = 0

while running:
    dt = clock.tick(FPS)
    scroll_offset += int(player_speed)  # to animate road dashes & trees

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx,my = pygame.mouse.get_pos()
                play_btn, car_btn = draw_menu()
                if play_btn.collidepoint((mx,my)):
                    # reset some things then start
                    player_rect.x = WIDTH//2 - player_w//2
                    player_rect.y = player_y
                    enemy_rect.x = WIDTH//2 - 150
                    enemy_rect.y = -200
                    for o in obstacles:
                        o.x = random.randint(200, WIDTH-200)
                        o.y = random.randint(-1000, -50)
                    score = 0.0
                    player_speed = 0.0
                    nitro_available = True
                    nitro_timer = 0
                    state = STATE_PLAY
                if car_btn.collidepoint((mx,my)):
                    state = STATE_CAR_SELECT

        elif state == STATE_CAR_SELECT:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx,my = pygame.mouse.get_pos()
                boxes, back = draw_car_select()
                if back.collidepoint((mx,my)):
                    state = STATE_MENU
                for i, box in enumerate(boxes):
                    if box.collidepoint((mx,my)):
                        selected_car_color = car_options[i]

        elif state == STATE_PLAY:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx,my = pygame.mouse.get_pos()
                menu_btn = pygame.Rect(20, 20, 100, 40)
                if menu_btn.collidepoint((mx,my)):
                    state = STATE_MENU

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and nitro_available:
                    player_speed = min(player_speed + nitro_boost, player_max_speed + nitro_boost)
                    nitro_available = False
                    nitro_timer = nitro_cooldown_frames

        elif state == STATE_GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx,my = pygame.mouse.get_pos()
                retry_btn = draw_game_over()
                if retry_btn.collidepoint((mx,my)):
                    # reset to menu
                    state = STATE_MENU

    # STATE HANDLING
    keys = pygame.key.get_pressed()
    if state == STATE_MENU:
        draw_menu()

    elif state == STATE_CAR_SELECT:
        draw_car_select()

    elif state == STATE_PLAY:
        # controls
        if keys[pygame.K_LEFT]:
            player_rect.x -= side_speed
        if keys[pygame.K_RIGHT]:
            player_rect.x += side_speed
        if keys[pygame.K_UP]:
            player_speed = min(player_speed + 0.18, player_max_speed)
        if keys[pygame.K_DOWN]:
            player_speed = max(player_speed - 0.25, player_min_speed)

        # nitro cooldown countdown
        if not nitro_available:
            nitro_timer -= 1
            if nitro_timer <= 0:
                nitro_available = True

        # keep player on road bounds
        left_bound = 150
        right_bound = WIDTH - 150 - player_rect.w
        player_rect.x = max(left_bound, min(player_rect.x, right_bound))

        # move enemy & obstacles downward to simulate forward movement
        enemy_rect.y += enemy_speed + player_speed*0.4
        if enemy_rect.y > HEIGHT + 50:
            enemy_rect.x = random.randint(left_bound+20, right_bound-20)
            enemy_rect.y = random.randint(-800, -150)

        for o in obstacles:
            o.y += (4 + player_speed*0.5)
            if o.y > HEIGHT + 50:
                o.x = random.randint(left_bound+20, right_bound-20)
                o.y = random.randint(-900, -100)

        # scoring
        score += 0.1 + player_speed*0.02

        # draw
        draw_road(scroll_offset)
        # menu button
        menu_btn = pygame.Rect(20, 20, 100, 40)
        button(menu_btn, GREY, "MENU", BLACK)

        # draw enemy (use blue)
        pygame.draw.rect(screen, BLUE, enemy_rect)
        # draw player (selected color)
        pygame.draw.rect(screen, selected_car_color, player_rect)

        # draw obstacles (dark grey)
        for o in obstacles:
            pygame.draw.rect(screen, (80,80,80), o)

        # HUD
        speed_text = small_font.render(f"Speed: {round(player_speed,1)}", True, WHITE)
        score_text = small_font.render(f"Score: {int(score)}", True, WHITE)
        nitro_text = small_font.render(f"Nitro: {'Ready' if nitro_available else '...'}", True, WHITE)
        screen.blit(speed_text, (20, 520))
        screen.blit(score_text, (20, 550))
        screen.blit(nitro_text, (140, 520))

        # collisions -> game over
        crashed = player_rect.colliderect(enemy_rect) or any(player_rect.colliderect(o) for o in obstacles)
        if crashed:
            state = STATE_GAME_OVER

    elif state == STATE_GAME_OVER:
        draw_game_over()

    pygame.display.flip()

pygame.quit()
sys.exit()
