import pygame
import random
import pandas as pd
import time
import datetime
from sklearn import tree


# Training
data = pd.read_csv('dataFloat.csv', sep=',')
# Iterate through rows using itertuples()
features = []
labels = []

for row in data.itertuples():
    features.insert(0,[row.count, row.rel_hor_dist_obj, row.rel_vert_dist_obj,row.rel_front_dist_wall, row.rel_right_dist_wall, row.rel_left_dist_wall,row.rel_front_dist_body, row.rel_right_dist_body, row.rel_left_dist_body,row.snake_pos_x, row.snake_pos_y, row.snake_dir, row.score])
    labels.append(row.snake_next_dir)

features.reverse()

classifier = tree.DecisionTreeClassifier()
classifier.fit(features,labels)

# Initialize pygame
pygame.init()

# Colors
white = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
black = (0, 0, 0)

# Button properties
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
BUTTON_COLOR = (0, 128, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_TEXT_SIZE = 36
BUTTON_PADDING = 20

# Set up display
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Snake properties
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_dir = "RIGHT"
last_dir = snake_dir
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
    register["rel_hor_dist_obj"], register["rel_vert_dist_obj"] = get_rel_fruit_distance()
    register["rel_front_dist_wall"], register["rel_right_dist_wall"], register["rel_left_dist_wall"] = get_rel_wall_distance()
    register["rel_front_dist_body"], register["rel_right_dist_body"], register["rel_left_dist_body"] = get_rel_body_distance()
    register["snake_pos_x"] = snake_pos[0]
    register["snake_pos_y"] = snake_pos[1]
    register["snake_dir"] = moves_to_float(last_dir)
    register["snake_next_dir"] = moves_to_float(change_to)
    register["score"] = score

    return register

def moves_to_float(move):
    case_dict = {
    'UP': 0,
    'RIGHT': 3,
    'DOWN': 6,
    'LEFT': 9
    }
    return case_dict.get(move, -1) 

def float_to_moves(float):
    case_dict = {
    0: 'UP',
    3: 'RIGHT',
    6: 'DOWN',
    9: 'LEFT'
    }
    return case_dict.get(float, -1)

def create_button(text, x, y):
    font = pygame.font.Font(None, BUTTON_TEXT_SIZE)
    button = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, BUTTON_COLOR, button)
    text_surface = font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=button.center)
    screen.blit(text_surface, text_rect)
    return button

def game_over(game_mode):  
    if (game_mode == "MANUAL"):
        history[:-1].to_csv(f"registers/{str(datetime.datetime.now()).replace('.', '-').replace(':', '-')}.csv")
    
    if(game_mode == "MANUAL" or game_mode == "AUTOMATIC"): 
        my_font = pygame.font.SysFont("times new roman", 50)
        game_over_surface = my_font.render("Your Score is: " + str(score), True, red)

    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (width/2, height/4)
    screen.fill(white)
    screen.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(1)
    pygame.quit()
    quit()

def game_loop(game_mode):

    global snake_dir, last_dir, change_to, history, counter, food_pos, food_spawn, score

    while True:
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over(game_mode)
                pygame.quit()
                quit()

        last_dir = snake_dir
        

        if(game_mode == "AUTOMATIC"):
            
            # Change direction from prediction
            register = add_move().copy()

            attributes = [[register["count"], register["rel_hor_dist_obj"], register["rel_vert_dist_obj"], register["rel_front_dist_wall"], register["rel_right_dist_wall"], register["rel_left_dist_wall"], register["rel_front_dist_body"], register["rel_right_dist_body"], register["rel_left_dist_body"], register["snake_pos_x"], register["snake_pos_y"], register["snake_dir"], register["score"]]]

            prediction = classifier.predict(attributes)[0]
            print(f"Prediccion: {prediction}")

            change_to = float_to_moves(prediction)
        
        elif(game_mode == "MANUAL"):
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
        counter += 1

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
            game_over(game_mode)
        if snake_pos[1] < 0 or snake_pos[1] > height-10:
            game_over(game_mode)

        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over(game_mode)

        pygame.display.update()
        clock.tick(5)

while True:
    game_mode = "UNSTARTED"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over(game_mode)
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if button1.collidepoint(event.pos):
                print("Button 1 clicked!")
                pygame.display.flip()
                game_mode = "MANUAL"
                game_loop(game_mode)

            elif button2.collidepoint(event.pos):
                print("Button 2 clicked!")
                pygame.display.flip()
                game_mode = "AUTOMATIC"
                game_loop(game_mode)

    screen.fill(white)

    button1 = create_button("Manual", width // 2 - BUTTON_WIDTH // 2, height // 2 - BUTTON_HEIGHT - BUTTON_PADDING)
    button2 = create_button("Automatic", width // 2 - BUTTON_WIDTH // 2, height // 2 + BUTTON_PADDING)

    pygame.display.flip()



    


