from superwires import games, color
import math,os,socket,sys

import Tkinter

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
MISSILE_SOUND=None
GAME_OVER=False
root=Tkinter.Tk()
SCREEN_WIDTH=root.winfo_screenwidth()
SCREEN_HEIGHT=root.winfo_screenheight()
BASE_WIDTH=1600
BASE_HEIGHT=900
SCALE_RATIO=SCREEN_WIDTH/BASE_WIDTH
print SCALE_RATIO

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
	
	return message.replace("|", "")

class Wrapper(games.Sprite):
	def check_wrap(self):
		if self.left>games.screen.width: self.left=0
		if self.right<0: self.right=games.screen.width
		if self.top>games.screen.height: self.top=0
		if self.bottom<0: self.bottom=games.screen.height

class Ship(Wrapper):
	
	KEYS=[games.K_RIGHT, games.K_LEFT, games.K_UP, games.K_SPACE]
	
	def __init__(self, num):
		games.Sprite.__init__(self, load_scaled_image(resource_path('res/ship'+str(num)+'.png')),
							  x=games.screen.width-200 if num==1 else 200,
							  y=games.screen.height/2, angle=0 if num==1 else 180)
							  
		self.convert=lambda t,r:(-math.cos(math.pi*t/180)*r, -math.sin(math.pi*t/180)*r)
		self.num=num
		self.v=self.a=0
		self.health=100
		self.keys=[]

		if not MISSILE_SOUND:
			load_images()
			global MISSILE_SOUND
			MISSILE_SOUND=games.load_sound(resource_path('res/missile.wav'))
		
		self.health_bar=Health(self)
		games.screen.add(self.health_bar)
		games.screen.add(self.health_bar.outline)
		games.screen.add(self.health_bar.bg)

		self.frozen=False
	
	def add_missile(self):
		buffer=self.convert(self.angle, (MISSILE_BUFFER+self.width/2))
		games.screen.add(Missile(buffer[0]+self.x, buffer[1]+self.y, *self.convert(self.angle, MISSILE_VELOCITY)))
		MISSILE_SOUND.play()
	
	def lose_health(self, amount=MISSILE_DAMAGE):
		self.health-=amount
		print "\a"
	
	def update(self):
		#Physics
		self.a-=(MOVING_FRICTION if self.a else SLOWING_FRICTION)*self.v
		self.v+=self.a
		self.v=(max if self.v>0 else min)(0, self.v)
		
		#Controls
		if not self.frozen:
			if games.K_RIGHT in self.keys: self.angle+=ROT_SPEED
			if games.K_LEFT in self.keys: self.angle-=ROT_SPEED
			self.a=ACCEL if games.K_UP in self.keys else 0
			
		#Compute component velocity vectors in Cartesian form
		self.dx,self.dy=self.convert(self.angle, self.v)

		#Check Wrapping
		self.check_wrap()
		
		for i in self.overlapping_sprites:
			if isinstance(i, Missile):
				self.lose_health()
				i.destroy()
		
		if self.health<=0:
			global GAME_OVER
			GAME_OVER=True
		
		if GAME_OVER:
			self.frozen=True
			if self.num==1:
				games.screen.add(games.Message("GAME OVER", 200, color.white,
								 x=games.screen.width/2, y=games.screen.height/2,
								 lifetime=150, after_death=games.screen.quit))
			
			games.screen.add(games.Text("You"+ "Won" if self.health else "Lose", 100, color.white, x=games.screen.width, y=600))
			
	def tick(self):
		self.interval=1
		if games.K_SPACE in self.keys and not self.frozen:
			self.interval=MISSILE_DELAY
			self.add_missile()

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