'''
IDEAS (Gamedesign):
- Map gets smaller over time (Force action and agressive gameplay)
- Maybe tiles that break away if visited twice (crack on first time)

CHANGELOG:
- added background texture
- increased health in Characters classes
- picking heros now takes turns
- fixed pull (and assigned to elf)
- pushing/pulling off ledge now kills


TODO:
- add pregame phase to let players pick starting points
- clean up MAIN and sort functions into other files
- add background picker, that picks BG texture according to playFieldSize
- make background texture usage procedual (one hex-texture instance rendered per hex-coord)
- hit effect / die effect

'''


import pygame, random, math, time, sys, copy, itertools
import Characters as char

pygame.init()

# Important Game Vars - SCREEN and PLAYFIELD
width = 1024
length = 680

hexW = 50
hexH = 60
playFieldSize = 3

healthBarW = 40
healthBarH = 10

midpoint = [int(width / 2), int(length / 2)]
print('midpoint:', midpoint)

playFields = [midpoint]
holderList = []

# Important Game Vars - POSITIONS AND COUNTS

turnToggler = False
heroPos = [[],[]]  # List of ALL positions of objects; seperated into 2 sublists
activeHeroNo = 0
activeEnemyNo = 0
heroCount = 4
enemyCount = 4
heroTeam = [[], []]   # List of ALL objects-pointers; seperated into 2 sublists

'''  building board: '''
for i in range(playFieldSize):
    for currentpoint in playFields:
        field = [currentpoint[0] + hexW, currentpoint[1]]
        if field not in playFields and field not in holderList:
            holderList.append(field)
        field = [currentpoint[0] - hexW, currentpoint[1]]
        if field not in playFields and field not in holderList:
            holderList.append(field)
        field = [currentpoint[0] - hexW / 2, currentpoint[1] + hexH * 0.75]
        if field not in playFields and field not in holderList:
            holderList.append(field)
        field = [currentpoint[0] + hexW / 2, currentpoint[1] + hexH * 0.75]
        if field not in playFields and field not in holderList:
            holderList.append(field)
        field = [currentpoint[0] - hexW / 2, currentpoint[1] - hexH * 0.75]
        if field not in playFields and field not in holderList:
            holderList.append(field)
        field = [currentpoint[0] + hexW / 2, currentpoint[1] - hexH * 0.75]
        if field not in playFields and field not in holderList:
            holderList.append(field)
        print('holder: ', holderList)
    for i in holderList:
        playFields.append(i)
    holderList = []

print('playfields:', playFields)
print('len playfields:', len(playFields))

#input cooldown to prevent multiple inputs per button press
inputCooldown = 5
inputCooldownCounter = inputCooldown

#create Play Surface
playSurface = pygame.display.set_mode((width, length))
pygame.display.set_caption('Herobrawl')

# Colors
red = pygame.Color(255, 0, 0)
blue = pygame.Color(0, 0, 255)
green = pygame.Color(0, 255, 0)
yellow = pygame.Color(255, 255, 0)
white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)
grey = pygame.Color(128, 128, 128)

# FPS controller
fpsController = pygame.time.Clock()


# Important Game Functions

def HexDrawer(pos):
    return [[pos[0] - hexW / 2, pos[1] - hexH / 4],
            [pos[0], pos[1] - hexH / 2],
            [pos[0] + hexW / 2, pos[1] - hexH / 4],
            [pos[0] + hexW / 2, pos[1] + hexH / 4],
            [pos[0], pos[1] + hexH / 2],
            [pos[0] - hexW / 2, pos[1] + hexH / 4]]

def GameOver(team):
    if team == 0:
        print('Team GREEN wins!')
    if team == 1:
        print('Team RED wins!')
    GOFont = pygame.font.SysFont('monaco', 72)
    if team == 0:
        GOsurf = GOFont.render('Team GREEN wins!', True, green)
    if team == 1:
        GOsurf = GOFont.render('Team RED wins!', True, red)
    GOrect = GOsurf.get_rect()
    GOrect.midtop = (width/2, length/5)
    playSurface.blit(GOsurf, GOrect)
    pygame.display.flip()

    time.sleep(5)
    pygame.quit()
    sys.exit()


