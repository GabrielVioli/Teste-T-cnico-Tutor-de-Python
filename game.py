import pgzrun
import random
import sys

# config das janelas 
WIDTH = 800
HEIGHT = 533
TITLE = "Caçador de Hollows"

# config do jogo
PLAYER_LIVES = 5
HOLLOWS_TO_WIN = 15
WALK_SPEED = 2
RUN_SPEED = 4
JUMP_STRENGTH = 12
GRAVITY = 0.5
ATTACK_DURATION = 20
FLOOR_TILE_SIZE = 50
GROUND_LEVEL = HEIGHT - FLOOR_TILE_SIZE
PARALLAX_SPEED = 0.5
FLOOR_PARALLAX_SPEED = 1.0
PLAYER_FEET_OFFSET = 8

# estado inicial
game_state = "start_menu"
sound_on = True
hollows_killed = 0

# elementos globais
player = Actor('respirando1')
player.pos = (100, GROUND_LEVEL)
player.bottom = GROUND_LEVEL + PLAYER_FEET_OFFSET
player.lives = PLAYER_LIVES
player.vy = 0
player.on_ground = True
player.facing_right = True
player.attack_timer = 0
player.anim_frame = 0
player.invincible_timer = 0
player.footstep_timer = 0

hollows = []
projectiles = []
hearts = []

bg_x = 0
floor_x = 0

# botões de men
start_button = Rect((WIDTH/2 - 100, 250), (200, 50))
sound_button = Rect((WIDTH/2 - 100, 320), (200, 50))
exit_button = Rect((WIDTH/2 - 100, 390), (200, 50))

hollow_spawn_timer = 240

def setup_hearts():
    hearts.clear()
    for i in range(player.lives):
        hearts.append(Actor('respirando1', (30 + i * 40, 30)))
        hearts[i].scale = 0.5

setup_hearts()

def draw():
    global bg_x, floor_x
    screen.blit('initial_background', (bg_x, 0))
    screen.blit('initial_background', (bg_x + WIDTH, 0))
    
    if game_state == "start_menu":
        draw_start_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        draw_end_screen("VOCÊ PERDEU!", "Tente novamente")
    elif game_state == "victory":
        draw_end_screen("VOCÊ VENCEU!", f"Você derrotou {HOLLOWS_TO_WIN} hollows!")

def draw_start_menu():
    screen.draw.text("Caçador de Hollows", center=(WIDTH/2, 150), fontsize=60, color="orange")
    screen.draw.filled_rect(start_button, "orange")
    screen.draw.text("Iniciar Jogo", center=start_button.center, fontsize=30, color="black")
    sound_text = "Som: LIGADO" if sound_on else "Som: DESLIGADO"
    screen.draw.filled_rect(sound_button, "orange")
    screen.draw.text(sound_text, center=sound_button.center, fontsize=30, color="black")
    screen.draw.filled_rect(exit_button, "red")
    screen.draw.text("Sair", center=exit_button.center, fontsize=30, color="white")

