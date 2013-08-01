import pygame
import tmx
import random

class Direction:
    NORTH, EAST, SOUTH, WEST = xrange(4)
    directions = [NORTH, EAST, SOUTH, WEST]
    DirectionVector = {NORTH : (-1, 0),
                       EAST : (0, 1),
                       SOUTH : (1, 0),
                       WEST : (0, -1)}

class GhostState:
    ENRAGED, CALM = xrange(2)

class Ghost(pygame.sprite.Sprite):
    image = pygame.image.load('res/images/enemy_big.png')

    def __init__(self, location, *groups):
        super(Ghost, self).__init__(*groups)
        self.spawn = location
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.state = GhostState.ENRAGED
        self.currentDirection = Direction.WEST
        self.speed = 150

    def update(self, dt, game):
        last = self.rect
        new = self.rect.move(Direction.DirectionVector[self.currentDirection])

        for cell in game.tilemap.layers['free'].collide(last, 'free'):
            direction = -1
            possible = []
            hallway = cell['free'] 
            if 't' in hallway:
                possible.append(Direction.NORTH)
            if 'b' in hallway:
                possible.append(Direction.SOUTH)
            if 'l' in hallway:
                possible.append(Direction.WEST)
            if 'r' in hallway:
                possible.append(Direction.EAST)
                
            while not direction in possible:
                direction = random.randint(0,3)
                
        self.currentDirection = direction 
            

        if self.currentDirection == Direction.WEST:
            self.rect.x -= self.speed * dt
        if self.currentDirection == Direction.EAST:
            self.rect.x += self.speed * dt
        if self.currentDirection == Direction.NORTH:
            self.rect.y -= self.speed * dt
        if self.currentDirection == Direction.SOUTH:
            self.rect.y += self.speed * dt
            

        # conforming collision (push the player bang even to the wall)
        if self.currentDirection == Direction.NORTH or self.currentDirection == Direction.SOUTH:
            pass
        if self.currentDirection == Direction.WEST or self.currentDirection == Direction.EAST:
            pass
        test = self.rect.inflate(-2., -2.)
        new = self.rect
        
        for cell in game.tilemap.layers['triggers'].collide(test, 'blockers'):
            # find the actual value of the blockers property
            blockers = cell['blockers']
            # now for each side set in the blocker check for collision; only
            # collide if we transition through the blocker side (to avoid
            # false-positives) and align the player with the side collided to
            # make things neater

            if 'l' in blockers and last.right <= cell.left and new.right > cell.left:
                new.right = cell.left
            if 'r' in blockers and last.left >= cell.right and new.left < cell.right:
                new.left = cell.right
            if 't' in blockers and last.bottom <= cell.top and new.bottom > cell.top:
                new.bottom = cell.top
            if 'b' in blockers and last.top >= cell.bottom and new.top < cell.bottom:
                new.top = cell.bottom
                
        if self.rect.colliderect(game.player.rect):
            if self.state == GhostState.ENRAGED:
                if (game.player.state == PlayerState.HURT):
                    pass
                    
                elif (game.player.state == PlayerState.NORMAL):
                    game.sounds[game.enemydying].play()
                    game.player.lives -= 1
                    game.points -= 500
                    game.player.state = PlayerState.HURT
            if self.state == GhostState.CALM:
                self.respawn()
                game.points += 100
    def respawn(self):
        # gg
        pass

class PlayerState:
    NORMAL, HURT = xrange(2)