def Attack(oldPos, newPos, direction):
    '''
        Main attack function
    '''
    global activeHeroNo
    global activeEnemyNo
    dead = False

    # toggle, whos turn it is:
    activeNo = ''
    if turnToggler == False:
        activeNo = activeHeroNo
    elif turnToggler == True:
        activeNo = activeEnemyNo

    x = heroPos[not turnToggler].index(newPos)
    print('x (target heros position index in heroPos list) = ', x)
    heroTeam[not turnToggler][x].health -= heroTeam[turnToggler][activeNo].damage
    if heroTeam[not turnToggler][x].health <= 0: # kills from both lists if healt < 0
        heroPos[not turnToggler].pop(x)
        heroTeam[not turnToggler].pop(x)
        heroPos[turnToggler][activeNo] = newPos # Moves to new pos
        # print('popping: ', heroTeam[not turnToggler][x], ' from heroPos')
        if len(heroPos[0]) == 0:
            GameOver(1)
        if len(heroPos[1]) == 0:
            GameOver(0)
        activeHeroNo = 0
        activeEnemyNo = 0
        heroPos[turnToggler][activeNo] = newPos
        dead = True
        return dead
    heroPos[turnToggler][activeNo] = oldPos
    if heroTeam[turnToggler][activeNo].push != 0:
        Push(direction, x, heroTeam[turnToggler][activeNo].push, activeNo)
    if heroTeam[turnToggler][activeNo].swap == True:
        Swap(direction, x, activeNo)
    return dead

def Move(direction, pos):
    '''
        Calculates next field from given position and direction

        Returns new position (newPos)
        Returns animation position (animPos)
    '''
    if direction == 'RIGHT':
        newPos = [pos[0] + hexW, pos[1]]
        animPos = [pos[0] + hexW * 0.5, pos[1]]
    if direction == 'LEFT':
        newPos = [pos[0] - hexW, pos[1]]
        animPos = [pos[0] - hexW * 0.5, pos[1]]
    if direction == 'UPRIGHT':
        newPos = [pos[0] + hexW * 0.5, pos[1] - hexH * 0.75]
        animPos = [pos[0] + hexW * 0.25, pos[1] - hexH * 0.375]
    if direction == 'DOWNRIGHT':
        newPos = [pos[0] + hexW * 0.5, pos[1] + hexH * 0.75]
        animPos = [pos[0] + hexW * 0.25, pos[1] + hexH * 0.375]
    if direction == 'UPLEFT':
        newPos = [pos[0] - hexW * 0.5, pos[1] - hexH * 0.75]
        animPos = [pos[0] - hexW * 0.25, pos[1] - hexH * 0.375]
    if direction == 'DOWNLEFT':
        newPos = [pos[0] - hexW * 0.5, pos[1] + hexH * 0.75]
        animPos = [pos[0] - hexW * 0.25, pos[1] + hexH * 0.375]
    print('newPos: ', newPos)

    return newPos, animPos

def InvertDirection(direction):
    '''
        Inverts movement direction.
         - Needed for some hero interactions e.g. pull (negativ push)
    '''
    switcher = {
        'LEFT': 'RIGHT',
        'RIGHT': 'LEFT',
        'UPRIGHT': 'DOWNLEFT',
        'DOWNLEFT': 'UPRIGHT',
        'UPLEFT': 'DOWNRIGHT',
        'DOWNRIGHT': 'UPLEFT'
    }
    return switcher[direction]


