import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60


screen_width = 800 #864 OG
screen_height = 900 #936 OG


screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF) #ec to Screen
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.SysFont('Time New Roman', 150) #ec to tf


#define colours
white = (255, 255, 100) #ec to yellow

#define game variables
ground_scroll = 0 #ec to gs
scroll_speed = 3 #ec to pace
flying = False
game_over = False #ec to gameOVER
pipe_gap = 180 #ec to pipeGap
pipe_frequency = 1500 #milliseconds                    #ec to pipeFreq
last_pipe = pygame.time.get_ticks() - pipe_frequency   #ec to lastPipe
score = 0
pass_pipe = False  #ec to passPipe



#load images
bg = pygame.image.load('bgtwo.png')
ground_img = pygame.image.load('ground.png') #ec to ground
button_img = pygame.image.load('restart.png') #ec to button1

#draws on screen
def draw_text(text, font, text_col, x, y): #ec to gameText
        img = font.render(text, True, text_col) #ec to imge
        screen.blit(img, (x, y))



class Bird(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		for n in range(1, 4):
			img = pygame.image.load(f'm{n}.png') #imag
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0
		self.clicked = False

	def update(self): #ec to movement

		if flying == True:
			#gravity
			self.vel += 0.6
			if self.vel > 8:
				self.vel = 8
			if self.rect.bottom < 768:
				self.rect.y += int(self.vel)

		if game_over == False:  #ec to gameOver
			#jump
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				self.vel = -10
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

			#handle the animation
			self.counter += 1
			flap_cooldown = 5 #ec to flap_cd

			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
			self.image = self.images[self.index]

			#rotate the bird
			self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
		else:
			self.image = pygame.transform.rotate(self.images[self.index], -90)



def reset_game(): #ec to gameReset
        pipe_group.empty() #ec to pipeGroup
        flappy.rect.x = 100
        flappy.rect.y = int(screen_height / 2)
        score = 0
        return score





class Pipe(pygame.sprite.Sprite): #ec to Pipes
        def __init__(self, x, y, position):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.image.load('pipe.png')
                self.rect = self.image.get_rect()
		#position 1 is from the top, -1 is from the bottom
                if position == 1:
                	self.image = pygame.transform.flip(self.image, False, True)
                	self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
                if position == -1:
                	self.rect.topleft = [x, y + int(pipe_gap / 2)]

        def update(self): #ec autoUpdate
                self.rect.x -= scroll_speed
                if self.rect.right < 0:
                        self.kill()


class Button():
	def __init__(self, x, y, image): #ec image to icon
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):

		action = False

		#get mouse position
		pos = pygame.mouse.get_pos() #ec to loc

		#check if mouse is over the button
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

bird_group = pygame.sprite.Group() #ec to birdGroup
pipe_group = pygame.sprite.Group() #ec to pipeGroup

flappy = Bird(100, int(screen_height / 2)) #ec to soar
bird_group.add(flappy)

#create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img) #ec to restart

run = True
while run:

	clock.tick(fps) #This part can just be replaced with 60 no fps needed

	#draw background
	screen.blit(bg, (0,0))

	bird_group.draw(screen)
	bird_group.update()
	pipe_group.draw(screen)

	#draw the ground
	screen.blit(ground_img, (ground_scroll, 768))

	#check the score
	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
			pass_pipe = True
		if pass_pipe == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1
				pass_pipe = False


	draw_text(str(score), font, white, int(screen_width / 2), 20) #ec to showText

	#look for collision
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
		game_over = True
        
	#check if bird has hit the ground
	if flappy.rect.bottom >= 768:
		game_over = True
		flying = False


	if game_over == False and flying == True:

		#generate new pipes
		time_now = pygame.time.get_ticks() #present
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-100, 100)#ec pipeH
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1) #ec btmPipe
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1) #ec topPipe
			pipe_group.add(btm_pipe)       #ec to pipeGroup 
			pipe_group.add(top_pipe)        
			last_pipe = time_now


		#draw and scroll the ground
		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0

		pipe_group.update()


	#check for game over and reset
	if game_over == True:
		if button.draw() == True:
			game_over = False
			score = reset_game()



	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
			flying = True

	pygame.display.update()

	


pygame.quit()






