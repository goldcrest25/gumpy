import pygame
import game_canvas


class Platform(pygame.sprite.Sprite):
    
    PLATFORM_HEIGHT = 20
    PLATFORM_COLOR = (255, 0, 0)

    def __init__(self):
        super().__init__()

        self.surf = pygame.Surface((game_canvas.WIDTH, self.PLATFORM_HEIGHT))
        self.surf.fill(self.PLATFORM_COLOR)
        
        self.rect = self.surf.get_rect(
            center = (game_canvas.WIDTH // 2, 
                game_canvas.HEIGHT - self.PLATFORM_HEIGHT // 2))
    
