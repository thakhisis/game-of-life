"""
Game of Life
"""

""""""

import datetime
from enum import Enum
from random import random
import arcade
import PIL

# Constants
CELL_RATIO = 0.5
CELL_WIDTH = 32
CELL_HEIGHT = 32

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Game of Life"

CELL_SCALING = 1

LAYER_NAME_ALL = "AllCells"
LAYER_NAME_ALIVE = "AliveCells"
LAYER_NAME_DEAD = "DeadCells"

# Speed is number of seconds between updates
EVOLVE_DELAY = 0.5

def create_textures():
    """ Create a list of images for sprites based on the global colors. """
    color = (255, 0,   0, 255)
    image = PIL.Image.new('RGBA', (CELL_WIDTH, CELL_HEIGHT), color)
    color_texture = arcade.Texture(str(color), image=image)
    
    return [arcade.load_texture("assets/dead.png"), arcade.load_texture("assets/alive.png"), color_texture ]

texture_list = create_textures()

def new_cells(game):
    """ Create a 2D array of dead cells. """
    cells = []
    for x in range(0, SCREEN_WIDTH, CELL_WIDTH):
        for y in range(0, SCREEN_HEIGHT, CELL_HEIGHT):
            cell = Cell(game, x, y, False)
            cells.append(cell)
    return cells

class CellAction(Enum):
    NONE = 0
    SPAWN = 1
    KILL = 2

class Cell(arcade.Sprite):
    def __init__(self, game, x, y, alive):
        super().__init__()
        for texture in texture_list:
            self.append_texture(texture)
        self.is_alive = alive
        self.set_texture(0)
        self.center_x = x + CELL_WIDTH / 2
        self.center_y = y + CELL_HEIGHT / 2
        self.action = CellAction.NONE
        self.game = game
        self.hit_box = [[-1-CELL_WIDTH/2, -1-CELL_HEIGHT/2], [1+CELL_WIDTH/2, -1-CELL_HEIGHT/2], [1+CELL_WIDTH/2, 1+CELL_HEIGHT/2], [-1-CELL_WIDTH/2, 1+CELL_HEIGHT/2]]

    def evolve(self):
        collisions = arcade.check_for_collision_with_list(self, self.game.scene[LAYER_NAME_ALIVE])
        count_neighbours = len(collisions)

        if self.is_alive and (count_neighbours < 2 or count_neighbours > 3):
            self.action = CellAction.KILL
        elif not self.is_alive and count_neighbours == 3:
            self.action  = CellAction.SPAWN

    def update(self):
        
        super().update()

        if self.action == CellAction.KILL:
            self.is_alive = False
            self.set_texture(0)
            self.remove_from_sprite_lists()
            self.game.scene.add_sprite(LAYER_NAME_DEAD, self)
            self.game.scene.add_sprite(LAYER_NAME_ALL, self)
            
        if self.action == CellAction.SPAWN:
            self.is_alive = True
            self.set_texture(1)
            self.remove_from_sprite_lists()
            self.game.scene.add_sprite(LAYER_NAME_ALIVE, self) 
            self.game.scene.add_sprite(LAYER_NAME_ALL, self)


        self.action = CellAction.NONE
            
class MyGame(arcade.Window):
    """
    Main application class.
    """
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.GRAY)

        self.last_evolve = 0
        self.total_time = 0

        self.is_paused = False
        
        self.cells = None

        self.age = 0
    
    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Create the cells
        self.cells = new_cells(self)

        # Initialize the scene
        self.scene = arcade.Scene()

        # Create the sprite lists
        self.scene.add_sprite_list(LAYER_NAME_ALL, use_spatial_hash=False )
        self.scene.add_sprite_list(LAYER_NAME_ALIVE, use_spatial_hash=True)
        self.scene.add_sprite_list(LAYER_NAME_DEAD, use_spatial_hash=False)

        # Initialize the cells layers
        for cell in self.cells:
            self.scene[LAYER_NAME_ALL].append(cell)
            self.scene[LAYER_NAME_DEAD].append(cell)
        
        # Initialize the cells
        self.init_random()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.setup()
        elif key == arcade.key.SPACE:
            self.is_paused = not self.is_paused
        else:
            self.evolve()
        
    def should_evolve(self):
        if self.last_evolve is None or self.total_time > self.last_evolve + EVOLVE_DELAY:
            self.last_evolve = self.total_time
            return True
    
    def evolve(self):
        self.age += 1
        
        for cell in self.cells:
            cell.evolve()

        self.last_evolve = self.total_time

    def update(self, delta_time):
        """All the logic to move, and the game logic goes here."""

        if not self.is_paused:
            
            self.total_time += delta_time

            if self.should_evolve():
                self.evolve()

        self.scene.update([LAYER_NAME_ALL, LAYER_NAME_DEAD, LAYER_NAME_ALIVE])

    def on_draw(self):
        """Render the screen."""

        # Clear the scene
        self.clear()
        
        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Age: {self.age}"

        # Draw the relevant layers
        self.scene[LAYER_NAME_ALL].draw()
        #self.scene[LAYER_NAME_ALIVE].draw_hit_boxes(arcade.csscolor.WHITE)

        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18,
        )

    def init_random(self):
        """Randomly populate the grid"""
        for cell in self.cells:
            cell.action = CellAction.SPAWN if random() < CELL_RATIO else None

def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()