import socket, threading, sys, time
from superwires import games, color
import Tkinter, os, math

MOVING_FRICTION=.13
SLOWING_FRICTION=.05
ACCEL=2
ROT_SPEED=5
MISSILE_DELAY=50
MISSILE_VELOCITY=20
MISSILE_LIFE=60
MISSILE_BUFFER=10
MISSILE_DAMAGE=5
COLLISION_DAMAGE=2
GAME_OVER=False
MISSILE_IMAGE=None
MISSILE_SOUND=None
root=None
BASE_WIDTH=1600
BASE_HEIGHT=900
#SCALE_RATIO=SCREEN_WIDTH/BASE_WIDTH
SCALE_RATIO=1

def load_scaled_image(file, transparent=True):
	return games.scale_image(games.load_image(file, transparent), SCALE_RATIO)
	
def load_images():
	images={"MISSILE_IMAGE": ('missile', False), "HEALTH_IMAGE": ('health_bar', False),
          	"BAR_OUTLINE_IMAGE": ('bar_outline', True), "BAR_BG_IMAGE": ('bar_bg', False)}
	for i in images:
		exec "global {0}; {0}=load_scaled_image(resource_path('res/{1}.png'), transparent={2})".format(i, images[i][0], images[i][1])


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def full_recv(conn, step=1):
	message=""
	while not message.endswith("|"):
		message+=conn.recv(step)
	
	return message.split("|")[-2]

class Wrapper(games.Sprite):
	def check_wrap(self):
		if self.left>games.screen.width: self.left=0
		if self.right<0: self.right=games.screen.width
		if self.top>games.screen.height: self.top=0
		if self.bottom<0: self.bottom=games.screen.height

class Missile(Wrapper):
	def __init__(self, x, y, dx, dy):
		games.Sprite.__init__(self, MISSILE_IMAGE, x=x, y=y, dx=dx, dy=dy, interval=MISSILE_LIFE)
		self.tick=self.destroy

	def update(self):
		self.check_wrap()

class Health(games.Sprite):
	def __init__(self, ship):
		global HEALTH_IMAGE
		self.ship=ship

		games.Sprite.__init__(self, HEALTH_IMAGE,
							  x=self.ship.x, y=50)
		
		self.pos=self.left
		
		self.outline=games.Sprite(BAR_OUTLINE_IMAGE, x=self.x, y=self.y)
		self.bg=games.Sprite(games.scale_image(BAR_BG_IMAGE, 0, 1), x=self.x, y=self.y)
		
	def update(self):
		self.left=self.pos
		self.bg.image=games.scale_image(BAR_BG_IMAGE, max(0, 100-self.ship.health), 1)
		self.outline.x=self.x
		self.bg.right=self.right
