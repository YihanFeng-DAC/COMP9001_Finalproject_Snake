""" 
This is the main script. To run the game, execute this file.
This project uses pygame (external library) for graphics rendering.
Please run the code in a local Python environment, as Ed's environment does not support pygame.
"""
import pygame
import sys
import random
import time
import os

# initialize Pygame
pygame.init()

# --- Game constant definitions ---

# color defination
BG_COLOR = (230, 240, 255)  # bg color
SNAKE_BODY_COLOR = (119, 192, 100) 
SNAKE_HEAD_COLOR = (80, 150, 65)  # diff from snake body
FOOD_COLOR = (255, 153, 153) 
OBSTACLE_COLOR = (0, 0, 0) 
UI_BG_COLOR = (170, 200, 230)  # UI bg
TEXT_COLOR_DARK = (50, 70, 90)  # dark text
TEXT_COLOR_ON_UI = (255, 255, 255)  # white text
TITLE_TEXT_COLOR = (255, 223, 0)  # title
SELECTED_OPTION_COLOR = (255, 255, 150) # for difficulty selection

BORDER_RADIUS = 4  # snake body

# screen and block size
SCREEN_WIDTH = 600  # width
SCREEN_HEIGHT = 400  # height
BLOCK_SIZE = 10  # block size

# paras in game
MAX_SNAKE_SPEED = 30  # max speed of snack
OBSTACLE_INTERVAL = 4  # min interval(s) of creating obstacle

# define 3 difficulty level
DIFFICULTY_LEVELS = {
    "SIMPLE": {
        "initial_speed": 4,
        "speed_increment": 0.15,
        "max_obstacles": 10,
        "display_name": "1. Easy"
    },
    "MEDIUM": {
        "initial_speed": 6,
        "speed_increment": 0.25,
        "max_obstacles": 20,
        "display_name": "2. Medium"
    },
    "HARD": {
        "initial_speed": 8,
        "speed_increment": 0.35,
        "max_obstacles": 40,
        "display_name": "3. Hard"
    }
}

# --- Game object class definition ---
class Snake:
    """Manages the snake's behavior and attributes."""
    def __init__(self, block_size, screen_width, screen_height):
        """Initializes the snake."""
        self.block_size = block_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        """Resets the snake to its initial state."""
        self.x = self.screen_width / 2
        self.y = self.screen_height / 2
        self.x_change = 0
        self.y_change = 0
        self.body = [[self.x, self.y]]
        self.length = 1

    def move(self):
        """Moves the snake and updates its body."""
        self.x += self.x_change
        self.y += self.y_change
        head = [self.x, self.y]
        self.body.append(head)
        if len(self.body) > self.length:
            del self.body[0]
        return head

    def grow(self):
        """Increases the snake's length."""
        self.length += 1

    def change_direction(self, direction):
        """Changes the snake's movement direction."""
        if direction == "LEFT" and self.x_change == 0:
            self.x_change = -self.block_size; self.y_change = 0
        elif direction == "RIGHT" and self.x_change == 0:
            self.x_change = self.block_size; self.y_change = 0
        elif direction == "UP" and self.y_change == 0:
            self.y_change = -self.block_size; self.x_change = 0
        elif direction == "DOWN" and self.y_change == 0:
            self.y_change = self.block_size; self.x_change = 0
    
    def check_collision_wall(self):
        """Checks if the snake has hit a wall."""
        return self.x >= self.screen_width or self.x < 0 or \
               self.y >= self.screen_height or self.y < 0

    def check_collision_self(self):
        """Checks if the snake has hit itself."""
        return self.length > 1 and self.body[-1] in self.body[:-1]

    def draw(self, surface):
        """Draws the snake on the given surface."""
        for i, segment in enumerate(self.body):
            rect = pygame.Rect(segment[0], segment[1], self.block_size, self.block_size)
            color = SNAKE_HEAD_COLOR if i == len(self.body) - 1 else SNAKE_BODY_COLOR
            pygame.draw.rect(surface, color, rect, border_radius=BORDER_RADIUS)

class Food:
    """Manages the food's position and spawning."""
    def __init__(self, block_size, screen_width, screen_height):
        """Initializes the food."""
        self.block_size = block_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0 
        self.y = 0

    def _generate_pos(self):
        """Generates a random position for the food."""
        pos_x = round(random.randrange(0, self.screen_width - self.block_size) / self.block_size) * self.block_size
        pos_y = round(random.randrange(0, self.screen_height - self.block_size) / self.block_size) * self.block_size
        return pos_x, pos_y

    def respawn(self, snake_body, obstacles_pos):
        """Respawns food, avoiding snake and obstacles."""
        while True:
            self.x, self.y = self._generate_pos()
            food_pos_as_list = [self.x, self.y]
            is_on_snake = any(segment == food_pos_as_list for segment in snake_body)
            is_on_obstacle = any(obs_pos == food_pos_as_list for obs_pos in obstacles_pos)
            if not is_on_snake and not is_on_obstacle: break
    
    def draw(self, surface):
        """Draws the food (as a circle)."""
        center_x = self.x + self.block_size // 2
        center_y = self.y + self.block_size // 2
        radius = self.block_size // 2
        pygame.draw.circle(surface, FOOD_COLOR, (center_x, center_y), radius)

