import pygame
import tmx
import random

class Direction:
    '''
    A class to be used to express directions.
    
    Also provides methods to convert from char to direction and receive a reversed
    direction. To be filled with more useful stuff.
    '''


    NORTH, EAST, SOUTH, WEST = xrange(4)
    directions = [NORTH, EAST, SOUTH, WEST]
    directionVector = {NORTH : (-1, 0),
                       EAST : (0, 1),
                       SOUTH : (1, 0),
                       WEST : (0, -1)}

    @staticmethod
    def getReverse(direction):
        '''
        Returns the reverse direction
        
        @param direction: a direction (NORTH, EAST, SOUTH, WEST)
        '''

        return direction + 2 % len(Direction.directions)

    @staticmethod
    def charToDirection(char):
        '''
        Converts a char (a string with length 1) to a direction.
        
        t, n: NORTH
        r, e: EAST
        b, s: SOUTH
        l, w: WEST
        '''
        if (char == 't' or char == 'n'):
            return Direction.NORTH
        if (char == 'r' or char == 'e'):
            return Direction.EAST
        if (char == 'b' or char == 's'):
            return Direction.SOUTH
        if (char == 'l' or char == 'w'):
            return Direction.WEST
        else:
            raise Exception, "Invalid direction"


class MovingSprite(pygame.sprite.Sprite):
    '''
    A class to represent moving Sprites such as the player or enemies.
    '''


    def __init__(self, game, image, location, direction, speed, *groups):
        '''
        Initialisation...
        '''
        super(MovingSprite, self).__init__(*groups)
        self.game = game
        self.spawn = location
        self.currentDirection = direction
        self.rect = pygame.rect.Rect(location, image.get_size())
        self.speed = speed
        self.image = image

    def update(self, dt):
        '''
        An update method which should be called regularly.
        
        @param dt: time passed since last call of this method, in seconds
        '''
        # movement actions
        self.planMovement()

        # execute movement and enforce conforming collision
        self.finalMovement(dt)

    def planMovement(self):
        '''
        Template method. This method should be used to plan the next
        move by handling manual input (keyboard, joystick, ...) or executing
        an AI.
        '''
        pass

    def finalMovement(self, dt):
        '''
        Tries to actually execute the planned movement.
        This method takes the passed time into account and the speed
        of this MovingSprite and moves the sprite accordingly to that.
        
        Also includes a conforming collision, that is:
        only collide if we transition through the blocker side
        (to avoid false-positives) and align the player with 
        the side collided to make things neater
        
        @param dt: time passed in seconds since last call of this method (or rather the update method)
        @see: planMovement
        
        '''
        lastRect = self.rect.copy()

        if self.currentDirection == Direction.WEST:
            self.rect.x -= self.speed * dt
        if self.currentDirection == Direction.EAST:
            self.rect.x += self.speed * dt
        if self.currentDirection == Direction.NORTH:
            self.rect.y -= self.speed * dt
        if self.currentDirection == Direction.SOUTH:
            self.rect.y += self.speed * dt


        # conforming collision
        inflated = self.rect.inflate(-2., -2.)
        newRect = self.rect

        for cell in self.game.tilemap.layers['triggers'].collide(inflated, 'blockers'):
            # find the actual value of the blockers property
            blockers = cell['blockers']
            # execute conforming collision

            if 'l' in blockers and lastRect.right <= cell.left and newRect.right > cell.left:
                newRect.right = cell.left
            if 'r' in blockers and lastRect.left >= cell.right and newRect.left < cell.right:
                newRect.left = cell.right
            if 't' in blockers and lastRect.bottom <= cell.top and newRect.bottom > cell.top:
                newRect.bottom = cell.top
            if 'b' in blockers and lastRect.top >= cell.bottom and newRect.top < cell.bottom:
                newRect.top = cell.bottom

        # update position
        self.rect = newRect

class GhostState:
    '''
    A class containing every possible GhostState
    '''
    ENRAGED, CALM = xrange(2)

class GhostColor:
    '''
    A class containing every possible GhostColor
    '''
    PINK, GREEN, BLUE, RED = xrange(4)
    ghostColors = [PINK, GREEN, BLUE, RED]

