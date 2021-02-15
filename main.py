"""  https://github.com/voidstarr/PySpaceGame
    rewrite of https://github.com/voidstarr/SpaceGame
    derived from https://github.com/pygame/pygame/blob/main/examples/aliens.py
""" 
import random
import os
import pygame as pg

# game constants
MAX_SHOTS = 2  # most player bullets onscreen
ALIEN_ODDS = 22  # chances a new alien appears
BOMB_ODDS = 60  # chances a new bomb will drop
ALIEN_RELOAD = 12  # frames between new aliens
SCREENRECT = pg.Rect(0, 0, 640, 480)

#globals
SCORE = 0
AMMO = 30
ALIENS_LEFT = 0
LIVES = 3
STAGE = 1

WINS = 0
LOSSES = 0
ALIENS_KILLED = 0
AMMO_USED = 0


main_dir = os.path.split(os.path.abspath(__file__))[0]

class Player(pg.sprite.Sprite):
  """ Representing the player as a moon buggy type car.
  """

  speed = 10
  images = []

  def __init__(self):
    pg.sprite.Sprite.__init__(self, self.containers)
    self.image = self.images[0]
    self.rect = self.image.get_rect(midleft=SCREENRECT.midleft)
    self.ammo = 30

  def move(self, x_direction, y_direction):
    self.rect.move_ip(x_direction * self.speed, y_direction * self.speed)
    self.rect = self.rect.clamp(SCREENRECT)

  def reset_pos():
    self.rect = self.image.get_rect(midleft=SCREENRECT.midleft)

class Alien(pg.sprite.Sprite):
  """ An alien space ship. That slowly moves down the screen.
  """

  speed = -8
  images = []

  def __init__(self):
    pg.sprite.Sprite.__init__(self, self.containers)
    self.image = self.images[0]
    self.rect = self.image.get_rect(right=SCREENRECT.right)
    self.rect.y = random.randint(40, SCREENRECT.height)

  def update(self):
    self.rect.move_ip(self.speed, 0)
    if not SCREENRECT.contains(self.rect):
      self.rect.right = SCREENRECT.right
      self.rect = self.rect.clamp(SCREENRECT)

class Drop(pg.sprite.Sprite):
  """ Useful drop from an alien.
  """

  speed = -8
  images = []

  def __init__(self, center):
    if random.random() >= 0.8:
      self.ammo = 1
    else:
      self.ammo = 0
    pg.sprite.Sprite.__init__(self, self.containers)
    self.image = self.images[self.ammo]
    self.rect = self.image.get_rect(center=center)

  def update(self):
    self.rect.move_ip(self.speed, 0)
    if not SCREENRECT.contains(self.rect):
      self.rect.right = SCREENRECT.right
      self.rect = self.rect.clamp(SCREENRECT)

class Shot(pg.sprite.Sprite):
  """ a bullet the Player sprite fires.
  """

  speed = 11
  images = []

  def __init__(self, pos):
    pg.sprite.Sprite.__init__(self, self.containers)
    self.image = self.images[0]
    self.rect = self.image.get_rect(midbottom=pos)

  def update(self):
    """ called every time around the game loop.
    Every tick we move the shot right-wards.
    """
    self.rect.move_ip(self.speed,0)
    if self.rect.right >= SCREENRECT.right:
      self.kill()

class InGameInfo(pg.sprite.Sprite):
  """ to keep track of the score.
  """

  def __init__(self):
    pg.sprite.Sprite.__init__(self, self.containers)
    self.font = pg.font.Font(None, 24)
    self.color = pg.Color("white")
    self.update()
    self.rect = self.image.get_rect(topleft=SCREENRECT.topleft)

  def update(self):
    """ We only update the score in update() when it has changed.
    """
    msg = "Aliens left: %d  Points: %d Stage: %d Lives: %d Ammo: %d" % (ALIENS_LEFT, SCORE, STAGE, LIVES, AMMO)
    self.image = self.font.render(msg, 0, self.color)

class Results(pg.sprite.Sprite):
  """ to keep track of the score.
  """

  def __init__(self):
    pg.sprite.Sprite.__init__(self, self.containers)
    self.font = pg.font.Font(None, 24)
    self.color = pg.Color("white")
    self.update()
    self.rect = self.image.get_rect(topleft=SCREENRECT.topleft)

  def update(self):
    """ We only update the score in update() when it has changed.
    """
    msg = "Aliens left: %d  Points: %d Stage: %d Lives: %d Ammo: %d" % (ALIENS_LEFT, SCORE, STAGE, LIVES, AMMO)
    self.image = self.font.render(msg, 0, self.color)


def load_image(file):
  """ loads an image, prepares it for play
  """
  file = os.path.join(main_dir, "res", file)
  try:
    surface = pg.image.load(file)
  except pg.error:
    raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
  return surface.convert()

