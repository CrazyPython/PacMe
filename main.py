import pygame
import pygame.font
import entities, resources
import tmx
import pyglet
import random
from kezmenu import KezMenu



class PrintLocation:
    TOP = (10, 20)
    BOTTOM = (10, -20)

class Game(object):
    def __init__(self):
        # total points
        self.points = 0
        # time passed in seconds
        self.timePassed = 0
        # sound cache
        self.sounds = resources.PygletSoundCache()
        # list of available sounds
        print "Loading ..."
        self.enemydying = 'res/sounds/Jump.wav'
        self.pickup = 'res/sounds/Powerup.wav'
        self.levelup = 'res/sounds/levelup.wav'
        
        # cache
        self.sounds[self.enemydying]
        self.sounds[self.pickup]
        self.sounds[self.levelup]
        print "Loaded"
        # TODO: make those paths configurable
    
    def main(self, screen):
        # new clock
        clock = pygame.time.Clock()
        # tmx magic
        self.tilemap = tmx.load('level1.tmx', screen.get_size())
        self.sprites = tmx.SpriteLayer()
        self.enemies = tmx.SpriteLayer()
        self.corns = tmx.SpriteLayer()
        
        
        for corn in self.tilemap.layers['triggers'].find('corn'):
            entities.Corn((corn.px, corn.py), self.corns) 
        self.tilemap.layers.append(self.corns)
        
        color = entities.GhostColor.PINK
        direction = entities.Direction.WEST
        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            # randomly choose a color and direction from the given possibilities
            if (len(enemy['color']) >= 1):
                rand = random.randint(0, len(enemy['color']) - 1)
                color = entities.GhostColor.ghostColors[int(enemy['color'][rand])]
            else:
                color = entities.GhostColor.PINK
                
            if (len(enemy['direction'])>= 1):
                rand = random.randint(0, len(enemy['direction']) - 1)
                direction = entities.Direction.charToDirection(enemy['direction'][rand])
            else:
                direction = entities.Direction.WEST
            entities.Ghost((enemy.px + 4, enemy.py + 4), direction, color, self.enemies)
        
        self.tilemap.layers.append(self.enemies)
            
        # access the triggers layer and return all player sprites (spawn points)
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = entities.Player((start_cell.px, start_cell.py), entities.Direction.EAST, self.sprites)
        self.tilemap.layers.append(self.sprites)
        
        info = False
        while True:
            # cap at 30 frames per second, returning the time from last call
            seconds_passed = clock.tick(30) / 1000.0

            # don't miss closing events!
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # TODO: find out the cause of "AL lib: ReleaseALC: 1 device not closed" 
                    
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
                x,y = screen.get_size()
                # see http://stackoverflow.com/a/498103/1176596
                self.printOnScreen(repr(self.points), map(sum,zip(PrintLocation.BOTTOM,(0, y))))

                
            if (self.player.lives <= 0):
                self.printOnScreen("Dead", PrintLocation.TOP)
            
            # switch screen buffer and actual screen
            pygame.display.flip()
        
    def printOnScreen(self, message, PrintLocation):
        myfont = pygame.font.SysFont("Monospace", 15)
        label = myfont.render(message, 1, (255,255,0))
        screen.blit(label, PrintLocation)
        
if __name__ == '__main__':
    # init pygame and create a screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    game = Game()
    game.main(screen)