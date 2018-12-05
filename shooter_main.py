'''
##########################################################################################################
Main Ideas and ToDo:
- add animation system (general anim func)
- new weapons, like flamethrower and rocketlauncher
- new perk-drops (shield,speedboost, infiniteammo, etc...)
- new monsters
- encrypt highscore file

Maintanance:
- ammoWarning system is quite hacked, optimize!
- make absolute values var's
- clean up and scale UI

##########################################################################################################
'''



import pygame, random, time, sys, math

# check for initializing errors
check_errors = pygame.init()
if check_errors[1] > 0:
    print("(!) Had {0} initializing errors, exiting...".format(check_errors[1]))
    sys.exit(-1)
else:
    print("(+) PyGame successfully initialized!")

'''
CheatMODE:
(give weapons with F1 to F3)
'''
cheatMode = True


# Play Surface
screenWidth = 600
screenHeight = 600
playSurface = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('SHOOTER')
pygame.event.set_grab(True) # traps the mouse in window
pygame.mouse.set_cursor(*pygame.cursors.broken_x) # uses predefined pygame cursor tuple

# Colors
red = pygame.Color(255,0,0)
orange = pygame.Color(255,128,0)
yellow = pygame.Color(255,255,0)
blue = pygame.Color(0,0,255)
green = pygame.Color(0,255,0)
white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)
grey = pygame.Color(128,128,128)
brown = pygame.Color(128,120,105)
darkBlue = pygame.Color(70,80,97)
alphaGrey = pygame.Color(128,128,128,128)
alphaBlack = pygame.Color(0,0,0,128)
alphaRed = pygame.Color(255,0,0,128)

# FPS controller
fpsController = pygame.time.Clock()
gameTime = 0  # time in frames

# Important Game Vars
gameClock = (0,0)

playerPos = [230, 230]
my_shots = []
score = 0
pause = False

enemyList = []
enemySpawn = True
enemyCount = 3
spawnFrequency = 20

dropList = []

gameOverBool = False