class Ghost(MovingSprite):
    '''
    A class representing our enemies, ghosts. This class inherits from MovingSprite
    and comes with a movement AI and a collision check to hurt the player on collision.
    
    It also handles the several different images; each color currently has four images, one
    for each direction.
    '''
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

    def __init__(self, game, location, direction, color, *groups):
        '''
        Initialisation...
        '''
        super(Ghost, self).__init__(game, self.images[color][direction], location, direction, 130, *groups)
        self.state = GhostState.ENRAGED
        self.color = color

    def update(self, dt):
        '''
        Calling the update-method of MovingSprite and adding a method
        for player Collision.
        
        @param dt: time passed in seconds since the last call of this method
        @see MovingSprite
        '''
        super(Ghost, self).update(dt)

        # check player Collision
        self.playerCollision()

    def planMovement(self):
        '''
        A template method used in combination with update()
        
        Currently this method is using a simple random movement algorithm, trying
        to stabilize movement (trying to avoid all-too-often direction changes).
        
        In the future there should be used something like an A*-algorithm to try to
        follow PacMe, but only if PacMe is in this Ghost's reach. If he is out of the reach,
        this random movement can be still used then.
        '''
        lastRect = self.rect

        # movement AI
        if len(self.game.tilemap.layers['free'].collide(lastRect, 'free')) == 1:
            for cell in self.game.tilemap.layers['free'].collide(lastRect, 'free'):
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
                    if random.randint(0, 10 / len(possible)) == 0:
                        while not direction in possible:
                            direction = random.randint(0, 3)
                    else:
                        direction = self.currentDirection
                else:
                    while not direction in possible:
                        direction = random.randint(0, 3)

                if direction == Direction.getReverse(self.currentDirection):
                    if random.randint(0, 1) == 0:
                        direction = self.currentDirection
                self.currentDirection = direction

        # update image
        self.image = self.images[self.color][self.currentDirection]


    def respawn(self):
        # TODO
        pass

    def playerCollision(self):
        '''
        A method checking if the Ghost currently is colliding with the PacMe
        and hurting him in case he is not hurt already.
        '''
        # player collision
        if self.rect.colliderect(self.game.player.rect):
            if self.state == GhostState.ENRAGED:
                # ghost is aggressive
                if (self.game.player.state == PlayerState.HURT):
                    # hurt protection after ghost hit
                    pass

                elif (self.game.player.state == PlayerState.NORMAL):
                    # hurt player
                    self.game.sounds[self.game.enemydying].play()
                    self.game.player.lives -= 1
                    self.game.points -= 500
                    self.game.player.state = PlayerState.HURT

            if self.state == GhostState.CALM:
                # ghost is fragile
                self.respawn()
                self.game.points += 100

class PlayerState:
    '''
    A class containing every possible PlayerState
    '''
    NORMAL, HURT = xrange(2)

class Player(MovingSprite):
    '''
    This is US! PacMe is inheriting from MovingSprite. It currently comes with
    keyboard control and a small check on the current status (HURT or NORMAL).
    
    Not much more to see here, for the moment.
    '''
    images = {Direction.NORTH : pygame.image.load('res/images/me_top.png'),
              Direction.EAST : pygame.image.load('res/images/me_right.png'),
              Direction.SOUTH : pygame.image.load('res/images/me_bottom.png'),
              Direction.WEST : pygame.image.load('res/images/me_left.png')}

    def __init__(self, game, location, direction, *groups):
        '''
        Initialisation...
        '''
        super(Player, self).__init__(game, self.images[direction], location, direction, 130, *groups)
        self.lives = 3
        self.state = PlayerState.NORMAL
        self.timeHurt = 0

    def center(self):
        '''
        Returns the center of PacMe's hit-box
        '''
        # currently not used
        x1, y1 = self.rect.topleft
        x2, y2 = self.rect.bottomright
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def update(self, dt):
        '''
        Calling the update-method of MovingSprite and adding a method
        for state checking.
        
        @param dt: time passed in seconds since the last call of this method
        @see MovingSprite
        '''
        super(Player, self).update(dt)
        
        self.stateCheck(dt)
        
    def stateCheck(self, dt):
        '''
        Resets the state to NORMAL if enough time has passed
        '''
        # invincibility check after being hurt
        if (self.state == PlayerState.HURT):
            self.timeHurt += dt
            if (self.timeHurt > 3):
                self.timeHurt = 0
                self.state = PlayerState.NORMAL

    def planMovement(self):
        '''
        Planning movement by reading keyboard input.
        
        Also updating the image for the correct direction
        '''
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

        # update image
        self.image = self.images[self.currentDirection]

    def finalMovement(self, dt):
        '''
        Overwriting MovingSprite's method to always center PacMe on the map.
        '''
        
        super(Player, self).finalMovement(dt)

        # set focus to follow player
        self.game.tilemap.set_focus(self.rect.x, self.rect.y)

class Item(pygame.sprite.Sprite):
    '''
    A class used for static sprites. On collision by PacMe something happens then.
    
    Examples would be corns, powerups, portals, ...
    '''
    def __init__(self, game, image, location, *groups):
        '''
        Initialisation...
        '''
        super(Item, self).__init__(*groups)
        self.game = game
        self.rect = pygame.rect.Rect(location, self.image.get_size())

    def onPlayerCollision(self):
        '''
        Template method to define what happens on collision with the player.
        
        It will be checked in the update method.
        '''
        pass

    def update(self, dt):
        '''
        This method should be called regularly.
        
        @param dt: time passed since last call of this method
        '''
        if self.rect.colliderect(self.game.player.rect):
            self.onPlayerCollision()

class Corn(Item):
    '''
    Basic item, grants points on picking it up and vanishes.
    '''
    image = pygame.image.load('res/images/corn.png')

    def __init__(self, game, location, *groups):
        '''
        Initialisation...
        '''
        super(Corn, self).__init__(game, self.image, location, *groups)

    def onPlayerCollision(self):
        '''
        Template method.
        
        Grants some points and makes this item vanish. Also plays a fancy sound.
        '''
        self.game.points += 5
        self.game.sounds[self.game.pickup].play()
        self.kill()