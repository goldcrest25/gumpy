import pygame
from pygame.locals import *
from pygame.surface import Surface
import game_canvas
import general_physics
import math
from typing import Optional
from enum import IntFlag

vec = pygame.math.Vector2

#region "Private" stuff
__PLAYER_SIZE__ = (24, 30)

class PlayerState(IntFlag):
    # FEDCBA9876543210
    # DS#####LRJFW4321

    #region Basic members
    NONE = 0    # Shouldn't occur
    STATE1 = 1
    STATE2 = 2
    STATE3 = 4
    STATE4 = 8
    WALK = 16
    FALL = 32
    JUMP = 64
    RIGHT = 128
    LEFT = 256
    STAND = 16384
    DIE = 32768
    #endregion

    #region Compound enumeration members
    DIRECTIONAL = LEFT | RIGHT

    WALK_RIGHT_1 = WALK | RIGHT | STATE1
    WALK_RIGHT_2 = WALK | RIGHT | STATE2
    WALK_RIGHT_3 = WALK | RIGHT | STATE3
    WALK_RIGHT_4 = WALK | RIGHT | STATE4

    WALK_LEFT_1 = WALK | LEFT | STATE1
    WALK_LEFT_2 = WALK | LEFT | STATE2
    WALK_LEFT_3 = WALK | LEFT | STATE3
    WALK_LEFT_4 = WALK | LEFT | STATE4

    FALL_RIGHT = FALL | RIGHT
    FALL_LEFT = FALL | LEFT

    JUMP_RIGHT = JUMP | RIGHT
    JUMP_LEFT = JUMP | LEFT
    #endregion

class PlayerSprites(pygame.sprite.Sprite):   
    # This is a singleton, so setup logic in subclass and 
    # override self.init to return instantiation of subclass if already done

    class __PlayerSpritesSingle(pygame.sprite.Sprite):
        __PLAYER_STATES__ = [
            # Straight states
            PlayerState.STAND,
            PlayerState.FALL,
            PlayerState.JUMP,
            PlayerState.DIE,
            # Directional states
            PlayerState.WALK_RIGHT_1,
            PlayerState.WALK_RIGHT_2,
            PlayerState.WALK_RIGHT_3,
            PlayerState.WALK_RIGHT_4,
            PlayerState.FALL_RIGHT,
            PlayerState.JUMP_RIGHT,
            PlayerState.WALK_LEFT_1,
            PlayerState.WALK_LEFT_2,
            PlayerState.WALK_LEFT_3,
            PlayerState.WALK_LEFT_4,
            PlayerState.FALL_LEFT,
            PlayerState.JUMP_LEFT,
        ]
        
        # (The graphics can only be loaded upon initialisation)
        Graphics = { state: pygame.Surface(__PLAYER_SIZE__) for state in __PLAYER_STATES__ }

        __SPRITE_FILEPATH_CONVENTION__ = "assets/graphics/player/{file}.png"

        def __init__(self):
            super().__init__()

            for state in self.__PLAYER_STATES__:
                stateName = "gump-" + state.name.lower().replace("_", "-")
                filepath = self.__SPRITE_FILEPATH_CONVENTION__.format(file = stateName)
                print("Acquiring: ""{filepath}""".format(filepath = filepath))
                self.Graphics[state] = pygame.image.load(filepath).convert()
                self.Graphics[state].set_colorkey(game_canvas.SPRITE_TRANSPARENT_COLOR)

    instance = None

    def __init__(self):
        if not PlayerSprites.instance:
            PlayerSprites.instance = PlayerSprites.__PlayerSpritesSingle()
    
    def Get(self, state) -> pygame.Surface:
        return PlayerSprites.instance.Graphics[state]

#endregion