def Dash(direction, pos, dash):
    '''
        Goes multiple fields forward to enemy and hits him.
        The distance is defined in character object as "DASH". Min dash is two
         - Lands on field before enemy if enemy survives.
         - Lands on field of enemy if enemy dies
         - Only goes one field if enemy is too far away
         - Can't dash over enemies or friends
    '''
    for i in range(dash):
        newPos, animPos = Move(direction, pos)
        dashPos = pos
        pos = newPos
        if newPos in heroPos[not turnToggler]:  # ATTACK
            print()
            print('ENEMY!')
            return newPos, animPos, dashPos
        elif newPos in heroPos[turnToggler]:  # checks collision
            print('FRIEND!')
            try:
                firstnewPos
            except NameError:
                print('not declared')
                firstnewPos = None
            if firstnewPos is not None:
                newPos = firstnewPos
                animPos = firstanimPos
            dashPos = None
            return newPos, animPos, dashPos
        elif newPos not in playFields:
            print('OUT OF BOUNDS!')
            try:
                firstnewPos
            except NameError:
                firstnewPos = None
            if firstnewPos is not None:
                newPos = firstnewPos
                animPos = firstanimPos
            dashPos = None
            return newPos, animPos, dashPos
        else:
            print('FREE!')
            if i == 0:
                firstnewPos = newPos
                firstanimPos = animPos
            if i == (dash - 1):
                newPos = firstnewPos
                animPos = firstanimPos
    dashPos = None
    return newPos, animPos, dashPos

def Shoot(direction, pos, shoot):
    '''
        Shoots an arrow (or some other kind of projectile) on an enemy
        - Only enemies in direct sight can be hit with that rock (or arrow)
          You cant shoot over (or through) your friends
        - Moves one field if there is no hero in reach
    '''
    for i in range(shoot):
        newPos, animPos = Move(direction, pos)
        pos = newPos
        if newPos in heroPos[not turnToggler]:  # ATTACK
            print()
            print('ENEMY!')
            return newPos, animPos
        elif newPos in heroPos[turnToggler]:  # checks collision
            print('FRIEND!')
            try:
                firstnewPos
            except NameError:
                print('not declared')
                firstnewPos = None
            if firstnewPos is not None:
                newPos = firstnewPos
                animPos = firstanimPos
            return newPos, animPos
        elif newPos not in playFields:
            print('OUT OF BOUNDS!')
            try:
                firstnewPos
            except NameError:
                firstnewPos = None
            if firstnewPos is not None:
                newPos = firstnewPos
                animPos = firstanimPos
            return newPos, animPos
        else:
            print('FREE!')
            if i == 0:
                firstnewPos = newPos
                firstanimPos = animPos
            if i == (dash - 1):
                newPos = firstnewPos
                animPos = firstanimPos
    return newPos, animPos


def Push(direction, x, push, activeNo):
    '''
        Push (or pull) enemy after successful hit
        - enemy lands one (or more) fields away in attacking direction
        - if enemy pushed successfully attacker lands on former enemy field
        - if pulled (negative value on push) enemy lands on field behind attacker or further
        - attacker doesn't move after pull
    '''
    pos = heroPos[not turnToggler][x]
    print('Origin Pos:    ', pos)
    if push < 0:
        print('PULLING    ', push)
        direction = InvertDirection(direction)
        print('inverterd direction   ', direction)
        newPos, animPos = Move(direction, pos)
        pos = newPos
        push = push * -1
    else:
        print('PUSH!   ', push)

    for i in range(push):
        newPos, animPos = Move(direction, pos)
        print('Push old Position:  ', pos)
        print('Push new Position:  ', newPos, animPos)
        if newPos in heroPos[not turnToggler]:
            return True
        elif newPos in heroPos[turnToggler]:
            return False
        elif newPos not in playFields:
            print('shoving off the ledge!')
            heroPos[not turnToggler].pop(x)
            heroTeam[not turnToggler].pop(x)
            if len(heroPos[0]) == 0:
                GameOver(1)
            if len(heroPos[1]) == 0:
                GameOver(0)
            activeHeroNo = 0
            activeEnemyNo = 0
            dead = True
            return dead
        else:
            heroPos[not turnToggler][x] = newPos
            if i == 0:
                heroPos[turnToggler][activeNo] = pos
            pos = newPos

def Swap(direction, x, activeNo):
    newheroPos = heroPos[not turnToggler][x]
    heroPos[not turnToggler][x] = heroPos[turnToggler][activeNo]
    heroPos[turnToggler][activeNo] = newheroPos