# Player Class
class Player:
    def __init__(self, x, y,):
        self.x = x
        self.y = y
        self.angle = 0
        self.moveSpeed = 5
        self.texture = pygame.image.load('char_policemen.png')
        self.cooldownCounter = 0
        self.dropWeapon()
        self.shotSize = 5

        self.ammoWarning = 0

    def move(self, keys):
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if not self.x > screenWidth -10:
                self.x += self.moveSpeed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if not self.x < 10:
                self.x -= self.moveSpeed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if not self.y < 10:
                self.y -= self.moveSpeed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if not self.y > screenHeight -10:
                self.y += self.moveSpeed

    def rotate(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        relX, relY = mouseX - self.x, mouseY - self.y
        self.radians = math.atan2(relY, relX)  # positive Atan because TOWARDS
        self.angle = (180 / math.pi) * -self.radians
        self.image = pygame.transform.rotate(self.texture, int(self.angle) - 90)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def render(self):
        imageRect = self.image.get_rect()
        imageRect.center = self.x, self.y
        playSurface.blit(self.image, imageRect)
        # HealthBarDrawer(pos, team[index].health, team[index].maxHealth)

    def dropWeapon(self):
        self.weaponSprite = pygame.image.load('wpn_revolver.png')
        self.weapon = 'revolver'
        self.cooldown = 10  # (frames)
        self.reloadTime = 20
        self.weaponPenetration = 1
        self.ammo = 6
        self.ammoCapacity = 6
        self.ammoStash = 999
        self.spread = 0 # in radians
        self.autoFire = False
        self.damage = 1
        self.shotSize = 5

    def shoot(self, bullets=1):
        if player1.cooldownCounter == 0:
            mousePos = pygame.mouse.get_pos()
            originPos = self.x, self.y
            sourceX = originPos[0]
            sourceY = originPos[1]
            targetX = mousePos[0]
            targetY = mousePos[1]
            offset = (targetY - sourceY, targetX - sourceX)
            radians = math.atan2(*offset)
            for i in range(bullets):
                angle = (radians - math.pi) + (random.randint(-self.spread, self.spread)) * 0.1
                my_shots.append(Projectile(sourceX, sourceY, angle, self.weaponPenetration, self.shotSize))
            self.ammo -= 1
            if self.ammo <= 0 and self.ammoStash <= 0 and self.weapon != 'revolver':
                self.dropWeapon()
            player1.cooldownCounter = player1.cooldown
            FX_List.append(fx_muzzleflash(self.x, self.y, self.radians))

    def reload(self):
        # fill ammo to max, if stash higher than capacity minus already loaded bullets
        if self.ammo == self.ammoCapacity:
            return
        elif self.ammoStash >= self.ammoCapacity - self.ammo:
            self.ammoStash -= self.ammoCapacity - self.ammo
            self.ammo = self.ammoCapacity
            self.cooldownCounter = self.reloadTime
            FX_List.append(fx_reloadBar())
        elif self.ammoStash <= 0:
            return
        else:  # so if stash wouldnt suffice to fill up magazine, but is larger then 0:
            # ammo is equal to stash
            self.ammo += self.ammoStash
            self.ammoStash = 0
            self.cooldownCounter = self.reloadTime
            FX_List.append(fx_reloadBar())

# instanciate player
player1 = Player(playerPos[0], playerPos[1])

class Enemy:
    def __init__(self, x, y):
        self.scoreVal = 10
        self.dropchance = 20
        self.hitboxSize = 10
        self.health = 1
        self.x = x
        self.y = y
        self.angle = 0
        self.radians = 0
        self.speed = 2
        self.velX = 0
        self.velY = 0
        self.texture = pygame.image.load('char_zombie.png')
        self.image = pygame.transform.rotate(self.texture, int(self.angle))

    def rotate(self):
        targetX, targetY = player1.x, player1.y
        relX, relY = targetX - self.x, targetY - self.y
        self.radians = math.atan2(relY, relX) # positive Atan because TOWARDS
        self.angle = (180 / math.pi) * self.radians
        self.image = pygame.transform.rotate(self.texture, int(self.angle)*-1)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.velX = self.speed * math.cos(self.radians)
        self.velY = self.speed * math.sin(self.radians)

    def move(self):
        self.x += self.velX
        self.y += self.velY


    def render(self):
        imageRect = self.image.get_rect()
        imageRect.center = self.x, self.y
        playSurface.blit(self.image, imageRect)
        # HealthBarDrawer(pos, team[index].health, team[index].maxHealth)

class LargeEnemy(Enemy):
    def __init__(self, x, y):
        self.hitboxSize = 15
        self.health = 2
        self.dropchance = 50
        self.scoreVal = 30
        self.x = x
        self.y = y
        self.angle = 0
        self.radians = 0
        self.speed = 1
        self.velX = 0
        self.velY = 0
        self.texture = pygame.image.load('char_largeZombie.png')
        self.image = pygame.transform.rotate(self.texture, int(self.angle))

class Drop:
    lifetime = 200
    alpha = 255

    def __init__(self, x, y,):
        self.x = x
        self.y = y
        self.texture = pygame.image.load('default.png')
        self.image = self.texture

    def render(self):
        imageRect = self.image.get_rect()
        imageRect.center = self.x, self.y
        blit_alpha(playSurface, self.image, imageRect, 100 if self.alpha < 100 else 255)

class Ammo(Drop):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ammo = 6
        self.alphaStep = self.alpha / self.lifetime
        self.texture = pygame.image.load('wpn_ammo.png')
        self.image = self.texture

    def pickup(self):
        print('Ammo picked up!')
        player1.ammoStash += self.ammo

class Pistol(Drop):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alphaStep = self.alpha / self.lifetime
        self.texture = pygame.image.load('wpn_pistol.png')
        self.image = self.texture

    def pickup(self):
        print('Pistol picked up!')
        if player1.weapon == 'pistol':
            player1.ammoStash += 12
            return
        player1.weapon = 'pistol'
        player1.ammo = 12
        player1.ammoCapacity = 12
        player1.ammoStash = 0
        player1.spread = 0
        player1.weaponPenetration = 3
        player1.weaponSprite = self.texture
        player1.cooldown = 1
        player1.reloadTime = 20
        player1.shotSize = 6
        player1.damage = 2

class Uzi(Drop):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alphaStep = self.alpha / self.lifetime
        self.texture = pygame.image.load('wpn_uzi.png')
        self.image = self.texture

    def pickup(self):
        print('Uzi picked up!')
        if player1.weapon == 'uzi':
            player1.ammoStash += 30
            return
        player1.weapon = 'uzi'
        player1.ammo = 30
        player1.ammoCapacity = 30
        player1.ammoStash = 0
        player1.spread = 2
        player1.weaponPenetration = 2
        player1.weaponSprite = self.texture
        player1.cooldown = 3
        player1.reloadTime = 20
        player1.shotSize = 5

class Shotgun(Drop):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alphaStep = self.alpha / self.lifetime
        self.texture = pygame.image.load('wpn_shotgun.png')
        self.image = self.texture

    def pickup(self):
        print('Shotgun picked up!')
        if player1.weapon == 'shotgun':
            player1.ammoStash += 10
            return
        player1.weapon = 'shotgun'
        player1.ammo = 5
        player1.ammoCapacity = 5
        player1.ammoStash = 5
        player1.spread = 3
        player1.weaponPenetration = 1
        player1.weaponSprite = self.texture
        player1.cooldown = 20
        player1.reloadTime = 40
        player1.shotSize = 3


# Projectile Class
class Projectile:
    def __init__(self, x, y, angle, penetration=2, size=5):
        self.x = x
        self.y = y
        self.size = size
        self.colour = yellow
        self.angle = angle
        self.speed = 20
        self.penetration = penetration
        self.velX = self.speed * math.cos(self.angle)
        self.velY = self.speed * math.sin(self.angle)

    def render(self):
        pygame.draw.rect(playSurface, self.colour, pygame.Rect(self.x, self.y, self.size, self.size))

    def update(self):
        self.x -= self.velX
        self.y -= self.velY

class FX:
    lifetime = 10
    angle = 0
    alpha = 255


    def render(self):
        imageRect = self.image.get_rect()
        imageRect.center = self.x, self.y
        blit_alpha(playSurface, self.image, imageRect, self.alpha)

class fx_muzzleflash(FX):
    def __init__(self, x, y, radians):
        self.radians = radians
        self.offset = 40
        self.angle = (180 / math.pi) * self.radians
        self.x = x + (self.offset * math.cos(self.radians))
        self.y = y + (self.offset * math.sin(self.radians))
        #self.angle = angle


        self.lifetime = 5
        self.alphaStep = self.alpha / self.lifetime
        self.texture = pygame.image.load('fx_muzzleflash.png')
        self.texture.set_alpha(100)
        self.image = pygame.transform.rotate(self.texture, int(self.angle)*-1)

class fx_bloodsplatter(FX):
    def __init__(self, x, y, radians):
        self.radians = radians
        self.offset = -30
        self.angle = (180 / math.pi) * self.radians
        self.x = x + (self.offset * math.cos(self.radians))
        self.y = y + (self.offset * math.sin(self.radians))
        #self.angle = angle


        self.lifetime = 5
        self.alphaStep = self.alpha / self.lifetime
        self.texture = pygame.image.load('fx_blood.png')
        self.texture.set_alpha(100)
        self.image = pygame.transform.rotate(self.texture, int(self.angle)*-1)

class fx_deadEnemy(FX):
    def __init__(self, x, y, radians):
        self.radians = radians
        self.offset = -20
        self.angle = (180 / math.pi) * self.radians
        self.x = x + (self.offset * math.cos(self.radians))
        self.y = y + (self.offset * math.sin(self.radians))
        #self.angle = angle


        self.lifetime = 80
        self.alphaStep = self.alpha / self.lifetime
        self.texture = pygame.image.load('fx_body.png')
        self.texture.set_alpha(100)
        self.image = pygame.transform.rotate(self.texture, int(self.angle)*-1)

class fx_reloadBar(FX):
    def __init__(self):
        self.alpha = 220  # hack using alpha as percent for this particular effect
        self.lifetime = player1.reloadTime
        self.alphaStep = self.alpha / self.lifetime
        self.coords =   ([0,0],
                        [0,0],
                        [0,0],
                        [0,0])

    def render(self):
        pygame.draw.polygon(playSurface, white, self.coords)
        self.coords =   ([110, screenHeight - 95],
                        [110+self.alpha, screenHeight - 95],
                        [110+self.alpha, screenHeight - 75],
                        [110, screenHeight - 75])

FX_List = []

# Direction Vars
direction = ''

def renderBG():
    '''
    bg = pygame.image.load('dirt.jpg')
    bg = pygame.transform.scale(bg, (screenWidth, screenHeight))
    bgRect = bg.get_rect()
    bgRect.center = screenWidth / 2, screenHeight / 2
    playSurface.blit(bg, bgRect)
    playSurface.fill(alphaGrey,None,8)
    '''
    playSurface.fill(darkBlue)


def paused():
    global pause
    print('## PAUSE ##')
    pygame.event.set_grab(False)

    pauseText = pygame.font.SysFont("monaco", 115)
    pauseSurf = pauseText.render("||", True, red)
    pauseRect = pauseSurf.get_rect()
    pauseRect.center = (screenHeight / 2, screenWidth / 2)
    playSurface.blit(pauseSurf, pauseRect)
    pygame.display.flip()

    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.event.set_grab(False)
                    pause = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# Game Over Func
def gameOver():
    global gameOverBool
    gameOverBool = True
    nameInput = ''

    GOFont = pygame.font.SysFont('monaco', 72)
    GOsurf = GOFont.render('Game over!', True, red)
    GOrect = GOsurf.get_rect()
    GOrect.midtop = (screenWidth/2, screenHeight/2)

    while True: # postgameLoop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Quit logic
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if len(nameInput) <= 20:
                    if event.key == pygame.K_BACKSPACE:
                        print('K_BACKSPACE')
                        nameInput = nameInput[:-1]
                    elif event.key == pygame.K_RETURN:  # confirms input, saves to file and quits
                        print('K_RETURN')
                        print('nameInput: ', nameInput)

                        with open('highScores.txt', 'r') as highScores: # reading highscore file into lists
                            highScoresList = [line.strip() for line in highScores]
                            highScoresListOfLists = [i.split(':') for i in highScoresList]
                            for i in highScoresListOfLists:
                                if int(i[0]) <= score:
                                    highScoresListOfLists.insert(highScoresListOfLists.index(i), [str(score), nameInput])
                                    break
                            else: highScoresListOfLists.append([str(score), nameInput])
                            highScoresListOfLists = highScoresListOfLists[:10]
                            print ('highScoresListOfLists (NEW): ', highScoresListOfLists)
                        highScores.close
                        highScores = open('highScores.txt', 'w')
                        for i in highScoresListOfLists:
                            highScores.write('{}:{}'.format(i[0], i[1]) + '\n')
                        highScores.close

                        # show highScores Loop (until quit)
                        playSurface.fill(darkBlue)
                        counter = screenHeight/12
                        place = 1
                        alreadySet = False
                        for entry in highScoresListOfLists:
                            highScoreFont = pygame.font.SysFont('monaco', 40)
                            if entry[1] == nameInput and entry[0] == str(score) and not alreadySet: # highlights current playthrough score
                                highScoreSurf = highScoreFont.render(str(place) + '.    ' + 'pts, '.join(entry), True, white)
                                alreadySet = True
                            else:
                                highScoreSurf = highScoreFont.render(str(place) + '.    ' + 'pts, '.join(entry), True, black)
                            highScoreRect = highScoreSurf.get_rect()
                            highScoreRect.midtop = (screenWidth / 2, screenHeight / 12 - 30 + counter)
                            counter += screenHeight/12
                            place += 1
                            playSurface.blit(highScoreSurf, highScoreRect)
                        pygame.display.flip()


                        while True: # endless loop until quit; displaying scoreboard
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:  # Quit logic
                                    pygame.quit()
                                    sys.exit()
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        print('K_ESCAPE')
                                        pygame.quit()
                                        sys.exit()

                    elif event.key == pygame.K_ESCAPE:
                        print('K_ESCAPE')
                        pygame.quit()
                        sys.exit()
                    else:
                        nameInput += event.unicode

        nameLabelFont = pygame.font.SysFont('monaco', 40)
        nameLabelSurf = nameLabelFont.render('Enter your Name', True, black)
        nameLabelRect = nameLabelSurf.get_rect()
        nameLabelRect.midtop = (screenWidth / 2, screenHeight/2 + 100)

        nameFont = pygame.font.SysFont('monaco', 40)
        nameSurf = nameFont.render(nameInput, True, white)
        nameRect = nameSurf.get_rect()
        nameRect.midtop = (screenWidth / 2, screenHeight/2 + 140)

        # Rendering BG
        playSurface.fill(darkBlue)

        # Rendering particles
        for particle in my_shots:
            particle.render()

        # Rendering FX
        for effect in FX_List:
            effect.render()

        # Rendering player
        player1.rotate()
        player1.render()

        # Rendering enemies
        for enemy in enemyList:
            enemy.render()
            enemy.rotate()

        # Rendering drop items
        for drop in dropList:
            drop.render()

        playSurface.blit(GOsurf, GOrect)
        playSurface.blit(nameLabelSurf, nameLabelRect)
        playSurface.blit(nameSurf, nameRect)
        renderUI(gameOverBool)
        pygame.display.flip()

    time.sleep(5)
    pygame.quit()
    sys.exit()

# UI Funcs
def renderUI(GO=0, playerweapon=''):
    ammoFont = pygame.font.SysFont('monaco', 40)
    ammoSurf = ammoFont.render('Ammo: '+ str(player1.ammo) + ' / ' + str(player1.ammoStash), True, white)
    ammoRect = ammoSurf.get_rect()

    warningFont = pygame.font.SysFont('monaco', 40)
    warningSurf = warningFont.render('Ammo: '+ str(player1.ammo), True, red)
    warningRect = warningSurf.get_rect()

    scoreFont = pygame.font.SysFont('monaco', 40)
    scoreSurf = scoreFont.render('Score: '+ str(score), True, white if GO==0 else black)
    scoreRect = scoreSurf.get_rect()

    timeFont = pygame.font.SysFont('monaco', 40)
    timeSurf = timeFont.render('Time: ' + str(('%02d:%02d' % (gameClock[0], gameClock[1]))), True, white)
    timeRect = timeSurf.get_rect()


    if GO == 0:
        scoreRect.midleft = (50, 50)
        ammoRect.midleft = (50, screenHeight-50)
        timeRect.midright = (screenWidth-50, screenHeight - 50)
        warningRect.midleft = (50, screenHeight - 50)
        playSurface.blit(ammoSurf, ammoRect)
        playSurface.blit(scoreSurf, scoreRect)
        playSurface.blit(timeSurf, timeRect)
        if player1.ammoWarning:
            playSurface.blit(warningSurf, warningRect)
            player1.ammoWarning -= 1
    else:
        scoreRect.midtop = (screenWidth/2, screenHeight/2 + 60)
        playSurface.blit(scoreSurf, scoreRect)


    ### render weapon besides ammo:
    texture = player1.weaponSprite
    texture = pygame.transform.scale(texture, (50, 50))
    imageRect = texture.get_rect()
    imageRect.bottomleft = (50, screenHeight-60)
    playSurface.blit(texture, imageRect)


# draw with alpha
def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

def pickupCheck(object):
    if (object.x > player1.x - 15 and object.x < player1.x + 15) and (object.y > player1.y - 15 and object.y < player1.y + 15):
        object.pickup()
        dropList.remove(object)


''' #################### MAIN LOOP ############################## '''

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #Quit logic
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # single shot, if revolver
            if player1.ammo > 0:
                player1.shoot(8 if player1.weapon == 'shotgun' else 1)
                player1.autoFire = True
            else:
                player1.ammoWarning = 3
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            player1.autoFire = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause = True
                paused()
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_r:
                player1.reload()
                player1.cooldownCounter = player1.reloadTime

    if player1.autoFire and player1.weapon == 'uzi' and player1.ammo > 0: # Todo: should work with second player param. like 'autofireCapability'
        player1.shoot()

    # get player movement
    keys = pygame.key.get_pressed()
    player1.move(keys)

    if keys[pygame.K_F1] and cheatMode:
        dropList.append(Pistol(player1.x, player1.y))
    if keys[pygame.K_F2] and cheatMode:
        dropList.append(Shotgun(player1.x, player1.y))
    if keys[pygame.K_F3] and cheatMode:
        dropList.append(Uzi(player1.x, player1.y))

    # spawn enemies
    #if enemySpawn and len(enemyList) < (enemyCount + score //100): # TEMP difficulty increase
    if gameTime/2 % spawnFrequency == 0 and len(enemyList) < (enemyCount + score //20):  # Todo: create better spawning/difficulty curve
        spawnEdges = [
                    (random.randint(0, screenWidth/10)*10, 0),
                    (screenWidth/10*10, random.randint(0, screenHeight/10)*10),
                    (random.randint(0, screenWidth/10)*10, screenWidth/10*10),
                    (0, screenWidth/10*10 )
                    ]
        randX, randY = random.choice(spawnEdges)

        token = random.choice([Enemy(randX, randY),
                               Enemy(randX, randY),
                               Enemy(randX, randY),
                               LargeEnemy(randX, randY)]) # hacking a 3 to 1 ratio
        enemyList.append(token)
        if spawnFrequency > 5:
            spawnFrequency -= 1

    # remove projectiles, when out of bound
    my_shots[:] = [shot for shot in my_shots if not shot.x <= 0 or shot.x >= screenWidth and not shot.y <= 0 or shot.y >= screenHeight] # TODO: comment on why using slice etc..

    # check projectile hits/kill
    for shot in my_shots:
        enemyDeathList = []
        for enemy in enemyList:
            if (shot.x > enemy.x - enemy.hitboxSize and shot.x < enemy.x + enemy.hitboxSize) and (shot.y > enemy.y - enemy.hitboxSize and shot.y < enemy.y + enemy.hitboxSize): # check if shot collides
                if enemy.health - player1.damage <= 0: # check if shot kills
                    if random.randint(1, 100) < enemy.dropchance:
                        dropList.append(random.choice([
                                                        Ammo(enemy.x, enemy.y),
                                                        Ammo(enemy.x, enemy.y),  # just upping the chance for ammo
                                                        Pistol(enemy.x, enemy.y),
                                                        Uzi(enemy.x, enemy.y),
                                                        Shotgun(enemy.x, enemy.y)
                                                       ]))
                        print('## DROP DROPPED: ', dropList[-1])
                    score += enemy.scoreVal
                    FX_List.append(fx_deadEnemy(enemy.x, enemy.y, enemy.radians))  # ToDo: crashbug: AttributeError: 'Enemy' object has no attribute 'radians'
                    enemyDeathList.append(enemy) # append to list, and then remove all from said list, to avoid .remove inside for loop
                else: # if does not kill, do damage
                    enemy.health -= player1.damage
                # in either case, do following
                FX_List.append(fx_bloodsplatter(enemy.x, enemy.y, enemy.radians))
                shot.penetration -= 1
                shot.colour = red
        enemyList[:] = [x for x in enemyList if x not in enemyDeathList]
        my_shots[:] = [x for x in my_shots if not x.penetration <= 0] # better then .remove inside for loop

    #check drop pickup
    for drop in dropList:
        pickupCheck(drop)


    # GAME OVER when player touches enemy
    for enemy in enemyList:
        if (player1.x > enemy.x - 15 and player1.x < enemy.x + 15) and (player1.y > enemy.y - 15 and player1.y < enemy.y + 15):
            gameOver()

    # Rendering BG
    renderBG()

    # Rendering FX
    for effect in FX_List:
        effect.render()
        effect.alpha -= effect.alphaStep  # decrements the alpha by one step
        if effect.alpha <= 0:
            FX_List.remove(effect)

    # Rendering player
    player1.rotate()
    player1.render()
    #pygame.draw.rect(playSurface, green, pygame.Rect(player1.x-1, player1.y-1, 3, 3))

    # Rendering enemies
    for enemy in enemyList:
        enemy.render()
        enemy.move()
        enemy.rotate()
        #pygame.draw.rect(playSurface, green, pygame.Rect(enemy.x-1, enemy.y-1, 3, 3))

    # Rendering particles
    for particle in my_shots:
        particle.render()
        particle.update()

    # Rendering drop items
    for drop in dropList:
        drop.render()
        #pygame.draw.rect(playSurface, green, pygame.Rect(drop.x-1, drop.y-1, 3, 3))
        drop.alpha -= drop.alphaStep # decrements the alpha by one step
        if drop.alpha <= 0:
            dropList.remove(drop)


    # common main logic parts

    if player1.cooldownCounter > 0:
        player1.cooldownCounter -= 1

    renderUI(gameOverBool)

    pygame.display.flip()

    # timer:
    gameTime += 1
    if gameTime % 30 == 0:
        print('gameTime: ', gameTime/30, ' | spawnfrequency: ', spawnFrequency)
    minutes = (gameTime//30)//60
    seconds = (gameTime//30) - minutes * 60
    gameClock = minutes, seconds




    fpsController.tick(30)

