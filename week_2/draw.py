#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import random
import math

SCREEN_DIM = (800, 600)

class Vec2d():
# =======================================================================================
# Функции для работы с векторами
# =======================================================================================
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, v):
        """"возвращает разность двух векторов"""
        return Vec2d(self.x - v.x, self.y - v.y)

    def __add__(self, v):
        """возвращает сумму двух векторов"""
        return Vec2d(self.x + v.x, self.y + v.y)

    @classmethod
    def len(cls, a):
        """возвращает длину вектора"""
        return math.sqrt(a.x * a.x + a.y * a.y)

    def __mul__(self, k):
        """возвращает произведение вектора на число"""
        return Vec2d(self.x * k, self.y * k)

    def int_pair(self):
        """возвращает пару координат, определяющих вектор (координаты точки конца вектора),
        координаты начальной точки вектора совпадают с началом системы координат (0, 0)"""
        return (self.x, self.y)


class Help():
    def __init__(self, gameDisplay):
        self.gameDisplay = gameDisplay

    def draw_help(self, steps):
        """функция отрисовки экрана справки программы"""
        self.gameDisplay.fill((50, 50, 50))
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        data = []
        data.append(["F1", "Show Help"])
        data.append(["R", "Restart"])
        data.append(["P", "Pause/Play"])
        data.append(["Num+", "More points"])
        data.append(["Num-", "Less points"])
        data.append(["", ""])
        data.append([str(steps), "Current points"])

        pygame.draw.lines(self.gameDisplay, (255, 50, 50, 255), True, [
            (0, 0), (800, 0), (800, 600), (0, 600)], 5)
        for i, text in enumerate(data):
            self.gameDisplay.blit(font1.render(
                text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
            self.gameDisplay.blit(font2.render(
                text[1], True, (128, 128, 255)), (200, 100 + 30 * i))


class Polyline():
# =======================================================================================
# Функции отрисовки
# =======================================================================================
    def __init__(self, gameDisplay):
        self.gameDisplay = gameDisplay

    points = []
    speeds = []

    def add_point(self, point, speed):
        self.points.append(point)
        self.speeds.append(speed)

    def draw_points(self, points = points, style="points", width=3, color=(255, 255, 255)):
        """функция отрисовки точек на экране"""
        if style == "line":
            for p_n in range(-1, len(points) - 1):
                pygame.draw.line(self.gameDisplay, color,
                                (int(points[p_n].x), int(points[p_n].y)),
                                (int(points[p_n + 1].x), int(points[p_n + 1].y)), width)

        elif style == "points":
            for p in self.points:
                pygame.draw.circle(self.gameDisplay, color,
                                (int(p.x), int(p.y)), width)

    def set_points(self):
        """функция перерасчета координат опорных точек"""
        for p in range(len(self.points)):
            self.points[p] = self.points[p] + self.speeds[p]

            if self.points[p].x > SCREEN_DIM[0] or self.points[p].x < 0:
                self.speeds[p] = Vec2d(- self.speeds[p].x, self.speeds[p].y)
            if self.points[p].y > SCREEN_DIM[1] or self.points[p].y < 0:
                self.speeds[p] = Vec2d(self.speeds[p].x, -self.speeds[p].y)


class Knot(Polyline):
    # =======================================================================================
    # Функции, отвечающие за расчет сглаживания ломаной
    # =======================================================================================
    def get_point(self, points, alpha, deg=None):
        if deg is None:
            deg = len(points) - 1
        if deg == 0:
            return points[0]
        return points[deg] * alpha + self.get_point(points, alpha, deg - 1) * (1 - alpha)

    def get_points(self, base_points, count):
        alpha = 1 / count
        res = []
        for i in range(count):
            res.append(self.get_point(base_points, i * alpha))
        return res

    def get_knot(self, count):
        if len(self.points) < 3:
            return []
        res = []
        for i in range(-2, len(self.points) - 2):
            ptn = []
            ptn.append((self.points[i] + self.points[i + 1]) * 0.5)
            ptn.append(self.points[i + 1])
            ptn.append((self.points[i + 1] + self.points[i + 2]) * 0.5)

            res.extend(self.get_points(ptn, count))
        return res

# =======================================================================================
# Основная программа
# =======================================================================================
if __name__ == "__main__":
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")

    steps = 35
    working = True
    show_help = False
    pause = True

    hue = 0
    color = pygame.Color(0)

    polyline = Polyline(gameDisplay)
    knot = Knot(gameDisplay)
    help_ = Help(gameDisplay)

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    polyline.points = []
                    polyline.speeds = []
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    steps += 1
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_KP_MINUS:
                    steps -= 1 if steps > 1 else 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                polyline.add_point(Vec2d(x, y), Vec2d(random.random() * 2, random.random() * 2))


        gameDisplay.fill((0, 0, 0))
        hue = (hue + 1) % 360
        color.hsla = (hue, 100, 50, 100)

        polyline.draw_points()
        polyline.draw_points(knot.get_knot(steps), "line", 3, color)

        if not pause:
            polyline.set_points()
        if show_help:
            help_.draw_help(steps)

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)

# a = Vec2d(1, 2)
# b = Vec2d(3, 2)

# print(type(a + b))