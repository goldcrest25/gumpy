import sys
import pygame
from pygame.locals import *
import game_canvas
from player import Player
from platform import Platform
 
pygame.init()

vec = pygame.math.Vector2  # 2 for two dimensional
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode(
    game_canvas.CANVAS_SIZE,
    pygame.SCALED)
pygame.display.set_caption(game_canvas.CAPTION)

Player = Player()
BasePlatform = Platform()

Platforms = pygame.sprite.Group()
Platforms.add(BasePlatform)

ImageSprites = pygame.sprite.Group()
ImageSprites.add(Player)
 
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    # Movement
    Player.move()

    # Updates
    Player.update(Platforms)

    # Show stuff
    displaysurface.fill(game_canvas.COLOR)          # Background
    for plat in Platforms:                          # Platforms
        displaysurface.blit(plat.surf, plat.rect)
    ImageSprites.draw(displaysurface)               # Image sprites
    

    pygame.display.update()
    FramePerSec.tick(game_canvas.FPS)
