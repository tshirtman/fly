#!/usr/bin/env python
# coding:utf-8
from __future__ import division

import os
import math
import itertools
import random
import configobj
import re
import pygame
from pygame.locals import *

import loaders

scrolling_speed = 10
angle_incr = 0.0001

levels = configobj.ConfigObj('levels.cfg')

class Level(object):
    def __init__(self, num):
        self.debug = True
        if "lvl"+str(num) in levels:
            lvl = levels['lvl'+str(num)]
            self.x = 0
            self.background = lvl['background']
            self.foreground_base = lvl['foreground_base']

            self.enemies = set()
            for e in lvl['enemies'].split('\n'):
                e = e.strip()
                if e == '': continue
                a = re.compile(' *, *')
                x, y, pattern, skin = a.split(e)
                self.enemies.add(
                        Enemy(int(x), int(y), MovePatern(pattern), skin)
                        )

    def update(self, deltatime):
        self.x += scrolling_speed/100.0 * deltatime

    def collide(self, entity):
        """
        this is a pseudo pixel perfect collision detection method, to detect
        collisions between the level and any entity

        this is not a true pixel perfect system, because the number of tested
        pixels is only proportional to the size of image, not equal to the
        number of pixels in the image. (but tests show it's enought for our use
        case)

        tested pixel in a example square:
         _________________
        |   .    .    .   |
        |.................|
        |   .    .    .   |
        |.................|
        |   .    .    .   |
        |.................|
        |___.____.____.___|

        4*h + 4*w - 16 pixels tested, for any h and w

        """
        #load the two current displayed images of the level
        img = (
            loaders.image(self.foreground_base+str(int(self.x/1000))+'.png'),
            loaders.image(self.foreground_base+str(int(self.x/1000)+1)+'.png')
            )
        #place entity at its real place on level
        clipped = entity.pos_rect().move(self.x, 0)

        for x in range(0, clipped.width, clipped.width//4):
            for y in range(0, clipped.height, clipped.height//4):
                # manage case where we are on the next tile
                try:
                    if (
                            (entity.x + x < -(self.x % 1000)+1000) and
                            entity.image[0].get_at((x,y)) != (255, 255, 255, 0) and
                            img[0][0].get_at((
                                    int(entity.x + x + (self.x % 1000)),
                                    int(entity.y + y)
                                    )) != (255, 255, 255, 0)):
                        return True
                    elif (
                            entity.image[0].get_at((x,y)) != (255, 255, 255, 0) and
                            img[1][0].get_at((
                                    int(entity.x + x + (self.x % 1000) - 1000),
                                    int(entity.y + y)
                                    )) != (255, 255, 255, 0)):
                        return True

                except IndexError, e:
                    #FIXME: find WHY!
                    pass

        return False

    def display(self, screen):
        """ Display the current two images chunk of the level using current x
        """
        screen.blit(loaders.image(self.background)[0], (0, 0))

        screen.blit(
            loaders.image(
                self.foreground_base+str(int(self.x/1000))+'.png'
            )[0],
            (-(self.x % 1000), 0))

        screen.blit(
            loaders.image(
                self.foreground_base+str(int((self.x)/1000)+1)+'.png'
            )[0],
            (-(self.x % 1000)+1000, 0))

class MovePatern(object):
    """ A move patern define vectors and time associated with them, so there is
        always a vector to follow.
    """
    def __init__(self, name):
        self.name = name.strip()

        if self.name == 'square':
            self.duration = 8000
            self.vectors = [
                (0, (-.1, 0)),
                (2000, (0, .1)),
                (4000, (.05, 0)),
                (6000, (0, -.1)),]

        elif self.name == 'down':
            self.duration = 6000
            self.vectors = [
                (0, (-.1, 0)),
                (2000, (-.1, .1)),
                (4000, (0, -.1)),]
        else:
            raise ValueError('"'+name+'" not a valid pattern name')

    def get_vector(self, t):
        """ Return the vector to use for time t
        """
        return list(itertools.dropwhile(
            lambda x: x[0] > (t %self.duration),
            reversed(self.vectors)))[0][1]

class Entity(object):
    """ Base object to abstract various entities in the game
    """
    def __init__(self, x, y, skin):
        self.x = x
        self.y = y
        self.angle = 0
        self.skin = skin

    def pos_rect(self):
        """ returns the rect of the current image, at the current position
        """
        return pygame.Rect((self.x, self.y), self.image[1][2:])

    def collide(self, entity):
        """ pixel perfect collision between two entities
        """
        # reduce tested zone to overlap of the two rects
        clipped = pygame.Rect((self.x, self.y), self.image[1][2:]).clip(
                pygame.Rect((entity.x, entity.y), entity.image[1][2:]))

        for x in range(clipped.width):
            for y in range(clipped.height):
                # return true if pixels in both images at x,y in the clipping
                # rect have a non transparent color
                if (
                    self.image[0].get_at((
                        clipped.x - int(self.x) + x,
                        clipped.y - int(self.y) + y
                        )) != (255, 255, 255, 0) and
                    entity.image[0].get_at((
                        clipped.x - int(entity.x) + x,
                        clipped.y - int(entity.y) + y
                        )) != (255, 255, 255, 0)
                   ):
                    return True
        return False

    def hit(self, points):
        """ Decrease life of points
        """
        self.life -= points

    @property
    def image(self):
        """ Return the image currently displayed by the engine for the entity.
        """
        return loaders.image(
                self.skin,
                rotate=-self.angle*5
                )

    def display(self, screen):
        """ display the current image, at the current coordinates.
        """
        screen.blit(
            self.image[0],
            (self.x, self.y)
        )

class Bonus(Entity):
    """ A simple entity with a name, to act on the player when he catch them
    """
    def __init__(self, x, y, category):
        self.x = x
        self.y = y
        self.angle = 0
        self.category = category
        self.skin = 'bonus_'+category+'.png'
        self.speed = scrolling_speed

    def update(self, deltatime):
        """ update position and angle """
        self.angle += angle_incr * deltatime
        self.speed -= (scrolling_speed/50000.)*deltatime
        self.x += (self.speed - scrolling_speed)*deltatime

class particle(Entity):
    def __init__(self, time, x, y, angle, speed):
        self.time = time
        self.x = x
        self.y = y
        self.angle = angle
        self.d_angle = angle
        self.speed = speed
        self.time = 0
        self.skin = 'particle1.png'

    def update(self, deltatime):
        self.time += deltatime
        self.x += math.cos(self.d_angle) * self.speed * deltatime
        self.y += math.sin(self.d_angle) * self.speed * deltatime
        self.x -= scrolling_speed/100. * deltatime
        # FIXME: lots of hardcoded values around here!
        if self.time > 200: self.skin = 'particle2.png'
        if self.time > 400: self.skin = 'particle.png'
        #self.speed -= deltatime * self.speed

    def display(self, screen):
        screen.blit(
                loaders.image(
                    self.skin,
                    alpha=(1500 - self.time)/1500.
                    )[0],
                (self.x, self.y),
                )


class Explosion(object):
    def __init__(self, x, y, size=100):
        self.x = x
        self.y = y
        self.time = size
        self.size = size
        self.particles = set()

    def update(self, deltatime):
        self.time -= deltatime
        if self.time > 0:
            for i in range(5):
                self.particles.add(
                    particle(
                        self.time,
                        self.x,
                        self.y,
                        (random.randint(0, 100)/100)*2*math.pi,
                        0.01)
                    )

        to_remove = set()
        for p in self.particles:
            p.update(deltatime)
            if p.time > 1500:
                to_remove.add(p)
        self.particles.difference_update(to_remove)

    @property
    def dead(self):
        return self.time < 0 and len(self.particles) == 0

    def display(self, screen):
        for p in self.particles:
            p.display(screen)

class Enemy(Entity):
    """ An entity at a position, moving with a pattern
    """
    def __init__(self, x, y, movepattern, skin):
        Entity.__init__(self, x, y, skin)
        self.movepattern = movepattern
        self.skin = skin
        self.time = 0
        self.life = 10
        self.angle = 0

    def update(self, deltatime):
        self.time += deltatime
        self.x += self.movepattern.get_vector(self.time)[0] * deltatime
        self.y += self.movepattern.get_vector(self.time)[1] * deltatime

class Bullet(Entity):
    """ An entity to attack others.
    """
    def __init__(self, x, y, angle):
        Entity.__init__(self, x, y, 'bullet.png')
        self.angle = angle
        self.speed = scrolling_speed * 1.1

    def update(self, deltatime):
        self.x += (math.cos(self.angle)*self.speed - scrolling_speed)*deltatime
        self.y += (math.sin(self.angle)*self.speed) * deltatime


class Plane(Entity):
    """ The entity controlled by the player.
    """
    def __init__(self):
        self.speed = 10
        self.x = 100
        self.y = 100
        self.angle = 0
        self.aim_angle = 0
        self.bullets = set()
        self.skin = 'plane.png'
        self.scnd_weapon = 'bomb', 1
        self.life = 100
        self.bombs = 0
        self.armor = 0

    def up(self, deltatime):
        """ direct plane up in the sky.
        """
        self.angle -= angle_incr * deltatime

    def down(self, deltatime):
        """ push plane down to the flor.
        """
        self.angle += angle_incr * deltatime

    def aim_up(self, deltatime):
        """ direct gun higher.
        """
        self.aim_angle -= angle_incr * deltatime

    def aim_down(self, deltatime):
        """ direct gun lower.
        """
        self.aim_angle += angle_incr * deltatime

    def fire(self):
        """ fire the gun.
        """
        self.bullets.add(Bullet(self.x, self.y, self.angle + self.aim_angle))

    def bomb(self):
        pass
        #self.

    def scnd_fire(self):
        """ fire the second gun
        """
        if self.scnd_weapon[0] == 'bomb':
            self.bomb()

    def display(self, screen):
        for bullet in self.bullets:
            bullet.display(screen)
        Entity.display(self, screen)

    def update(self, deltatime, level):
        """ Update physics of the plane and its bullets.
        """
        self.angle += angle_incr/5 * deltatime
        self.angle = max(-500 * angle_incr, min(2000 * angle_incr, self.angle))
        self.x += (math.cos(self.angle)*self.speed - scrolling_speed)*deltatime
        self.y += (math.sin(self.angle) * self.speed) * deltatime
        self.x = max(0, min(600, self.x))
        self.y = max(0, min(480, self.y))


    def get_bonus(self, bonus):
        """ Handle the catching of a bonus.
        """
        if bonus.category == 'life':
            self.life += 50
        elif bonus.category == 'bomb':
            self.bombs += 1
        elif bonus.category == 'armor':
            self.armor += 100

def main():
    pygame.init()
    gamefont = pygame.font.Font(pygame.font.match_font('tlwgtypist', bold=True), 18)

    screen = pygame.display.set_mode((800, 480))
    quit = False
    plane = Plane()
    level = Level(1)
    bonuses = set()
    bonustypes = (
        'bomb',
        'life',
        'armor',
    )

    explosions = set()

    clock = pygame.time.Clock()
    while not quit:
        deltatime = clock.tick()
        # get controls
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            quit = True

        if keys[pygame.K_UP]:
            plane.up(deltatime)

        if keys[pygame.K_DOWN]:
            plane.down(deltatime)

        if keys[pygame.K_q]:
            plane.aim_up(deltatime)

        if keys[pygame.K_d]:
            plane.aim_down(deltatime)

        if keys[pygame.K_RIGHT]:
            plane.speed = 1.05 * scrolling_speed
        elif keys[pygame.K_LEFT]:
            plane.speed = 0.95 * scrolling_speed
        else:
            plane.speed = 10

        if keys[pygame.K_SPACE]:
            plane.fire()

        # update
        plane.update(deltatime, level)
        level.update(deltatime)

        if level.collide(plane):
            plane.life -= 1
            plane.y -= 10
            if plane.life < 0:
                level = Level(1)
                plane = Plane()
                bonuses = set()

        to_remove = set()
        for bonus in bonuses:
            bonus.update(deltatime)
            if bonus.x < 0:
                to_remove.add(bonus)
            if plane.collide(bonus):
                plane.get_bonus(bonus)
                to_remove.add(bonus)

        for explosion in explosions:
            explosion.update(deltatime)

        bonuses.difference_update(to_remove)

        bullets_to_remove = set()
        for bullet in plane.bullets:
            bullet.update(deltatime)
            if bullet.x > 1000:
                to_remove.add(bullet)
            elif level.collide(bullet):
                to_remove.add(bullet)
                explosions.add(Explosion(bullet.x, bullet.y, 50))

        plane.bullets.difference_update(to_remove)

        bullets_to_remove = set()
        enemies_to_remove = set()
        for enemy in level.enemies:
            enemy.update(deltatime)
            if enemy.collide(plane):
                plane.hit(20)
                explosions.add(
                    Explosion(
                            enemy.x,
                            enemy.y,
                            500,
                        )
                    )
                enemies_to_remove.add(enemy)
                continue
            for bullet in plane.bullets:
                if bullet.collide(enemy):
                    enemy.hit(1)
                    if enemy.life <= 0:
                        explosions.add(
                            Explosion(
                                    enemy.x,
                                    enemy.y,
                                    500,
                                )
                            )

                        enemies_to_remove.add(enemy)
                        if random.randint(0,6) == 6:
                            bonuses.add(
                                Bonus(
                                    enemy.x,
                                    enemy.y,
                                    random.choice(bonustypes)
                                    )
                                )

                    bullets_to_remove.add(bullet)
        plane.bullets.difference_update(bullets_to_remove)
        level.enemies.difference_update(enemies_to_remove)
        to_remove = set()

        for e in explosions:
            if e.dead:
                to_remove.add(e)
        explosions.difference_update(to_remove)

        # update display
        level.display(screen)
        plane.display(screen)
        for i in bonuses:
            i.display(screen)
        for i in level.enemies:
            i.display(screen)
        for i in explosions:
            i.display(screen)

        screen.blit(
                gamefont.render(
                    str(plane.life),
                    True,
                    pygame.Color("red"),
                    ),
                (0,0)
            )

        screen.blit(
            gamefont.render(
                str(plane.armor),
                True,
                pygame.Color("red"),
                ),
            (0,20)
            )

        screen.blit(
            gamefont.render(
                str(plane.bombs),
                True,
                pygame.Color("red"),
                ),
            (0,40)
            )

        pygame.display.flip()

if __name__ == '__main__':
    main()
