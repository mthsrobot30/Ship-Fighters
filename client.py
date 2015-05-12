import threading,socket,sys
from superwires import games, color
import Tkinter, os, math

from game_engine import *

SERVER_ADDRESS=None
ip_enter=None

class Ship(Wrapper):
	
	KEYS=[games.K_RIGHT, games.K_LEFT, games.K_UP, games.K_SPACE]
	
	def __init__(self, num, game):
		games.Sprite.__init__(self, load_scaled_image(resource_path('res/ship'+str(num)+'.png')),
							  x=games.screen.width-200 if num==1 else 200,
							  y=games.screen.height/2, angle=0 if num==1 else 180)
							  
		self.convert=lambda t,r:(-math.cos(math.pi*t/180)*r, -math.sin(math.pi*t/180)*r)
		self.num=num
		self.v=self.a=0
		self.health=100
		self.keys=[]
		self.game=game

		if not MISSILE_IMAGE:
			global MISSILE_SOUND
			MISSILE_SOUND=games.load_sound("missile.wav")
			load_images()
		
		self.health_bar=Health(self)
		games.screen.add(self.health_bar)
		games.screen.add(self.health_bar.outline)
		games.screen.add(self.health_bar.bg)

		self.frozen=False
	
	def add_missile(self):
		buffer=self.convert(self.angle, (MISSILE_BUFFER+self.width/2))
		missile=Missile(buffer[0]+self.x, buffer[1]+self.y, *self.convert(self.angle, MISSILE_VELOCITY))
		games.screen.add(missile)
		self.game.missiles.append(missile)
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
			if self.num==self.game.num:
				games.screen.add(games.Message("GAME OVER", 200, color.white,
								 x=games.screen.width/2, y=games.screen.height/2,
								 lifetime=50, after_death=games.screen.quit))
			
				games.screen.add(games.Text("You "+ ("Won" if self.health else "Lost") +"!", 100, color.white, x=games.screen.width/2, y=200*SCALE_RATIO))
			
	def tick(self):
		self.interval=1
		if games.K_SPACE in self.keys and not self.frozen:
			self.interval=MISSILE_DELAY
			self.add_missile()

class Game(games.Text):
	def __init__(self, conn, num):
		games.Text.__init__(self, value='.', size=5, color=color.blue, x=-100, y=-100)
		
		self.conn=conn
		self.num=num
		self.missiles=[]
		
		self.p1, self.p2=Ship(1, self), Ship(2, self)
		
		games.screen.background=load_scaled_image(resource_path('res/bg.png'), transparent=False)
		games.music.load(resource_path('res/music.mp3'))
		games.music.play(-1)
		
		games.screen.add(self.p1)
		games.screen.add(self.p2)
		games.screen.add(self)
		
	def update(self):
		if not GAME_OVER:
			self.conn.send(str([i for i in (games.K_SPACE, games.K_RIGHT, games.K_LEFT, games.K_UP, games.K_DOWN) if games.keyboard.is_pressed(i)])+"|")
			
			info=full_recv(self.conn)
			
			if "end game" not in info:
				info=eval(info)
				self.p1.x, self.p1.y, self.p1.health, self.p1.angle, self.p2.x, self.p2.y, self.p2.health, self.p2.angle, missiles = info
			
				while len(self.missiles)!=len(missiles):
					if len(self.missiles)<len(missiles):
						missile=Missile(0,0,0,0)
						games.screen.add(missile)
						self.missiles.append(missile)
					else:
						self.missiles.pop().destroy()

				for i, v in enumerate(missiles):
					self.missiles[i].x, self.missiles[i].y, self.missiles[i].dx, self.missiles[i].dy=v
			else:
				games.screen.quit()
			
class Menu(games.Text):
	def __init__(self):
		games.Text.__init__(self, value=".", size=5, color=color.blue, x=-100, y=-100, interval=25)
		
		self.message=games.Text(value="Connecting to Server...", size=100, color=color.white, x=games.screen.width/2, y=games.screen.height/2)
		self.stage=0
		
		games.screen.add(self)
		games.screen.add(self.message)
		
		games.screen.mainloop()
		
	def tick(self):
		if self.stage==0:
			self.conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.conn.connect((SERVER_ADDRESS, 5000))
		
			self.num=int(full_recv(self.conn).split()[1])
			self.message.value="You are Player "+str(self.num)+"."
		
		elif self.stage==1:
			self.message.value="Waiting for Opponent..."
			full_recv(self.conn)
		
		else:
			self.message.destroy()
			self.destroy()
		
			Game(self.conn, self.num)
		
		self.stage+=1

def start_game():
	global SERVER_ADDRESS
	SERVER_ADDRESS=ip_enter.get()
	
	root.destroy()
	games.init(1600*SCALE_RATIO, 800*SCALE_RATIO, 50)
	
	menu=Menu()

def main():
	global ip_enter, root
	root=Tkinter.Tk()
	#root.geometry("500")
	Tkinter.Label(root, text="Type in the server's IP address: ").grid(column=0, row=0)
	ip_enter=Tkinter.Entry(root)
	ip_enter.grid(column=1, row=0)
	Tkinter.Button(root, text="Submit", command=start_game).grid(column=2, row=0)
	root.mainloop()
	
if __name__=="__main__":
	main()