class Player(pygame.sprite.Sprite):

    # Position and dimensions
    PLAYER_SIZE = (24, 30)
    PLAYER_CENTER = (PLAYER_SIZE[0] // 2, PLAYER_SIZE[1] // 2)
    PLAYER_STARTING_POSITION = (10, 0)

    # Physics
    PLAYER_JUMP_VELOCITY = 8
    PLAYER_ACCELERATION = 0.5
    PLAYER_FRICTION = 0.12
    
    def __init__(self):
        super().__init__() 

        # Initialize position
        self.pos = vec(
            self.PLAYER_STARTING_POSITION[0] + self.PLAYER_CENTER[0], 
            self.PLAYER_STARTING_POSITION[1] + self.PLAYER_CENTER[1])
        self.vel = vec(0,0)
        self.acc = vec(0,0)

        # Initialize state
        self.on_ground = False
        self.current_state = PlayerState.NONE   # For diagnostic purposes
        self.animation_frame = 0
        
        # Configure image
        self.image = self.__current_graphic__()
        self.rect = self.image.get_rect()

    def move(self):
        # Base acceleration on the player character
        self.acc = vec(0, general_physics.GRAVITY)
    
        # Register what has been pressed
        pressed_keys = pygame.key.get_pressed()
                
        if pressed_keys[K_LEFT]:
            self.acc.x = -self.PLAYER_ACCELERATION
        if pressed_keys[K_RIGHT]:
            self.acc.x = self.PLAYER_ACCELERATION
        if pressed_keys[K_UP]:
            self.jump()

        # Adjust acceleration, velocity and position
        self.acc.x += self.vel.x * -self.PLAYER_FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        
        # Ensure player doesn't wander off the edge of the screen
        if self.pos.x > game_canvas.WIDTH - self.PLAYER_CENTER[0]:
            self.pos.x = game_canvas.WIDTH - self.PLAYER_CENTER[0]
        if self.pos.x < self.PLAYER_CENTER[0]:
            self.pos.x = self.PLAYER_CENTER[0]

        # Reposition sprite to position
        self.rect.midbottom = self.pos
    
    def update(self, platforms):
        # If the player is falling, determine which platforms if any are colliding
        if self.vel.y > 0:
            top = self.__platform_top__(platforms)
            if top != None:
                self.pos.y = top + 1    # +1 so that the player doesn't continually collide
                self.vel.y = 0
                self.on_ground = True
            else:
                self.on_ground = False
        self.image = self.__current_graphic__()
    
    def jump(self):
        if(self.on_ground):
            self.vel.y = -self.PLAYER_JUMP_VELOCITY
            self.on_ground = False

    # Determine which platforms if any are colliding with the player, and returns the topmost y-coord
    def __platform_top__(self, platforms) -> Optional[int]:
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            return min([hit.rect.top for hit in hits])
        return None
    
    # Determine current state of player
    def __current_state__(self) -> PlayerState:
        def __current_animation_frame__(self) -> PlayerState:
            # Advance the player frame every 4 frames
            current_frame = self.animation_frame
            self.animation_frame = (current_frame + 1) % 16
            # Account for enumeration (i.e. STATE_1, etc)
            return 1 << (current_frame // 4)
        CLOSE_ENOUGH_TO_ZERO = 0.05

        # Player can be either moving left or right
        # (treat values below 0.05 as "zero")
        state = PlayerState.RIGHT if (self.vel.x > CLOSE_ENOUGH_TO_ZERO) \
            else PlayerState.LEFT if (self.vel.x < -CLOSE_ENOUGH_TO_ZERO) \
            else PlayerState.NONE

        if(self.on_ground):
            # Player is either standing there or walking
            if(math.fabs(self.vel.x) < CLOSE_ENOUGH_TO_ZERO):
                state |= PlayerState.STAND
            else:
                state |= PlayerState.WALK
                state |= __current_animation_frame__(self)
        else:
            # Player is either rising (after jumping) or falling
            if(self.vel.y < 0):
                state |= PlayerState.JUMP
            else:
                state |= PlayerState.FALL
        
        if(self.current_state != state):
            #print("New state: {state}".format(state = state))
            self.current_state = state
        return state
    
    def __current_graphic__(self) -> pygame.Surface:
        return PlayerSprites().Get(self.__current_state__())
