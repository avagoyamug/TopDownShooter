import pygame, random, time, sys, math

class Player:
    def __init__(self, x, y,):
        self.x = x
        self.y = y
        self.angle = 0
        #self.speed = 20
        self.texture = pygame.image.load('char_policemen.png')
        self.image = pygame.transform.rotate(self.texture, int(self.angle))

        self.ammo = 6
        self.ammoCapacity = 6
        self.ammoStash = 12


    def rotate(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        relX, relY = mouseX - self.x, mouseY - self.y
        self.angle = (180 / math.pi) * -math.atan2(relY, relX)
        self.image = pygame.transform.rotate(self.texture, int(self.angle) - 90)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def render(self, playSurface):
        imageRect = self.image.get_rect()
        imageRect.center = self.x, self.y
        playSurface.blit(self.image, imageRect)
        # HealthBarDrawer(pos, team[index].health, team[index].maxHealth)

class Enemy:
    def __init__(self, x, y,):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 2
        self.velX = 0
        self.velY = 0

        self.scoreVal = 10
        self.texture = pygame.image.load('char_terrorist.png')
        self.image = pygame.transform.rotate(self.texture, int(self.angle))

    def move(self):
        #print('velX: ', self.velX, '        velY: ', self.velY)
        self.x += self.velX
        self.y += self.velY

    def rotate(self):
        targetX, targetY = player1.x, player1.y
        relX, relY = targetX - self.x, targetY - self.y
        self.angle = (180 / math.pi) * math.atan2(relY, relX) # positive Atan because TOWARDS
        self.image = pygame.transform.rotate(self.texture, int(self.angle)*-1-90)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.velX = self.speed * math.cos(self.angle)
        self.velY = self.speed * math.sin(self.angle)



    def render(self):
        imageRect = self.image.get_rect()
        imageRect.center = self.x, self.y
        playSurface.blit(self.image, imageRect)
        # HealthBarDrawer(pos, team[index].health, team[index].maxHealth)