def main(winstyle=0):
  pg.init()
  global SCORE
  global AMMO
  global ALIENS_LEFT
  global LIVES
  global STAGE

  global WINS
  global LOSSES
  global ALIENS_KILLED
  global AMMO_USED

  fullscreen = False
  # Set the display mode
  winstyle = 0   #|FULLSCREEN
  bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
  screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

  # Load images, assign to sprite classes
  # (do this before the classes are used, after screen setup)
  img = load_image("craft.png")
  Player.images = [img]
  Alien.images = [load_image("alien.png")]
  Shot.images = [load_image("projectile.png")]
  Drop.images = [load_image("life.png"), load_image("ammo.png")]

  pg.display.set_caption("Pygame SpaceGame")

  background = pg.transform.scale(load_image("background.png"), (640, 480))
  
  screen.blit(background, (0, 0))
  pg.display.flip()


  aliens = pg.sprite.Group()
  shots = pg.sprite.Group()
  drops = pg.sprite.Group()
  bombs = pg.sprite.Group()
  all = pg.sprite.RenderUpdates()
  lastalien = pg.sprite.GroupSingle()
  endscreen = pg.sprite.RenderUpdates()

  Player.containers = all
  Alien.containers = aliens, all, lastalien
  Shot.containers = shots, all
  Drop.containers = drops, all
  InGameInfo.containers = all, endscreen

  #create Some Starting Values
  alienreload = ALIEN_RELOAD
  clock = pg.time.Clock()
  last_shot = pg.time.get_ticks()

  # initialize our starting sprites
  player = Player()
  in_game_info = InGameInfo()

  # stage 1 starts with 5 aliens
  for x in range(4):
    Alien()

  ALIENS_LEFT = len(aliens)

  while True:
    for event in pg.event.get():
      if event.type == pg.QUIT:
        return
      if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
        return

    all.clear(screen, background)
    endscreen.clear(screen, background)
    keystate = pg.key.get_pressed()

    if player.alive():
      in_game_info.update()

      # update all the sprites
      all.update()

      # handle player input
      x_direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
      y_direction = keystate[pg.K_DOWN] - keystate[pg.K_UP]
      player.move(x_direction, y_direction)
      
      if AMMO > 0 and keystate[pg.K_SPACE] and pg.time.get_ticks() - last_shot > 100:
        last_shot = pg.time.get_ticks()
        Shot(player.rect.bottomright)
        AMMO -= 1

      # Create new alien
      #if alienreload:
      #  alienreload = alienreload - 1
      #elif not int(random.random() * ALIEN_ODDS):
      #  Alien()
      #  alienreload = ALIEN_RELOAD

      for drop in pg.sprite.spritecollide(player, drops, 1):
        SCORE += 100
        if drop.ammo:
          AMMO += random.randint(1, 20)
        else:
          LIVES += 1 
          

      # Detect collisions between aliens and players.
      for alien in pg.sprite.spritecollide(player, aliens, 1):
        print("player alien colision.");
        SCORE += 100
        ALIENS_LEFT -= 1
        LIVES -= 1
        if (LIVES == 0):
          LOSSES += 1
          player.kill()

      # See if shots hit the aliens.
      for alien in pg.sprite.groupcollide(shots, aliens, 1, 1).keys():
        SCORE += 100
        ALIENS_KILLED += 1
        ALIENS_LEFT -= 1
        if random.random() < 0.3:
          Drop(alien.rect.center)

      # all aliens are dead? go to next stage or win the game!
      if(len(aliens) == 0 and player.alive()):
        if(STAGE == 10):
          WINS += 1
          player.kill()
        else:
          STAGE += 1
          ALIENS_LEFT = STAGE * 5
          for i in range(ALIENS_LEFT-1):
            Alien()
        
      
      dirty = all.draw(screen)
      pg.display.update(dirty)
    else:
      if keystate[pg.K_r]:
        print("restart")
        STAGE = 1
        ALIENS = 5
        AMMO = 30
        LIVES = 3
        SCORE = 0
        player = Player()
      font = pg.font.Font(None, 24)
      font_color = pg.Color("white")

        #global WINS
      wins = pg.sprite.Sprite(endscreen)
      wins.image = font.render("Wins: %d" % WINS, 0, font_color)
      wins.rect = wins.image.get_rect(midbottom=SCREENRECT.center)

      restart_text = pg.sprite.Sprite(endscreen)
      restart_text.image = font.render("Press R to restart", 0, font_color)
      restart_text.rect = restart_text.image.get_rect(midtop=wins.rect.midbottom)

      
  #global LOSSES
      losses = pg.sprite.Sprite(endscreen)
      losses.image = font.render("Losses: %d" % LOSSES, 0, font_color)
      losses.rect = losses.image.get_rect(midbottom=wins.rect.midtop)


  #global ALIENS_KILLED
      aliens_killed = pg.sprite.Sprite(endscreen)
      aliens_killed.image = font.render("Aliens killed: %d" % ALIENS_KILLED, 0, font_color)
      aliens_killed.rect = aliens_killed.image.get_rect(midbottom=losses.rect.midtop)


  #global AMMO_USED
      ammo_used = pg.sprite.Sprite(endscreen)
      ammo_used.image = font.render("Ammo used: %d" % AMMO_USED, 0, font_color)
      ammo_used.rect = ammo_used.image.get_rect(midbottom=aliens_killed.rect.midtop)

      result = pg.sprite.Sprite(endscreen)
      result.image = font.render("You Win" if STAGE == 10 else "You Lose", 0, font_color)
      result.rect = result.image.get_rect(midbottom=ammo_used.rect.midtop)


      dirty = endscreen.draw(screen)
      pg.display.update(dirty)
    clock.tick(40)

  pg.time.wait(1000)
  pg.quit()

if __name__ == "__main__":
  main()