def InitMove(direction):
    global activeHeroNo
    global activeEnemyNo

    #check whos turn it is and set him to activeNo:
    activeNo = ''
    if turnToggler == False:
        activeNo = activeHeroNo
    elif turnToggler == True:
        activeNo = activeEnemyNo
    print()
    print('turnToggler: ', turnToggler)
    print('heroPos[turnToggler] :', heroPos[turnToggler])
    print('heroTeam[turnToggler] :', heroTeam[turnToggler])

    oldPos = copy.copy(heroPos[turnToggler][activeNo])
    newPos = []
    animPos = []

    ''' THIS CALLS THE NEW MOVE! ########################'''
    pos = [heroPos[turnToggler][activeNo][0], heroPos[turnToggler][activeNo][1]]
    print(pos)
    if heroTeam[turnToggler][activeNo].dash > 0:
        print('Dashing')
        newPos, animPos, dashPos = Dash(direction, pos, heroTeam[turnToggler][activeNo].dash)
    else:
        newPos, animPos = Move(direction, pos)

    heroPos[turnToggler][activeNo] = animPos #half Movement step

    image = pygame.image.load(str(heroTeam[turnToggler][activeNo].image))
    imagerect = image.get_rect()
    imagerect.center = animPos
    playSurface.blit(image, imagerect)
    pygame.display.flip()

    pygame.time.delay(200)


    if newPos in heroPos[not turnToggler]: #ATTACK
        print()
        print('ATTACK!')
        dead = Attack(oldPos, newPos, direction)
        try:
            dashPos
        except NameError:
            dashPos = None
        if dashPos is not None:
            heroPos[turnToggler][activeNo] = dashPos
            if dead == True:
                heroPos[turnToggler][activeNo] = newPos
        return True
    elif newPos in heroPos[turnToggler]: #checks collision
        print('InitMove function detected collision with FRIEND, Movement canceled')
        heroPos[turnToggler][activeNo] = oldPos
        return False
    elif newPos not in playFields:
        print('Not a valid play field, Movement canceled')
        heroPos[turnToggler][activeNo] = oldPos
        return False
    else:
        heroPos[turnToggler][activeNo] = newPos
        return True

def HealthBarDrawer(pos, health, maxHealth):
    fraction = int(healthBarW / maxHealth)  # gets pixel-width of each healthbar sub portions (rounded as an integer)
    maxBar =  [[pos[0] - healthBarW / 2, pos[1] + 10 + healthBarH],
               [pos[0] + healthBarW / 2, pos[1] + 10 + healthBarH],
               [pos[0] + healthBarW / 2, pos[1] + 10],
               [pos[0] - healthBarW / 2, pos[1] + 10]]
    currentBar = [[pos[0] - healthBarW / 2, pos[1] + 10 + healthBarH],
                  [pos[0] - healthBarW / 2 + health * fraction, pos[1] + 10 + healthBarH],
                  [pos[0] - healthBarW / 2 + health * fraction, pos[1] + 10],
                  [pos[0] - healthBarW / 2, pos[1] + 10]]
    pygame.draw.polygon(playSurface, red, maxBar , 0)  # draw red base
    pygame.draw.polygon(playSurface, green, currentBar, 0)  # draw green partial overlay
    pygame.draw.polygon(playSurface, white, maxBar, 2)  # draw white frame overlay

def RenderHero(index, pos, team):
    #strPos = '' + str(int(pos[0])) + '/' + str(int(pos[1]))
    #heroFont = pygame.font.SysFont('monaco', 18)
    #heroSurf = heroFont.render(str(index), True, yellow)
    #heroSurf2 = heroFont.render(str(strPos), True, yellow)
    #heroSurf3 = heroFont.render(str(team[index].class_Name), True, yellow)
    ###################heroSurf = heroFont.render(str(team[index].health), True, yellow)
    #heroRect = heroSurf.get_rect()
    #heroRect.inflate_ip(10, 10)
    image = pygame.image.load(str(team[index].image))
    imagerect = image.get_rect()
    imagerect.center = pos
    playSurface.blit(image, imagerect)
    HealthBarDrawer(pos, team[index].health, team[index].maxHealth)
    #heroRect.midtop = pos
    #playSurface.blit(heroSurf2, heroRect)
    #heroRect.midbottom = pos
    #playSurface.blit(heroSurf, heroRect)
    #heroRect.center = pos
    #playSurface.blit(heroSurf3, heroRect)