def draw_game():
    global floor_x
    num_tiles = (WIDTH // FLOOR_TILE_SIZE) + 2
    for i in range(num_tiles):
        screen.blit('bloco_chao', (floor_x + i * FLOOR_TILE_SIZE, GROUND_LEVEL))

    if player.invincible_timer % 10 < 5:
        player.draw()
    for hollow in hollows:
        hollow.draw()
    for projectile in projectiles:
        projectile.draw()
        
    screen.draw.text(f"Hollows Derrotados: {hollows_killed}", (WIDTH - 250, 20), fontsize=30, color="white")
    for heart in hearts:
        heart.draw()

def draw_end_screen(title, subtitle):
    screen.draw.text(title, center=(WIDTH/2, 200), fontsize=80, color="red")
    screen.draw.text(subtitle, center=(WIDTH/2, 300), fontsize=40, color="white")
    screen.draw.text("Pressione ENTER para voltar ao menu", center=(WIDTH/2, 400), fontsize=30, color="white")

def update():
    global bg_x, floor_x, game_state
    
    bg_x -= PARALLAX_SPEED
    if bg_x <= -WIDTH:
        bg_x = 0
        
    floor_x -= FLOOR_PARALLAX_SPEED
    if floor_x <= -FLOOR_TILE_SIZE:
        floor_x = 0
    
    if game_state == "playing":
        player.x -= PARALLAX_SPEED
        update_player()
        update_hollows()
        update_projectiles()
        check_collisions()

        if player.lives <= 0:
            music.stop()
            game_state = "game_over"
        elif hollows_killed >= HOLLOWS_TO_WIN:
            music.stop()
            game_state = "victory"

def update_player():
    running = True if keyboard.lshift or keyboard.rshift else False
    moving = False
    current_speed = RUN_SPEED if running else WALK_SPEED
    
    if player.attack_timer == 0:
        if keyboard.left and player.left > 0:
            player.x -= current_speed
            player.facing_right = False
            moving = True
        elif keyboard.right and player.right < WIDTH:
            player.x += current_speed
            player.facing_right = True
            moving = True

    if moving and player.on_ground:
        if player.footstep_timer <= 0:
            if sound_on:
                sounds.walking.play()
                player.footstep_timer = 25
        else:
            player.footstep_timer -= 1
    
    player.vy += GRAVITY
    player.y += player.vy
    
    if player.bottom > GROUND_LEVEL + PLAYER_FEET_OFFSET:
        player.bottom = GROUND_LEVEL + PLAYER_FEET_OFFSET
        player.vy = 0
        player.on_ground = True
    else:
        player.on_ground = False
        
    player.anim_frame = (player.anim_frame + 1) % 40 
    
    if player.attack_timer > 0:
        frame = 'ataque1' if player.attack_timer > ATTACK_DURATION / 2 else 'ataque2'
    elif moving and player.on_ground:
        if running:
            frame = 'correndo1' if player.anim_frame < 20 else 'correndo2'
        else:
            frame = 'andando1' if player.anim_frame < 20 else 'andando2'
    else:
        frame = 'respirando1' if player.anim_frame < 20 else 'respirando2'
    
    player.image = f"{frame}_esq" if not player.facing_right else frame
        
    if player.invincible_timer > 0:
        player.invincible_timer -= 1
    if player.attack_timer > 0:
        player.attack_timer -= 1

def update_hollows():
    global hollow_spawn_timer
    hollow_spawn_timer -= 1
    if hollow_spawn_timer <= 0:
        side = random.choice([-50, WIDTH + 50])
        hollow = Actor('hollow1')
        hollow.x = side
        hollow.bottom = GROUND_LEVEL + PLAYER_FEET_OFFSET
        hollow.speed = random.uniform(1.0, 2.0)
        hollow.attack_cooldown = random.randint(120, 240)
        hollows.append(hollow)
        hollow_spawn_timer = random.randint(240, 360) 

    for h in hollows[:]:
        if h.x < player.x:
            h.x += h.speed
            h.image = 'hollow1'
        else:
            h.x -= h.speed
            h.image = 'hollow1_esq'
        
        distance_to_player = abs(player.x - h.x)
        if distance_to_player < 300:
            h.attack_cooldown -= 1
            if h.attack_cooldown <= 0:
                direction_right = player.x > h.x
                proj_img = 'bola' if direction_right else 'bola_esq'
                projectile = Actor(proj_img)
                projectile.pos = h.pos
                projectile.direction = 1 if direction_right else -1
                projectiles.append(projectile)
                h.attack_cooldown = random.randint(180, 300)

def update_projectiles():
    for p in projectiles[:]:
        p.x += 5 * p.direction
        if not (0 < p.x < WIDTH):
            projectiles.remove(p)

def check_collisions():
    global hollows_killed
    
    # Colisão de ataque
    if player.attack_timer > 0:
        for h in hollows[:]:
            if player.colliderect(h):
                hollows.remove(h)
                hollows_killed += 1
    
    # Colisão do player com hollows ou ataques
    if player.invincible_timer == 0:
        for h in hollows[:]:
            if player.colliderect(h):
                player_hit()
                break
        for p in projectiles[:]:
            if player.colliderect(p):
                player_hit()
                projectiles.remove(p)
                break

def player_hit():
    player.lives -= 1
    player.invincible_timer = 60
    if hearts:
        hearts.pop()

def on_key_down(key):
    global game_state
    if game_state == "playing":
        if key == keys.SPACE and player.on_ground:
            player.vy = -JUMP_STRENGTH
            player.on_ground = False
        if key == keys.R and player.attack_timer == 0:
            if sound_on:
                sounds.ataque_espada.play()
            player.attack_timer = ATTACK_DURATION
    
    elif game_state in ["game_over", "victory"]:
        if key == keys.RETURN:
            reset_game()

def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == "start_menu":
        if start_button.collidepoint(pos):
            if sound_on:
                sounds.menu_clique.play()
                music.play('main_sound')
                music.set_volume(0.3)
            game_state = "playing"
        elif sound_button.collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                sounds.menu_clique.play()
                music.unpause()
            else:
                music.pause()
        elif exit_button.collidepoint(pos):
            sys.exit()

def reset_game():
    global game_state, hollows_killed
    music.stop()
    player.pos = (100, GROUND_LEVEL)
    player.bottom = GROUND_LEVEL + PLAYER_FEET_OFFSET
    player.lives = PLAYER_LIVES
    player.attack_timer = 0
    player.footstep_timer = 0
    hollows.clear()
    projectiles.clear()
    hollows_killed = 0
    setup_hearts()
    game_state = "start_menu"

pgzrun.go()