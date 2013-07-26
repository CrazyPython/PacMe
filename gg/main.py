import pygame
import pygame.font
import entities
import tmx
import pyglet
from kezmenu import KezMenu




class Game(object):
    # sounds
    enemydying = pyglet.resource.media('res/sounds/Jump.wav', streaming = False)
    pickup = pyglet.resource.media('res/sounds/Powerup.wav', streaming = False)
    levelup = pyglet.resource.media('res/sounds/levelup.wav', streaming = False)
    def main(self, screen):
        # new clock
        clock = pygame.time.Clock()
        # tmx magic
        self.tilemap = tmx.load('level1.tmx', screen.get_size())
        self.sprites = tmx.SpriteLayer()
        self.enemies = tmx.SpriteLayer()
        self.corns = tmx.SpriteLayer()
        self.points = 0
        # time passed in seconds
        self.timePassed = 0
        
        for corn in self.tilemap.layers['triggers'].find('corn'):
            entities.Corn((corn.px, corn.py), self.corns) 
        self.tilemap.layers.append(self.corns)
        
        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            entities.Ghost((enemy.px + 4, enemy.py + 4), self.enemies)
        print str(len(self.enemies))
        self.tilemap.layers.append(self.enemies)
            
        # access the triggers layer and return all player sprites (spawn points)
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = entities.Player((start_cell.px, start_cell.py), entities.Direction.RIGHT, self.sprites)
        self.tilemap.layers.append(self.sprites)
        
        info = False
        while True:
            # cap at 30 frames per second, returning the time from last call
            seconds_passed = clock.tick(30) / 1000.0

            # don't miss closing events!
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    self.player.rect = pygame.rect.Rect((32, 40), (16, 16))
                    self.player.currentDirection = entities.Direction.RIGHT
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    info = not info

            # update our sprites group
            self.tilemap.update(seconds_passed, self)

            # draw sprites
            self.tilemap.draw(screen)

            if (info):
                myfont = pygame.font.SysFont("Monospace", 15)
                label = myfont.render(repr(self.points), 1, (255,255,0))
                x,y = screen.get_size()
                screen.blit(label, (10, y-20))
                
            # switch screen buffer and actual screen
            pygame.display.flip()
        
if __name__ == '__main__':
    # init pygame and create a screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    game = Game()
    game.main(screen)