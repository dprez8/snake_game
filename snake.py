import pygame
import random
import pandas as pd
import time

# Initialize pygame
pygame.init()

# Set up display
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Colors
white = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
black = (0, 0, 0)

# Snake properties
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_dir = "RIGHT"
change_to = snake_dir

# Food properties
food_pos = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
food_spawn = True

# Score
score = 0

# Initialize clock
clock = pygame.time.Clock()

# Movement history
counter = 0
history = pd.DataFrame()

# Game over function
def get_rel_fruit_distance():

    def get_rel_distance_up():
        return (food_pos[0] - snake_pos[0], snake_pos[1] - food_pos[1])

    def get_rel_distance_right():
        return (food_pos[1] - snake_pos[1], food_pos[0] - snake_pos[0])

    if snake_dir == "UP":
        return get_rel_distance_up()
    if snake_dir == "DOWN":
        return tuple(-1 * x for x in get_rel_distance_up())
    if snake_dir == "LEFT":
        return tuple(-1 * x for x in get_rel_distance_right())
    if snake_dir == "RIGHT":
        return get_rel_distance_right()

def get_rel_wall_distance():

    distance_up = snake_pos[1]
    distance_down = height - 10 - snake_pos[1]
    distance_right = width - 10 - snake_pos[0]
    distance_left = snake_pos[0]

    # FRONT - RIGHT - LEFT
    if snake_dir == "UP":
        return (distance_up, distance_right, distance_left)
    if snake_dir == "DOWN":
        return (distance_down, distance_left, distance_right)
    if snake_dir == "LEFT":
        return (distance_left, distance_up, distance_down)
    if snake_dir == "RIGHT":
        return (distance_right, distance_down, distance_up)

def get_rel_body_distance():

    aux_up = [pos[1] for pos in filter(lambda pos: pos[0] == snake_pos[0] and pos[1] < snake_pos[1], snake_body)]
    distance_up = snake_pos[1] - max(aux_up) - 10 if len(aux_up) > 0 else None
   
    aux_down = [pos[1] for pos in filter(lambda pos: pos[0] == snake_pos[0] and pos[1] > snake_pos[1], snake_body)]
    distance_down = min(aux_down) - snake_pos[1] - 10 if len(aux_down) > 0 else None

    aux_right = [pos[0] for pos in filter(lambda pos: pos[1] == snake_pos[1] and pos[0] > snake_pos[0], snake_body)]
    distance_right = min(aux_right) - snake_pos[0] - 10 if len(aux_right) > 0 else None 

    aux_left = [pos[0] for pos in filter(lambda pos: pos[1] == snake_pos[1] and pos[0] < snake_pos[0], snake_body)]
    distance_left = snake_pos[0] - max(aux_left) - 10 if len(aux_left) > 0 else None

    # FRONT - RIGHT - LEFT
    if snake_dir == "UP":
        return (distance_up, distance_right, distance_left)
    if snake_dir == "DOWN":
        return (distance_down, distance_left, distance_right)
    if snake_dir == "LEFT":
        return (distance_left, distance_up, distance_down)
    if snake_dir == "RIGHT":
        return (distance_right, distance_down, distance_up)

def add_move():
    register = {}

    global counter
    register["count"] = counter
    counter += 1
    register["rel_hor_dist_obj"], register["rel_vert_dist_obj"] = get_rel_fruit_distance()
    register["rel_front_dist_wall"], register["rel_right_dist_wall"], register["rel_left_dist_wall"] = get_rel_wall_distance()
    register["rel_front_dist_body"], register["rel_right_dist_body"], register["rel_left_dist_body"] = get_rel_body_distance()
    register["snake_pos_x"] = snake_pos[0]
    register["snake_pos_y"] = snake_pos[1]
    register["snake_dir"] = last_dir
    register["snake_next_dir"] = change_to
    register["score"] = score

    return register

