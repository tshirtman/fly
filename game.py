#!/usr/bin/env python
# coding:utf-8
import math
import pygame
from pygame.locals import *

import loaders

scrolling_speed = 10
angle_incr = 0.0001

class Bullet(object):
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 11

    def update(self, deltatime):
        self.x += (math.cos(self.angle)*self.speed - scrolling_speed)*deltatime
        self.y += (math.sin(self.angle)*self.speed) * deltatime

    def display(self, screen):
        screen.blit(
            loaders.image(
                'bullet.png',
                rotate=self.angle*5
            )[0],
            (self.x, 480-self.y)
        )

class Plane(object):
    def __init__(self):
        self.speed = 10
        self.x = 100
        self.y = 100
        self.angle = 0
        self.aim_angle = 0
        self.bullets = set()

    def up(self, deltatime):
        self.angle += angle_incr * deltatime

    def down(self, deltatime):
        self.angle -= angle_incr * deltatime

    def aim_up(self, deltatime):
        self.aim_angle += angle_incr * deltatime

    def aim_down(self, deltatime):
        self.aim_angle -= angle_incr * deltatime

    def fire(self):
        self.bullets.add(Bullet(self.x, self.y, self.angle + self.aim_angle))

    def display(self, screen):
        for bullet in self.bullets:
            bullet.display(screen)

        screen.blit(
            loaders.image(
                'plane.png',
                rotate=self.angle*5
            )[0],
            (self.x, 480-self.y)
        )

    def update(self, deltatime):
        self.angle -= angle_incr/5 * deltatime
        self.angle = max(-500 * angle_incr, min(2000 * angle_incr, self.angle))
        self.x += (math.cos(self.angle)*self.speed - scrolling_speed)*deltatime
        self.y += (math.sin(self.angle) * self.speed) * deltatime
        #print self.x, self.y
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
    screen = pygame.display.set_mode((800,480))
    quit = False
    plane = Plane()
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

        # display
        screen.fill(pygame.Color('white'))
        plane.display(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
