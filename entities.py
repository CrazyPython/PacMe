import pygame
import tmx
import random

class Direction:
    NORTH, EAST, SOUTH, WEST = xrange(4)
    directions = [NORTH, EAST, SOUTH, WEST]
    directionVector = {NORTH : (-1, 0),
                       EAST : (0, 1),
                       SOUTH : (1, 0),
                       WEST : (0, -1)}
    
    @staticmethod
    def getReverse(direction):
        return direction+2 % len(Direction.directions)

class MovingSprite(pygame.sprite.Sprite):
    
    def __init__(self, image, location, direction, speed, *groups):
        super(MovingSprite, self).__init__(*groups)
        self.spawn = location
        self.currentDirection = direction
        self.rect = pygame.rect.Rect(location, image.get_size())
        self.speed = speed
        self.image = image
        
    def finalMoveWithConformingCollision(self, dt, game):
        lastRect = self.rect.copy()
        
        if self.currentDirection == Direction.WEST:
            self.rect.x -= self.speed * dt
        if self.currentDirection == Direction.EAST:
            self.rect.x += self.speed * dt
        if self.currentDirection == Direction.NORTH:
            self.rect.y -= self.speed * dt
        if self.currentDirection == Direction.SOUTH:
            self.rect.y += self.speed * dt
            

        # conforming collision (push the sprite bang even to the wall, if there is a collision)
        inflated = self.rect.inflate(-2., -2.)
        newRect = self.rect
        
        for cell in game.tilemap.layers['triggers'].collide(inflated, 'blockers'):
            # find the actual value of the blockers property
            blockers = cell['blockers']
            # now for each side set in the blocker check for collision; only
            # collide if we transition through the blocker side (to avoid
            # false-positives) and align the player with the side collided to
            # make things neater

            if 'l' in blockers and lastRect.right <= cell.left and newRect.right > cell.left:
                newRect.right = cell.left
            if 'r' in blockers and lastRect.left >= cell.right and newRect.left < cell.right:
                newRect.left = cell.right
            if 't' in blockers and lastRect.bottom <= cell.top and newRect.bottom > cell.top:
                newRect.bottom = cell.top
            if 'b' in blockers and lastRect.top >= cell.bottom and newRect.top < cell.bottom:
                newRect.top = cell.bottom
        
        self.rect = newRect

class GhostState:
    ENRAGED, CALM = xrange(2)

class GhostColor:
    PINK, GREEN, BLUE, RED = xrange(4)
    ghostColors = [PINK, GREEN, BLUE, RED]

class Ghost(MovingSprite):
    pink_images = {Direction.NORTH : pygame.image.load('res/images/monster_pink.png'),
              Direction.EAST : pygame.image.load('res/images/monster_pink.png'),
              Direction.SOUTH : pygame.image.load('res/images/monster_pink.png'),
              Direction.WEST : pygame.image.load('res/images/monster_pink.png')}

    green_images = {Direction.NORTH : pygame.image.load('res/images/monster_green.png'),
              Direction.EAST : pygame.image.load('res/images/monster_green.png'),
              Direction.SOUTH : pygame.image.load('res/images/monster_green.png'),
              Direction.WEST : pygame.image.load('res/images/monster_green.png')}

    blue_images = {Direction.NORTH : pygame.image.load('res/images/monster_blue.png'),
              Direction.EAST : pygame.image.load('res/images/monster_blue.png'),
              Direction.SOUTH : pygame.image.load('res/images/monster_blue.png'),
              Direction.WEST : pygame.image.load('res/images/monster_blue.png')}

    red_images = {Direction.NORTH : pygame.image.load('res/images/monster_red.png'),
              Direction.EAST : pygame.image.load('res/images/monster_red.png'),
              Direction.SOUTH : pygame.image.load('res/images/monster_red.png'),
              Direction.WEST : pygame.image.load('res/images/monster_red.png')}

    images = {GhostColor.PINK: pink_images,
             GhostColor.GREEN: green_images ,
             GhostColor.BLUE: blue_images ,
             GhostColor.RED: red_images}

    def __init__(self, location, direction, color, *groups):
        super(Ghost, self).__init__(self.images[color][direction], location, direction, 130, *groups)
        self.state = GhostState.ENRAGED
        self.color = color

    def update(self, dt, game):
        lastRect = self.rect
        
        # movement AI
        if len(game.tilemap.layers['free'].collide(lastRect, 'free')) == 1:
            for cell in game.tilemap.layers['free'].collide(lastRect, 'free'):
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
                
                if self.currentDirection in possible:
                    if random.randint(0,10/len(possible)) == 0:
                        while not direction in possible:
                            direction = random.randint(0,3)
                    else:
                        direction = self.currentDirection
                else:
                    while not direction in possible:
                        direction = random.randint(0,3)
                
                if direction == Direction.getReverse(self.currentDirection):
                    if random.randint(0,1) == 0:
                        direction = self.currentDirection
                self.currentDirection = direction
        # movement AI END
        
        # update image    
        self.image = self.images[self.color][self.currentDirection]
        
        # execute movement and enforce conforming collision
        self.finalMoveWithConformingCollision(dt, game)
        
        # player collision
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
        # TODO
        pass

class PlayerState:
    NORMAL, HURT = xrange(2)

class Player(MovingSprite):
    images = {Direction.NORTH : pygame.image.load('res/images/me_top.png'),
              Direction.EAST : pygame.image.load('res/images/me_right.png'),
              Direction.SOUTH : pygame.image.load('res/images/me_bottom.png'),
              Direction.WEST : pygame.image.load('res/images/me_left.png')}

    def __init__(self, location, direction, *groups):
        super(Player, self).__init__(self.images[direction], location, direction, 130, *groups)
        self.lives = 3
        self.state = PlayerState.NORMAL
        self.timeHurt = 0
        print str(self.rect)
        
    def center(self):
        # currently not used
        x1, y1 = self.rect.topleft
        x2, y2 = self.rect.bottomright
        return ((x1 + x2)/2.0, (y1 + y2)/2.0)
        
    def update(self, dt, game):
        last = self.rect.copy()

        # movement commanded by player key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.currentDirection = Direction.WEST
        if key[pygame.K_RIGHT] and not key[pygame.K_LEFT]:
            self.currentDirection = Direction.EAST
        if key[pygame.K_UP] and not key[pygame.K_DOWN]:
            self.currentDirection = Direction.NORTH
        if key[pygame.K_DOWN] and not key[pygame.K_UP]:
            self.currentDirection = Direction.SOUTH
        
        self.image = self.images[self.currentDirection]

        # actual movement + conforming collision
        self.finalMoveWithConformingCollision(dt, game)
        
        # set focus to follow player
        game.tilemap.set_focus(self.rect.x, self.rect.y)
        
        # invincibility check after being hurt
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