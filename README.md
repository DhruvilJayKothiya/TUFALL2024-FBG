# TUFALL2024-Soaring Tunnel Vision
import random
import pygame
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()
fps = 60
width = 800
height = 900
Screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
pygame.display.set_caption("Soaring Tunnel Vision")

# Images
bg = pygame.image.load("bgtwo.png")
ground = pygame.image.load("ground.png")
pipe_img = pygame.image.load("pipe.png")
restart_img = pygame.image.load("restart.png")

# Game Variables
gs = 0
pace = 4
pipeGap = 160
score = 0
pipeFreq = 1500  # in milliseconds
lastPipe = pygame.time.get_ticks() - pipeFreq
flying = False
gameOver = False
passPipe = False

# Power-up Variables
invincible = False
gap_boost = False
double_score = False
powerup_timer = 0

# Font & Colors
tf = pygame.font.SysFont("Times New Roman", 120)
yellow = (255, 255, 100)


def gameText(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    Screen.blit(img, (x, y))


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [
            pygame.image.load("m1.png"),
            pygame.image.load("m2.png"),  # Optional other bird images
        ]
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def movement(self):
        global gameOver
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not gameOver:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Animation
            self.counter += 1
            flap_cd = 5
            if self.counter > flap_cd:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

            # Rotate Bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipes(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pipe_img
        self.rect = self.image.get_rect()
        if position == 1:  # Top pipe
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipeGap // 2]
        if position == -1:  # Bottom pipe
            self.rect.topleft = [x, y + pipeGap // 2]

    def autoUpdate(self):
        self.rect.x -= pace
        if self.rect.right < 0:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        pygame.sprite.Sprite.__init__(self)
        self.power_type = power_type
        if power_type == "invincible":
            self.image = pygame.image.load("invincible.png")
        elif power_type == "gap_boost":
            self.image = pygame.image.load("gap_boost.png")
        elif power_type == "double_score":
            self.image = pygame.image.load("double_score.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def autoUpdate(self):
        self.rect.x -= pace
        if self.rect.right < 0:
            self.kill()


def gameReset():
    global score, invincible, gap_boost, double_score, powerup_timer
    pipeGroup.empty()
    powerUpGroup.empty()
    soar.rect.x = 100
    soar.rect.y = height // 2
    score = 0
    invincible = False
    gap_boost = False
    double_score = False
    powerup_timer = 0
    return score


class Button:
    def __init__(self, x, y, icon):
        self.image = icon
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        loc = pygame.mouse.get_pos()
        if self.rect.collidepoint(loc):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        Screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


# Sprites
birdGroup = pygame.sprite.Group()
pipeGroup = pygame.sprite.Group()
powerUpGroup = pygame.sprite.Group()

# Bird object
soar = Bird(100, height // 2)
birdGroup.add(soar)

# Restart button
restart = Button(width // 2 - 50, height // 2 - 100, restart_img)

# Game loop
run = True
while run:
    clock.tick(fps)
    birdGroup.draw(Screen)
    birdGroup.update()
    pipeGroup.draw(Screen)
    powerUpGroup.draw(Screen)

    # Draw ground
    Screen.blit(ground, (gs, 768))

    # Collision detection
    if not invincible and pygame.sprite.groupcollide(birdGroup, pipeGroup, False, False):
        gameOver = True

    if soar.rect.bottom >= 768 or soar.rect.top <= 0:
        gameOver = True
        flying = False

    if not gameOver and flying:
        # Create pipes
        present = pygame.time.get_ticks()
        if present - lastPipe > pipeFreq:
            pipeH = random.randint(-100, 100)
            btmPipe = Pipes(width, height // 2 + pipeH, -1)
            topPipe = Pipes(width, height // 2 + pipeH, 1)
            pipeGroup.add(btmPipe)
            pipeGroup.add(topPipe)
            lastPipe = present

            # Randomly spawn power-ups
            if random.randint(1, 10) == 1:
                powerUp = PowerUp(width, random.randint(100, 700), random.choice(["invincible", "gap_boost", "double_score"]))
                powerUpGroup.add(powerUp)

        gs -= pace
        if abs(gs) > 35:
            gs = 0
        pipeGroup.update()
        powerUpGroup.update()

        # Handle power-up collection
        if pygame.sprite.spritecollide(soar, powerUpGroup, True):
            power_type = random.choice(["invincible", "gap_boost", "double_score"])
            if power_type == "invincible":
                invincible = True
                powerup_timer = pygame.time.get_ticks()
            elif power_type == "gap_boost":
                pipeGap = 200
                powerup_timer = pygame.time.get_ticks()
            elif power_type == "double_score":
                double_score = True
                powerup_timer = pygame.time.get_ticks()

        # Reset power-ups after time
        if pygame.time.get_ticks() - powerup_timer > 5000:
            invincible = False
            gap_boost = False
            double_score = False
            pipeGap = 160

    if gameOver:
        if restart.draw():
            gameOver = False
            score = gameReset()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not gameOver:
            flying = True

    pygame.display.update()

pygame.quit()