def gameIntro():
    global inputCooldownCounter
    global turnToggler
    intro = True

    # reserving player-positions
    while len(heroPos[0]) < heroCount:
        n = random.choice(playFields)
        print('n: ', n)
        if n not in heroPos[0] and n not in heroPos[1]:
            heroPos[0].append(copy.copy(n))
            print('assembly: heroPos: ', heroPos)
        else:
            print('spawner: field taken')

    # reserving enemy-positions
    while len(heroPos[1]) < enemyCount:
        n = random.choice(playFields)
        print('n: ', n)
        if n not in heroPos[0] and n not in heroPos[1]:  # to make shure it's not spawning on taken fields
            heroPos[1].append(copy.copy(n))
            print('assembly: heroPos: ', heroPos)
        else:
            print('spawner: field taken')

    print('heroPos: ', heroPos)

    count = 0  # used for indexing the object-creator

    while intro == True:  # pregame logic loop
        for event in pygame.event.get():

           if event.type == pygame.QUIT:
               pygame.quit()
               sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        #Below comes the actual switch for choosing the heros and filling heroTeam list
        if keys[pygame.K_1]:
            if inputCooldownCounter == 0:
                heroTeam[turnToggler].append(char.Dwarf(count))
                turnToggler = not turnToggler
                print("button 1 pressed, Dwarf added")
                inputCooldownCounter = inputCooldown

        if keys[pygame.K_2]:
            if inputCooldownCounter == 0:
                heroTeam[turnToggler].append(char.Elf(count))
                turnToggler = not turnToggler
                print("button 2 pressed, Elf added")
                inputCooldownCounter = inputCooldown

        if keys[pygame.K_3]:
            if inputCooldownCounter == 0:
                heroTeam[turnToggler].append(char.Daemon(count))
                turnToggler = not turnToggler
                print("button 3 pressed, Daemon added")
                inputCooldownCounter = inputCooldown

        if keys[pygame.K_4]:
            if inputCooldownCounter == 0:
                heroTeam[turnToggler].append(char.Berserk(count))
                turnToggler = not turnToggler
                print("button 4 pressed, Berserk added")
                inputCooldownCounter = inputCooldown

        if len(heroTeam[0]) == heroCount and len(heroTeam[1]) == enemyCount:
            print("Teams complete! Starting Game...")
            intro = False


        # Rendering background:
        bg = pygame.image.load('TitleScreen.png')
        bgRect = bg.get_rect()
        bgRect.center = midpoint
        playSurface.blit(bg, bgRect)
        #playSurface.fill(grey)  # old grey background

        # Rendering UI and texts
        introFont = pygame.font.SysFont('Creepster-Regular.ttf', 45)
        introSurf = introFont.render('Take turns and pick your Heros!', True, white)
        introRect = introSurf.get_rect()
        introRect.midtop = (width / 2, length / 5)
        playSurface.blit(introSurf, introRect)

        pickedBarL = [[midpoint[0] - 400, midpoint[1] - 200],
                  [midpoint[0] - 300, midpoint[1] - 200],
                  [midpoint[0] - 300, midpoint[1] + 200],
                  [midpoint[0] - 400, midpoint[1] + 200]]
        pygame.draw.polygon(playSurface, green, pickedBarL, 10)  # draw left black frame

        pickedBarR = [[midpoint[0] + 400, midpoint[1] - 200],
                  [midpoint[0] + 300, midpoint[1] - 200],
                  [midpoint[0] + 300, midpoint[1] + 200],
                  [midpoint[0] + 400, midpoint[1] + 200]]
        pygame.draw.polygon(playSurface, red, pickedBarR, 10)  # draw right black frame

        # Rendering Heros

        for i in heroTeam[0]:  # Team 0
            RenderHero(heroTeam[0].index(i), [midpoint[0] - 350, midpoint[1] - 150 + heroTeam[0].index(i) * 100], heroTeam[0])

        for i in heroTeam[1]:  # Team 1
            RenderHero(heroTeam[1].index(i), [midpoint[0] + 350, midpoint[1] - 150 + heroTeam[1].index(i) * 100], heroTeam[1])

        pygame.display.update()
        fpsController.tick(30)
        if inputCooldownCounter >= 1:
            inputCooldownCounter -= 1

            # finally, before starting Main Loop:
    print('heroTeam = ', heroTeam)
    print('charCount: ', char.Character.charCount)


