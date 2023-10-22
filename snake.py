import pygame
import random
import pandas as pd
import time
import datetime
from sklearn import tree
import os
import numpy as np
import pickle

from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder

#  Cleaning data
def clean(df):
    def get_next_move(row):
    
        moves_values = {
            "UP": {"LEFT": "LEFT", "UP": "FRONT", "RIGHT": "RIGHT", "DOWN": None},
            "RIGHT": {"UP": "LEFT", "RIGHT": "FRONT", "DOWN": "RIGHT", "LEFT": None},
            "DOWN": {"RIGHT": "LEFT", "DOWN": "FRONT", "LEFT": "RIGHT", "UP": None},
            "LEFT": {"DOWN": "LEFT", "LEFT": "FRONT", "UP": "RIGHT", "RIGHT": None}
        }

        #print(f'{row["snake_dir"]} - {row["snake_next_dir"]} - {moves_values[row["snake_dir"]][row["snake_next_dir"]]}')

        return moves_values[row["snake_dir"]][row["snake_next_dir"]]

    def sign(x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0

    df["snake_dir"] = df["snake_dir"].shift(-1)
    df["snake_next_dir"] = df["snake_next_dir"].shift(-1)
    print(df.shape)
    df.dropna(subset= ["snake_next_dir", "snake_dir"], inplace= True)
    print(df.shape)
    
    df["snake_next_move"] =  df.apply(get_next_move, axis = 1)

    df["rel_front_dist_min"] = df[['rel_front_dist_wall','rel_front_dist_body']].min(axis=1)
    df["rel_right_dist_min"] = df[['rel_right_dist_wall','rel_right_dist_body']].min(axis=1)
    df["rel_left_dist_min"] = df[['rel_left_dist_wall','rel_left_dist_body']].min(axis=1)

    return df

path = "registers/train"
file_names = os.listdir(path)

train_obs = pd.DataFrame()
for file_name in file_names:
    df = pd.read_csv(os.path.join(path,file_name))[:-50]
    df = clean(df)
    print(df.shape)
    train_obs = pd.concat([train_obs, df], axis=0)

train_obs.to_csv("train_obs.csv")


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

# Tree
def get_next_move(row):
    
    moves_values = {
        "UP": {"LEFT": "LEFT", "UP": "FRONT", "RIGHT": "RIGHT", "DOWN": None},
        "RIGHT": {"UP": "LEFT", "RIGHT": "FRONT", "DOWN": "RIGHT", "LEFT": None},
        "DOWN": {"RIGHT": "LEFT", "DOWN": "FRONT", "LEFT": "RIGHT", "UP": None},
        "LEFT": {"DOWN": "LEFT", "LEFT": "FRONT", "UP": "RIGHT", "RIGHT": None}
    }
    #print(f'{row["snake_dir"]} - {row["snake_next_dir"]} - {moves_values[row["snake_dir"]][row["snake_next_dir"]]}')
    return moves_values[row["snake_dir"]][row["snake_next_dir"]]

def get_next_dir(move):
    moves = {
        "UP": {"LEFT": "LEFT", "FRONT": "UP","RIGHT": "RIGHT"},
        "RIGHT": {"LEFT": "UP", "FRONT": "RIGHT","RIGHT": "DOWN"},
        "DOWN": {"LEFT": "RIGHT", "FRONT": "DOWN","RIGHT": "LEFT"},
        "LEFT":{"LEFT": "DOWN", "FRONT": "LEFT","RIGHT": "UP"}
    }

    return moves[snake_dir][move]

def get_status():
    rel_hor_dist_obj, rel_vert_dist_obj = get_rel_fruit_distance()
    rel_front_dist_wall, rel_right_dist_wall, rel_left_dist_wall = get_rel_wall_distance()
    rel_front_dist_body, rel_right_dist_body, rel_left_dist_body = get_rel_body_distance()

    return [rel_hor_dist_obj, rel_vert_dist_obj, min(i for i in [rel_front_dist_wall, rel_front_dist_body] if i is not None), min(i for i in [rel_right_dist_body, rel_right_dist_wall] if i is not None), min(i for i in [rel_left_dist_body, rel_left_dist_wall] if i is not None)]
#
#, rel_front_dist_wall, rel_right_dist_wall, rel_left_dist_wall, rel_front_dist_body, rel_right_dist_body, rel_left_dist_body, min(i for i in [rel_front_dist_wall, rel_front_dist_body] if i is not None), min(i for i in [rel_right_dist_body, rel_right_dist_wall] if i is not None), min(i for i in [rel_left_dist_body, rel_left_dist_wall] if i is not None)
    

register = pd.read_csv("clean_obs.csv")

# relleno nulls con pared
#register['rel_front_dist_body'] = register['rel_front_dist_body'].fillna(register['rel_front_dist_wall'])
#register['rel_right_dist_body'] = register['rel_right_dist_body'].fillna(register['rel_right_dist_wall'])
#register['rel_left_dist_body'] = register['rel_left_dist_body'].fillna(register['rel_left_dist_wall'])

#register["snake_next_move"] =  register.apply(get_next_move, axis = 1)
register.dropna(subset= ["snake_true_next_move"], inplace= True)

print(register.shape)

#register_1 = register.loc[register["snake_next_move"] != "FRONT"]
#register_2 = register.loc[register["snake_next_move"] == "FRONT"]

#register =  pd.concat([register_1, register_2], axis=0)
print(register)

model_name = "rna_300_6_alpha_03"
x = register[["rel_hor_dist_obj", "rel_vert_dist_obj","rel_front_dist_min","rel_right_dist_min", "rel_left_dist_min"]]
x = x.values
#,"rel_front_dist_wall","rel_right_dist_wall","rel_left_dist_wall","rel_front_dist_body","rel_right_dist_body","rel_left_dist_body",,"rel_front_dist_min","rel_right_dist_min","rel_left_dist_min"
y = register["snake_true_next_move"]
#label_encoder = OneHotEncoder(sparse=False)
#y = label_encoder.fit_transform(np.array(y).reshape(-1, 1))

clfs = [MLPClassifier(hidden_layer_sizes=(500,500,500,500,500,500), alpha=0.3, verbose = True, max_iter=500).fit(x, y),
        MLPClassifier(hidden_layer_sizes=(500,500,500,500,500,500), alpha=0.3, verbose = True, max_iter=500).fit(x, y),]
# #print(f'Best loss 1: {clfs[0].best_loss_}')
# #print(f'Best loss 2: {clfs[1].best_loss_}')
# save
with open(f'{model_name}_clf1.pkl', 'wb') as f:
    pickle.dump(clfs[0], f)
with open(f'{model_name}_clf2.pkl', 'wb') as f:
    pickle.dump(clfs[1], f)

# load
# with open(f'{model_name}_clf1.pkl', 'rb') as f:
#     clf1 = pickle.load(f)
# with open(f'{model_name}_clf2.pkl', 'rb') as f:
#     clf2 = pickle.load(f)
# clfs = [clf1, clf2]

#clf = tree.DecisionTreeClassifier()
#clf = clf.fit(x, y)

# Register methods
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
    register["snake_dir"] = last_dir
    register["snake_next_dir"] = change_to
    register["score"] = score

    return register

# Game over function
def game_over():
    os.makedirs(f"registers/model_run/{model_name}", exist_ok=True )
    clean(history)[:-1].to_csv(f"registers/model_run/{model_name}/{str(datetime.datetime.now()).replace('.', '-').replace(':', '-')}.csv")
    #update csv with best loss
    pd.DataFrame([clfs[0].best_loss_]).to_csv(f"registers/model_run/{model_name}/best_loss.csv")
    my_font = pygame.font.SysFont("times new roman", 50)
    game_over_surface = my_font.render("Your Score is: " + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (width/2, height/4)
    screen.fill(white)
    screen.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    quit()

# Main game loop
while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over()
            pygame.quit()
            quit()

        # Arrow keys to control snake
        
        
    print(get_status())
    selected_clf = random.choice(clfs)
    prediction = selected_clf.predict([get_status()])[0]
    print(prediction)
    change_to = get_next_dir(prediction)
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

    #print(add_move())
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
        game_over()
    if snake_pos[1] < 0 or snake_pos[1] > height-10:
        game_over()

    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()

    pygame.display.update()
    clock.tick(200)


    