def game_over():
    history.to_csv("history.csv")
    my_font = pygame.font.SysFont("times new roman", 50)
    game_over_surface = my_font.render("Your Score is: " + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (width/2, height/4)
    screen.fill(white)
    screen.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(5)
    pygame.quit()
    quit()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        # Arrow keys to control snake
        keys = pygame.key.get_pressed()
        for key in keys:
            if keys[pygame.K_UP]:
                change_to = "UP"
            if keys[pygame.K_DOWN]:
                change_to = "DOWN"
            if keys[pygame.K_LEFT]:
                change_to = "LEFT"
            if keys[pygame.K_RIGHT]:
                change_to = "RIGHT"

    # Validation of direction
    last_dir = snake_dir
    if change_to == "UP" and not snake_dir == "DOWN":
        snake_dir = "UP"
    if change_to == "DOWN" and not snake_dir == "UP":
        snake_dir = "DOWN"
    if change_to == "LEFT" and not snake_dir == "RIGHT":
        snake_dir = "LEFT"
    if change_to == "RIGHT" and not snake_dir == "LEFT":
        snake_dir = "RIGHT"

    # Moving the snake
    if snake_dir == "UP":
        snake_pos[1] -= 10
    if snake_dir == "DOWN":
        snake_pos[1] += 10
    if snake_dir == "LEFT":
        snake_pos[0] -= 10
    if snake_dir == "RIGHT":
        snake_pos[0] += 10

    print(add_move())
    history = history._append(add_move(), ignore_index=True)

    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
    else:
        snake_body.pop()

    if not food_spawn:
        food_pos = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
        food_spawn = True

    # Draw snake and food
    screen.fill(white)
    for pos in snake_body:
        pygame.draw.rect(screen, green, pygame.Rect(pos[0], pos[1], 10, 10))
    
    
    if snake_dir == "UP":
        pygame.draw.rect(screen, black, pygame.Rect(snake_pos[0]+ 1, snake_pos[1] + 3, 3, 3))
        pygame.draw.rect(screen, black, pygame.Rect(snake_pos[0]+ 6, snake_pos[1] + 3, 3, 3))
    if snake_dir == "DOWN":
        pygame.draw.rect(screen, black, pygame.Rect(snake_pos[0]+ 1, snake_pos[1] + 2, 3, 3))
        pygame.draw.rect(screen, black, pygame.Rect(snake_pos[0]+ 6, snake_pos[1] + 2, 3, 3))
    if snake_dir == "LEFT":
        pygame.draw.rect(screen, black, pygame.Rect(snake_pos[0], snake_pos[1] + 2, 3, 3))
        pygame.draw.rect(screen, black, pygame.Rect(snake_pos[0]+ 5, snake_pos[1] + 2, 3, 3))
    if snake_dir == "RIGHT":
        pygame.draw.rect(screen, black, pygame.Rect(snake_pos[0]+ 2, snake_pos[1] + 2, 3, 3))
        pygame.draw.rect(screen, black, pygame.Rect(snake_pos[0]+ 7, snake_pos[1] + 2, 3, 3))
    
    pygame.draw.rect(screen, red, pygame.Rect(food_pos[0], food_pos[1], 10, 10))
    pygame.draw.rect(screen, white, pygame.Rect(food_pos[0], food_pos[1], 2, 2))
    pygame.draw.rect(screen, white, pygame.Rect(food_pos[0]+8, food_pos[1], 2, 2))
    pygame.draw.rect(screen, white, pygame.Rect(food_pos[0], food_pos[1]+8, 2, 2))
    pygame.draw.rect(screen, white, pygame.Rect(food_pos[0]+8, food_pos[1]+8, 2, 2))
    pygame.draw.rect(screen, green, pygame.Rect(food_pos[0]+5, food_pos[1]-1, 4, 2))

    # Game Over conditions
    if snake_pos[0] < 0 or snake_pos[0] > width-10:
        game_over()
    if snake_pos[1] < 0 or snake_pos[1] > height-10:
        game_over()

    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()

    pygame.display.update()
    clock.tick(5)


    


