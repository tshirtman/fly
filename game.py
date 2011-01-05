#!/usr/bin/env python
# coding:utf-8
import os
import math
import itertools
import pygame
from pygame.locals import *

import loaders

scrolling_speed = 10
angle_incr = 0.0001

class Level(object):
    def __init__(self, levelname):
        with open(os.path.join("levels",levelname)) as level:
            for line in level.readlines():
                if line.split(':')[0] == '':
                    level.append()

class MovePatern(object):
    def __init__(self, name):
        self.name = name

        if name == 'square':
            self.duration = 8000
            self.vectors=[
                (0, (-.1, 0)),
                (2000, (0, .1)),
                (4000, (.05, 0)),
                (6000, (0, -.1)),
            ]

        elif name == 'down':
            self.duration = 6000
            self.vectors=[
                (0, (-.1, 0)),
                (2000, (-.1, .1)),
                (4000, (0, -.1)),
            ]

    def get_vector(self, t):
        return list(itertools.dropwhile(
            lambda x: x[0] > (t %self.duration),
            reversed(self.vectors)
        ))[0][1]

class Bonus(Entity):
    def __init__(self, category):
        pass

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

class Enemy(Entity):
    def __init__(self, x, y, movepattern, skin):
        Entity.__init__(self, x, y, skin)
        self.movepattern = movepattern
        self.skin = skin
        self.time = 0
        self.life = 10

    def hit(self, points):
        self.life -= points

    def update(self, deltatime):
        self.time += deltatime
        self.x += self.movepattern.get_vector(self.time)[0] * deltatime
        self.y += self.movepattern.get_vector(self.time)[1] * deltatime

    def display(self, screen):
        screen.blit( loaders.image( self.skin)[0], (self.x, self.y))

class Bullet(Entity):
    def __init__(self, x, y, angle):
        Entity.__init__(self, x, y, 'bullet.png')
        self.angle = angle
        self.speed = 11

    def update(self, deltatime):
        self.x += (math.cos(self.angle)*self.speed - scrolling_speed)*deltatime
        self.y += (math.sin(self.angle)*self.speed) * deltatime

    def display(self, screen):
        screen.blit(
            loaders.image(
                self.skin,
                rotate=-self.angle*5
            )[0],
            (self.x, self.y)
        )

class Plane(Entity):
    def __init__(self):
        self.speed = 10
        self.x = 100
        self.y = 100
        self.angle = 0
        self.aim_angle = 0
        self.bullets = set()
        self.skin = 'plane.png'

    def up(self, deltatime):
        self.angle -= angle_incr * deltatime

    def down(self, deltatime):
        self.angle += angle_incr * deltatime

    def aim_up(self, deltatime):
        self.aim_angle -= angle_incr * deltatime

    def aim_down(self, deltatime):
        self.aim_angle += angle_incr * deltatime

    def fire(self):
        self.bullets.add(Bullet(self.x, self.y, self.angle + self.aim_angle))

    def display(self, screen):
        for bullet in self.bullets:
            bullet.display(screen)

        screen.blit(
            loaders.image(
                self.skin,
                rotate=-self.angle*5
            )[0],
            (self.x, self.y)
        )

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
    enemies = set()
    enemies.add(Enemy(500, 300, MovePatern('square'), 'enemy1.png'))
    enemies.add(Enemy(600, 300, MovePatern('square'), 'enemy1.png'))
    enemies.add(Enemy(500, 100, MovePatern('square'), 'enemy1.png'))
    enemies.add(Enemy(600, 100, MovePatern('square'), 'enemy1.png'))
    enemies.add(Enemy(550, 200, MovePatern('square'), 'enemy1.png'))

    enemies.add(Enemy(800, 100, MovePatern('down'), 'enemy1.png'))
    enemies.add(Enemy(950, 200, MovePatern('down'), 'enemy1.png'))

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
        enemies_to_remove = set()
        bullets_to_remove = set()

        for enemy in enemies:
            enemy.update(deltatime)
            for bullet in plane.bullets:
                if bullet.collide(enemy):
                    enemy.hit(1)
                    if enemy.life <= 0:
                        enemies_to_remove.add(enemy)

                    bullets_to_remove.add(bullet)
        plane.bullets.difference_update(bullets_to_remove)
        enemies.difference_update(enemies_to_remove)

        # display
        screen.fill(pygame.Color('white'))
        plane.display(screen)
        for i in enemies:
            i.display(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