# Main Logic and Loop *************************************************************************************************

gameIntro()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()
    if keys[pygame.K_LEFT] and not keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
        if inputCooldownCounter == 0:
            if InitMove('LEFT'):
                inputCooldownCounter = inputCooldown/2
                turnToggler = not turnToggler
    if keys[pygame.K_RIGHT] and not keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
        if inputCooldownCounter == 0:
            if InitMove('RIGHT'):
                inputCooldownCounter = inputCooldown/2
                turnToggler = not turnToggler
    if keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
        if inputCooldownCounter == 0:
            if InitMove('DOWNRIGHT'):
                inputCooldownCounter = inputCooldown/2
                turnToggler = not turnToggler
    if keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
        if inputCooldownCounter == 0:
            if InitMove('DOWNLEFT'):
                inputCooldownCounter = inputCooldown/2
                turnToggler = not turnToggler
    if keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
        if inputCooldownCounter == 0:
            if InitMove('UPRIGHT'):
                inputCooldownCounter = inputCooldown/2
                turnToggler = not turnToggler
    if keys[pygame.K_UP] and keys[pygame.K_LEFT]:
        if inputCooldownCounter == 0:
            if InitMove('UPLEFT'):
                inputCooldownCounter = inputCooldown/2
                turnToggler = not turnToggler

    if keys[pygame.K_SPACE]:  # change hero
        if turnToggler:
            if inputCooldownCounter == 0:
                if activeEnemyNo <= len(heroPos[1]) - 2:
                    activeEnemyNo += 1
                else:
                    activeEnemyNo = 0
            print('activeEnemyNo: ', activeEnemyNo)
        if not turnToggler:
            if inputCooldownCounter == 0:
                if activeHeroNo <= len(heroPos[0]) - 2:
                    activeHeroNo += 1
                else:
                    activeHeroNo = 0
            print('activeHeroNo: ', activeHeroNo)

        inputCooldownCounter = inputCooldown

    # Rendering
    # Rendering background:
    bg = pygame.image.load('background_size3.png')
    bgRect = bg.get_rect()
    bgRect.center = midpoint
    playSurface.blit(bg, bgRect)
    #playSurface.fill(grey)  # old grey bg

    for pos in heroPos[0]:  # rendering heroes
        pygame.draw.polygon(playSurface, green, HexDrawer(pos))
        RenderHero(heroPos[0].index(pos), pos, heroTeam[0])
    for pos in heroPos[1]:  # rendering enemies
        pygame.draw.polygon(playSurface, red, HexDrawer(pos))
        RenderHero(heroPos[1].index(pos), pos, heroTeam[1])
    '''for field in playFields :  # rendering hex fields
        pygame.draw.polygon(playSurface, black, HexDrawer(field), 3)
    ''' # deactivated ATM, since hexfields are in background texture

    for pos in heroPos[0]: # rendering white outline
        if pos == heroPos[0][activeHeroNo] and not turnToggler:
            pygame.draw.polygon(playSurface, white, HexDrawer(pos), 5)
    for pos in heroPos[1]:  # rendering white outline
        if pos == heroPos[1][activeEnemyNo] and turnToggler:
            pygame.draw.polygon(playSurface, white, HexDrawer(pos), 5)

    # common main logic parts
    if inputCooldownCounter >= 1:
        inputCooldownCounter -= 1

    pygame.display.flip()

    fpsController.tick(30)

