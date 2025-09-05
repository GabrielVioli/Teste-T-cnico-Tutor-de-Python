import pgzrun
from pgzero.keyboard import keys

# configurações de tela
WIDTH = 800
HEIGHT = 533

# Player
player = Actor('respirando1')
player.pos = 400, 490

# Animação correndo
running_frame = True
frame_counter = 0
animation_speed = 5
facing_right = True

# pulo
jumping = False
jump_time = 0
jump_frames = 10  

# Background
bg_x = 0  

ground_img = Actor('chao')
ground_img.pos = 400, 540

def update():
    global running_frame, frame_counter, facing_right, jumping, jump_time, bg_x

    moving = False
    movement = 0

    # movimento na horizontal
    if keyboard.LEFT:
        player.x -= 2
        facing_right = False
        moving = True
        movement = -4

    elif keyboard.RIGHT:
        player.x += 2
        facing_right = True
        moving = True
        movement = 4

    # animacao correndo
    if moving:
        frame_counter += 1
        if frame_counter >= animation_speed:
            running_frame = not running_frame
            frame_counter = 0
        if facing_right:
            player.image = 'correndo1' if running_frame else 'correndo2'
        else:
            player.image = 'correndo1_esq' if running_frame else 'correndo2_esq'
    else:
        player.image = 'respirando1' if facing_right else 'respirando1_esq'
        frame_counter = 0

    # logica do pulo
    if jumping:
        jump_time += 1
        if jump_time >= jump_frames:
            player.y += 50
            jumping = False
            jump_time = 0

    # limites da janela
    if player.left < 0:
        player.left = 0
    if player.right > WIDTH:
        player.right = WIDTH
    if player.top < 0:
        player.top = 0
    if player.bottom > HEIGHT:
        player.bottom = HEIGHT

    # Parallax
    if facing_right and moving:
        bg_x -= 0.2 * 4  

    # repetir o fundo
    if bg_x <= -WIDTH:
        bg_x = 0
    elif bg_x >= WIDTH:
        bg_x = 0

def on_key_down(key):
    global jumping, jump_time
    if key == keys.SPACE and not jumping:
        player.y -= 50  
        jumping = True
        jump_time = 0

def draw():
    screen.blit('initial_background', (bg_x, 0))
    screen.blit('initial_background', (bg_x + WIDTH, 0))
    
    # Draw player
    player.draw()
    ground_img.draw()

pgzrun.go()