class Obstacle:
    """Manages a single obstacle."""
    def __init__(self, block_size, screen_width, screen_height, snake_body, food_pos, existing_obstacles_pos):
        """Initializes an obstacle."""
        self.block_size = block_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._generate_pos(snake_body, food_pos, existing_obstacles_pos)

    def _generate_pos(self, snake_body, food_pos, existing_obstacles_pos):
        """Generates a random position, avoiding conflicts."""
        while True:
            self.x = round(random.randrange(0, self.screen_width - self.block_size) / self.block_size) * self.block_size
            self.y = round(random.randrange(0, self.screen_height - self.block_size) / self.block_size) * self.block_size
            obstacle_pos_as_list = [self.x, self.y]
            is_on_snake = any(segment == obstacle_pos_as_list for segment in snake_body)
            is_on_food = (food_pos == obstacle_pos_as_list)
            is_on_existing_obstacle = any(obs_pos == obstacle_pos_as_list for obs_pos in existing_obstacles_pos)
            if not is_on_snake and not is_on_food and not is_on_existing_obstacle: break
    
    def get_pos(self):
        """Returns the obstacle's position."""
        return [self.x, self.y]

    def draw(self, surface):
        """Draws the obstacle (black square)."""
        rect = pygame.Rect(self.x, self.y, self.block_size, self.block_size)
        pygame.draw.rect(surface, OBSTACLE_COLOR, rect)