class Player(pygame.sprite.Sprite):
    images = {Direction.NORTH : pygame.image.load('res/images/me_top.png'),
              Direction.EAST : pygame.image.load('res/images/me_right.png'),
              Direction.SOUTH : pygame.image.load('res/images/me_bottom.png'),
              Direction.WEST : pygame.image.load('res/images/me_left.png')}

    def __init__(self, location, direction, *groups):
        super(Player, self).__init__(*groups)
        self.spawn = location
        self.currentDirection = direction
        self.nextDirection = direction
        self.lives = 3
        self.image = self.images[self.currentDirection]
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.speed = 150
        self.state = PlayerState.NORMAL
        self.timeHurt = 0
        print str(self.rect)
        
    def center(self):
        x1, y1 = self.rect.topleft
        x2, y2 = self.rect.bottomright
        return ((x1 + x2)/2.0, (y1 + y2)/2.0)
    
    def findDirection(self, game):
        direction = self.nextDirection
        for blocker in game.tilemap.layers['triggers'].collide(self.rect, 'blockers'):
            print "blocker: " + str(blocker)
            if self.nextDirection == Direction.WEST or self.nextDirection == Direction.EAST:
                
                if blocker.top + 1 < self.rect.bottom:
                    print "A"
                    direction = self.currentDirection
                    break
                if blocker.bottom - 1 > self.rect.top:
                    print "B"
                    direction = self.currentDirection
                    break
            if self.nextDirection == Direction.NORTH or self.nextDirection == Direction.SOUTH:
                if blocker.left + 1 < self.rect.right:
                    print "C"
                    direction = self.currentDirection
                    break
                if blocker.right - 1 < self.rect.left:
                    print "D"
                    direction = self.currentDirection
                    break
        
        self.currentDirection = direction
    
    def loseLife(self):
        self.lives -= 1
        self.game
            
    
    def update(self, dt, game):
        last = self.rect.copy()

        key = pygame.key.get_pressed()
        
        
        if key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.nextDirection = Direction.WEST
        if key[pygame.K_RIGHT] and not key[pygame.K_LEFT]:
            self.nextDirection = Direction.EAST
        if key[pygame.K_UP] and not key[pygame.K_DOWN]:
            self.nextDirection = Direction.NORTH
        if key[pygame.K_DOWN] and not key[pygame.K_UP]:
            self.nextDirection = Direction.SOUTH
        
        self.currentDirection = self.nextDirection
        # self.findDirection(game)
            
            
        if self.currentDirection == Direction.WEST:
            self.rect.x -= self.speed * dt
        if self.currentDirection == Direction.EAST:
            self.rect.x += self.speed * dt
        if self.currentDirection == Direction.NORTH:
            self.rect.y -= self.speed * dt
        if self.currentDirection == Direction.SOUTH:
            self.rect.y += self.speed * dt
            
        self.image = self.images[self.currentDirection]

        # conforming collision (push the player bang even to the wall)
        if self.currentDirection == Direction.NORTH or self.currentDirection == Direction.SOUTH:
            pass
        if self.currentDirection == Direction.WEST or self.currentDirection == Direction.EAST:
            pass
        test = self.rect.inflate(-2., -2.)
        new = self.rect
        
        for cell in game.tilemap.layers['triggers'].collide(test, 'blockers'):
            # find the actual value of the blockers property
            blockers = cell['blockers']
            # now for each side set in the blocker check for collision; only
            # collide if we transition through the blocker side (to avoid
            # false-positives) and align the player with the side collided to
            # make things neater

            if 'l' in blockers and last.right <= cell.left and new.right > cell.left:
                new.right = cell.left
            if 'r' in blockers and last.left >= cell.right and new.left < cell.right:
                new.left = cell.right
            if 't' in blockers and last.bottom <= cell.top and new.bottom > cell.top:
                new.bottom = cell.top
            if 'b' in blockers and last.top >= cell.bottom and new.top < cell.bottom:
                new.top = cell.bottom
        game.tilemap.set_focus(new.x, new.y)
        
        
        if (self.state == PlayerState.HURT):
            self.timeHurt += dt
            if (self.timeHurt > 3):
                self.timeHurt = 0
                self.state = PlayerState.NORMAL
        

class Corn(pygame.sprite.Sprite):
    image = pygame.image.load('res/images/corn.png')

    def __init__(self, location, *groups):
        super(Corn, self).__init__(*groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())

    def update(self, dt, game):
        if self.rect.colliderect(game.player.rect):
            game.points += 5
            game.sounds[game.pickup].play()
            self.kill()