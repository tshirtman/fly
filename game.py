#!/usr/bin/env python
# coding:utf-8
import os
import math
import itertools
import random
import pygame
from pygame.locals import *

import loaders

scrolling_speed = 10
angle_incr = 0.0001

class Level(object):
    def __init__(self, num):
        self.debug = True
        self.x = 0
        self.background = 'lvl1_background.png'
        self.foreground_base = 'lvl1_foreground_'

        self.enemies = set()
        self.enemies.add(Enemy(500, 300, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(600, 300, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(500, 100, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(600, 100, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(550, 200, MovePatern('square'), 'enemy1.png'))

        self.enemies.add(Enemy(800, 100, MovePatern('down'), 'enemy1.png'))
        self.enemies.add(Enemy(950, 200, MovePatern('down'), 'enemy1.png'))

        self.enemies.add(Enemy(1500, 300, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(1600, 300, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(1500, 100, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(1600, 100, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(1550, 200, MovePatern('square'), 'enemy1.png'))

        self.enemies.add(Enemy(1800, 100, MovePatern('down'), 'enemy1.png'))
        self.enemies.add(Enemy(1950, 200, MovePatern('down'), 'enemy1.png'))
        self.enemies.add(Enemy(1500, 300, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(2600, 300, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(2500, 100, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(2600, 100, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(2550, 200, MovePatern('square'), 'enemy1.png'))

        self.enemies.add(Enemy(2800, 100, MovePatern('down'), 'enemy1.png'))
        self.enemies.add(Enemy(2950, 200, MovePatern('down'), 'enemy1.png'))
        self.enemies.add(Enemy(2500, 300, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(2600, 300, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(2500, 100, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(2600, 100, MovePatern('square'), 'enemy1.png'))
        self.enemies.add(Enemy(2550, 200, MovePatern('square'), 'enemy1.png'))

        self.enemies.add(Enemy(2800, 100, MovePatern('down'), 'enemy1.png'))
        self.enemies.add(Enemy(2950, 200, MovePatern('down'), 'enemy1.png'))

    def update(self, deltatime):
        self.x += scrolling_speed/100.0 * deltatime

    def collide(self, plane):
        img = (
            loaders.image(self.foreground_base+str(int(self.x/1000))+'.png'),
            loaders.image(self.foreground_base+str(int(self.x/1000)+1)+'.png')
            )

        clipped = plane.pos_rect().move(self.x, 0)

        for x in range(0, clipped.width, 16):
            for y in range(0, clipped.height, 8):
                # manage case where we are on the next tile
                #print int(plane.x + x + (self.x % 1000)), int(plane.y + y)
                if (plane.x +x < -(self.x % 1000)+1000):
                    if (
                        plane.image()[0].get_at((x,y)) != (255, 255, 255, 0) and
                        img[0][0].get_at((
                            int(plane.x + x + (self.x % 1000)),
                            int(plane.y + y)
                            )) != (255, 255, 255, 0)
                       ):
                        return True
                else:
                    if (
                        plane.image()[0].get_at((x,y)) != (255, 255, 255, 0) and
                        img[1][0].get_at((
                            int(plane.x + x + (self.x % 1000) - 1000),
                            int(plane.y + y)
                            )) != (255, 255, 255, 0)
                       ):
                        return True
        return False

    def display(self, screen):
        screen.blit(loaders.image(self.background)[0], (0, 0))
        screen.blit(
            loaders.image(
                self.foreground_base+str(int(self.x/1000))+'.png'
            )[0],
            (-(self.x % 1000), 0)
        )
        screen.blit(
            loaders.image(
                self.foreground_base+str(int((self.x)/1000)+1)+'.png'
            )[0],
            (-(self.x % 1000)+1000, 0)
        )

class MovePatern(object):
    def __init__(self, name):
        self.name = name

        if name == 'square':
            self.duration = 8000
            self.vectors = [
                (0, (-.1, 0)),
                (2000, (0, .1)),
                (4000, (.05, 0)),
                (6000, (0, -.1)),
            ]

        elif name == 'down':
            self.duration = 6000
            self.vectors = [
                (0, (-.1, 0)),
                (2000, (-.1, .1)),
                (4000, (0, -.1)),
            ]

    def get_vector(self, t):
        return list(itertools.dropwhile(
            lambda x: x[0] > (t %self.duration),
            reversed(self.vectors)
        ))[0][1]

class Entity(object):
    def __init__(self, x, y, skin):
        self.x = x
        self.y = y
        self.skin = skin

    def collide(self, entity):
        return pygame.Rect(
            (self.x, self.y), loaders.image(self.skin)[1][2:]
            ).colliderect(
            pygame.Rect(
                (entity.x, entity.y), loaders.image(entity.skin)[1][2:]
            )
        )

    def image(self):
        return loaders.image(
                self.skin,
                rotate=-self.angle*5
                )

    def display(self, screen):
        screen.blit(
            self.image()[0],
            (self.x, self.y)
        )

class Bonus(Entity):
    def __init__(self, x, y, category):
        self.x = x
        self.y = y
        self.angle = 0
        self.category = category
        self.skin = 'bonus_'+category+'.png'
        self.speed = scrolling_speed

    def update(self, deltatime):
        self.angle += angle_incr * deltatime
        self.speed -= (scrolling_speed/50000.)*deltatime
        self.x += (self.speed - scrolling_speed)*deltatime

class Enemy(Entity):
    def __init__(self, x, y, movepattern, skin):
        Entity.__init__(self, x, y, skin)
        self.movepattern = movepattern
        self.skin = skin
        self.time = 0
        self.life = 10
        self.angle = 0

    def hit(self, points):
        self.life -= points

    def update(self, deltatime):
        self.time += deltatime
        self.x += self.movepattern.get_vector(self.time)[0] * deltatime
        self.y += self.movepattern.get_vector(self.time)[1] * deltatime

class Bullet(Entity):
    def __init__(self, x, y, angle):
        Entity.__init__(self, x, y, 'bullet.png')
        self.angle = angle
        self.speed = 11

    def update(self, deltatime):
        self.x += (math.cos(self.angle)*self.speed - scrolling_speed)*deltatime
        self.y += (math.sin(self.angle)*self.speed) * deltatime


class Plane(Entity):
    def __init__(self):
        self.speed = 10
        self.x = 100
        self.y = 100
        self.angle = 0
        self.aim_angle = 0
        self.bullets = set()
        self.skin = 'plane.png'
        self.scnd_weapon = 'bomb', 1

    def up(self, deltatime):
        self.angle -= angle_incr * deltatime

    def pos_rect(self):
        """ returns the rect of the current image, at the current position """
        return pygame.Rect((self.x, self.y), loaders.image(self.skin)[1][2:])

    def down(self, deltatime):
        self.angle += angle_incr * deltatime

    def aim_up(self, deltatime):
        self.aim_angle -= angle_incr * deltatime

    def aim_down(self, deltatime):
        self.aim_angle += angle_incr * deltatime

    def fire(self):
        self.bullets.add(Bullet(self.x, self.y, self.angle + self.aim_angle))

    def scnd_fire(self):
        if self.scnd_weapon[0] == 'bomb':
            self.bomb()

    def display(self, screen):
        for bullet in self.bullets:
            bullet.display(screen)
        Entity.display(self, screen)

    def update(self, deltatime):
        self.angle += angle_incr/5 * deltatime
        self.angle = max(-500 * angle_incr, min(2000 * angle_incr, self.angle))
        self.x += (math.cos(self.angle)*self.speed - scrolling_speed)*deltatime
        self.y += (math.sin(self.angle) * self.speed) * deltatime
        self.x = max(0, min(800, self.x))
        self.y = max(0, min(480, self.y))

        to_remove = set()
        for bullet in self.bullets:
            bullet.update(deltatime)
            if bullet.x > 1000:
                to_remove.add(bullet)

        self.bullets.difference_update(to_remove)

def main():
    pygame.init()
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
            plane.speed = 10.5
        elif keys[pygame.K_LEFT]:
            plane.speed = 9.5
        else:
            plane.speed = 10

        if keys[pygame.K_SPACE]:
            plane.fire()

        # update
        plane.update(deltatime)
        level.update(deltatime)
        enemies_to_remove = set()
        bullets_to_remove = set()

        if level.collide(plane):
            level = Level(1)
            plane = Plane()

        to_remove = set()
        for bonus in bonuses:
            bonus.update(deltatime)
            if bonus.x < 0:
                to_remove.add(bonus)
        bonuses.difference_update(to_remove)

        for enemy in level.enemies:
            enemy.update(deltatime)
            for bullet in plane.bullets:
                if bullet.collide(enemy):
                    enemy.hit(1)
                    if enemy.life <= 0:
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

        # display
        #screen.fill(pygame.Color('white'))
        level.display(screen)
        plane.display(screen)
        for i in bonuses:
            i.display(screen)
        for i in level.enemies:
            i.display(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