class Game:
    """Main class for managing the game flow and elements."""
    def __init__(self):
        """Initializes the game."""
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.block_size = BLOCK_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Snake Game - Difficulty Levels') # English caption

        base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "snake_icon.png")
        self.snake_icon = pygame.image.load(icon_path)
        self.snake_icon = pygame.transform.scale(self.snake_icon, (60, 60)) 

        self.clock = pygame.time.Clock()
        # Using common English fonts
        self.font_style = pygame.font.SysFont("arial", 30) 
        self.score_font = pygame.font.SysFont("arial", 25)
        self.title_font = pygame.font.SysFont("arial", 35) # Larger title font
        self.small_font = pygame.font.SysFont("arial", 22) 

        self.current_difficulty_settings = {} 
        self.game_state = "SELECT_DIFFICULTY"
        self.game_over_flag = False
        self.snake, self.food, self.obstacles = None, None, []
        self.score, self.current_speed, self.last_obstacle_spawn_time = 0, 0, 0

    def _display_message(self, msg, color, y_pos, font=None, center_x=True, x_pos=None):
        """Helper to display messages on screen. y_pos is absolute from top."""
        active_font = font if font else self.font_style
        message_surface = active_font.render(msg, True, color)
        if center_x:
            text_rect = message_surface.get_rect(center=(self.screen_width / 2, y_pos))
        else:
            text_rect = message_surface.get_rect(topleft=(x_pos if x_pos is not None else 0, y_pos))
        self.screen.blit(message_surface, text_rect)

    def _draw_score(self):
        """Draws the current score."""
        if self.game_state == "PLAYING":
             self._display_message(f"Score: {self.score}", TEXT_COLOR_DARK, 10, font=self.score_font, center_x=False, x_pos=10)

    def _spawn_obstacle(self):
        """Spawns new obstacles based on current difficulty."""
        current_time = time.time()
        if (current_time - self.last_obstacle_spawn_time) > OBSTACLE_INTERVAL:
            max_obs_for_difficulty = self.current_difficulty_settings.get("max_obstacles", 3)
            if len(self.obstacles) >= max_obs_for_difficulty:
                if self.obstacles: self.obstacles.pop(0)
            
            food_current_pos = [self.food.x, self.food.y]
            existing_obstacles_positions = [obs.get_pos() for obs in self.obstacles]
            new_obstacle = Obstacle(self.block_size, self.screen_width, self.screen_height,
                                    self.snake.body, food_current_pos, existing_obstacles_positions)
            self.obstacles.append(new_obstacle)
            self.last_obstacle_spawn_time = current_time
    
    def _reset_game_full(self):
        """Fully resets game state based on current difficulty."""
        self.snake = Snake(self.block_size, self.screen_width, self.screen_height)
        self.food = Food(self.block_size, self.screen_width, self.screen_height)
        self.obstacles = []
        self.food.respawn(self.snake.body, [])
        self.score = 0
        self.current_speed = self.current_difficulty_settings.get("initial_speed", 10)
        self.last_obstacle_spawn_time = time.time()

    
    def _draw_difficulty_selection_screen(self):
        """Draws the difficulty selection screen with game title and snake icon."""
        self.screen.fill(UI_BG_COLOR)

        # Title positioning
        game_title_y = self.screen_height * 0.15
        game_title_text = "Snake Game"

        # Get text surface to measure width
        title_surface = self.title_font.render(game_title_text, True, (0, 160, 0))

        title_rect = title_surface.get_rect(center=(self.screen_width // 2 + 40, game_title_y))

        # Icon position (to left of title)
        icon_size = 60
        icon_x = title_rect.left - icon_size - 10
        icon_y = game_title_y - icon_size // 2

        # Draw icon and title
        self.screen.blit(self.snake_icon, (icon_x, icon_y))
        self.screen.blit(title_surface, title_rect)

        # Difficulty Title
        difficulty_y = title_rect.bottom + 40
        self._display_message("Select Difficulty", TITLE_TEXT_COLOR, difficulty_y, font=self.title_font)

        # Difficulty options
        options_start_y = difficulty_y + 60
        option_spacing = 50
        for i, (key, level_info) in enumerate(DIFFICULTY_LEVELS.items()):
            display_text = level_info["display_name"]
            self._display_message(display_text, TEXT_COLOR_ON_UI, options_start_y + i * option_spacing, font=self.font_style)

        # Instruction
        instruction_y = options_start_y + len(DIFFICULTY_LEVELS) * option_spacing + 20
        self._display_message("Press 1, 2, or 3 to choose", TEXT_COLOR_ON_UI, instruction_y, font=self.small_font)

        pygame.display.update()


    def _handle_difficulty_selection_events(self):
        """Handles events on the difficulty selection screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.game_over_flag = True
            if event.type == pygame.KEYDOWN:
                key_map = {pygame.K_1: "SIMPLE", pygame.K_2: "MEDIUM", pygame.K_3: "HARD"}
                if event.key in key_map:
                    self.current_difficulty_settings = DIFFICULTY_LEVELS[key_map[event.key]]
                    self._reset_game_full()
                    self.game_state = "PLAYING"
                    if self.snake.x_change == 0 and self.snake.y_change == 0:
                        self.snake.change_direction("RIGHT")
                    self.last_obstacle_spawn_time = time.time()

    def _handle_game_over_screen_events(self):
        """Handles events on the game over screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.game_over_flag = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: self.game_over_flag = True
                if event.key == pygame.K_c: self.game_state = "SELECT_DIFFICULTY"
    
    def _handle_playing_events(self):
        """Handles events during active gameplay."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.game_over_flag = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  self.snake.change_direction("LEFT")
                elif event.key == pygame.K_RIGHT: self.snake.change_direction("RIGHT")
                elif event.key == pygame.K_UP:    self.snake.change_direction("UP")
                elif event.key == pygame.K_DOWN:  self.snake.change_direction("DOWN")

    def run(self):
        """Main game loop."""
        while not self.game_over_flag:
            if self.game_state == "SELECT_DIFFICULTY":
                self._draw_difficulty_selection_screen()
                self._handle_difficulty_selection_events()
                self.clock.tick(15)

            elif self.game_state == "PLAYING":
                self._handle_playing_events()
                snake_is_static_at_start = (self.snake.x_change == 0 and self.snake.y_change == 0 and self.score == 0)
                if not snake_is_static_at_start and self.snake: # Add check for self.snake
                    snake_head = self.snake.move()
                    if self.snake.check_collision_wall() or self.snake.check_collision_self():
                        self.game_state = "GAME_OVER_SCREEN"
                    for obs in self.obstacles:
                        if snake_head[0] == obs.x and snake_head[1] == obs.y:
                            self.game_state = "GAME_OVER_SCREEN"; break
                if self.game_state == "GAME_OVER_SCREEN": continue
                
                if not snake_is_static_at_start and self.snake and self.food: # Add checks
                    if self.snake.body[-1][0] == self.food.x and self.snake.body[-1][1] == self.food.y:
                        self.snake.grow()
                        self.score += 1
                        speed_increment = self.current_difficulty_settings.get("speed_increment", 0.2)
                        self.current_speed = min(MAX_SNAKE_SPEED, self.current_speed + speed_increment)
                        self.food.respawn(self.snake.body, [o.get_pos() for o in self.obstacles])
                
                if self.food: self._spawn_obstacle() # Ensure food exists before accessing its pos

                self.screen.fill(BG_COLOR)
                if self.snake: self.snake.draw(self.screen)
                if self.food: self.food.draw(self.screen)
                for obs in self.obstacles: obs.draw(self.screen)
                self._draw_score()
                pygame.display.update()
                self.clock.tick(self.current_speed if self.current_speed > 0 else 10)

            elif self.game_state == "GAME_OVER_SCREEN": 
                self.screen.fill(UI_BG_COLOR)
                self._display_message("Game Over!", OBSTACLE_COLOR, self.screen_height * 0.25, font=self.title_font)
                self._display_message(f"Your Score: {self.score}", TEXT_COLOR_ON_UI, self.screen_height * 0.45, font=self.font_style)
                self._display_message("Press C to Restart", TEXT_COLOR_ON_UI, self.screen_height * 0.65, font=self.font_style)
                self._display_message("Press Q to Quit", TEXT_COLOR_ON_UI, self.screen_height * 0.75, font=self.font_style)
                pygame.display.update()
                self._handle_game_over_screen_events()
                self.clock.tick(15)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()