from superwires import games
import math,os

MOVING_FRICTION=.2	
SLOWING_FRICTION=.05
ACCEL=3
ROT_SPEED=5
MISSILE_DELAY=50
MISSILE_VELOCITY=15
MISSILE_LIFE=150
MISSILE_BUFFER=10
MISSILE_IMAGE=None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Wrapper(games.Sprite):
	def check_wrap(self):
		if self.left>games.screen.width: self.left=0
		if self.right<0: self.right=games.screen.width
		if self.top>games.screen.height: self.top=0
		if self.bottom<0: self.bottom=games.screen.height

class Ship(Wrapper):
	def __init__(self):
		games.Sprite.__init__(self, games.load_image(resource_path('res/ship1.png')), x=games.screen.width/2, y=games.screen.height/2)
		self.convert=lambda t,r:(-math.cos(math.pi*t/180)*r, -math.sin(math.pi*t/180)*r)
		self.v=self.a=0
	
	def add_missile(self):
		buffer=self.convert(self.angle, (MISSILE_BUFFER+self.width/2))
		games.screen.add(Missile(buffer[0]+self.x, buffer[1]+self.y, *self.convert(self.angle, MISSILE_VELOCITY)))
	
	def update(self):
		#Physics
		self.a-=(MOVING_FRICTION if self.a else SLOWING_FRICTION)*self.v
		self.v=max(0, self.a+self.v)
		
		#Controls
		if games.keyboard.is_pressed(games.K_RIGHT): self.angle+=ROT_SPEED
		if games.keyboard.is_pressed(games.K_LEFT): self.angle-=ROT_SPEED
		self.a=ACCEL if games.keyboard.is_pressed(games.K_UP) else 0
		
		#Compute component velocity vectors in Cartesian form
		self.dx,self.dy=self.convert(self.angle, self.v)

		#Check Wrapping
		self.check_wrap()
	
	def tick(self):
		self.interval=1
		if games.keyboard.is_pressed(games.K_SPACE):
			self.interval=MISSILE_DELAY
			self.add_missile()

class Missile(Wrapper):
	def __init__(self, x, y, dx, dy):
		games.Sprite.__init__(self, MISSILE_IMAGE, x=x, y=y, dx=dx, dy=dy, interval=MISSILE_LIFE)
		self.tick=self.destroy

	def update(self):
		self.check_wrap()

def main():
	global MISSILE_IMAGE
	games.init(1600, 800, 50)
	MISSILE_IMAGE=games.load_image(resource_path('res/missile.png'), transparent=False)
	games.screen.background=games.load_image(resource_path('res/bg.png'), transparent=False)
	games.music.load(resource_path('res/music.mid'))
	games.music.play(-1)
	games.screen.add(Ship())
	games.screen.mainloop()

if __name__=='__main__':
	main()