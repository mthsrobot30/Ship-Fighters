import socket, threading, sys, time
from superwires import games, color
import Tkinter, os, math

from game_engine import *

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
		#MISSILE_SOUND.play()
	
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
			
	def tick(self):
		self.interval=1
		if games.K_SPACE in self.keys and not self.frozen:
			self.interval=MISSILE_DELAY
			self.add_missile()

class Game(games.Text):
	def __init__(self, p1, p2):
		games.Text.__init__(self, value=".", size=5, color=color.blue, x=-100, y=-100)
		
		self.p1_conn, self.p2_conn=p1, p2
		self.p1, self.p2=Ship(1, self), Ship(2, self)
		self.missiles=[]
		
		[games.screen.add(i) for i in self.p1, self.p2, self]
		
		games.screen.mainloop()
	
	def update(self):
		info=[self.p1.x, self.p1.y, self.p1.health, self.p1.angle, self.p2.x, self.p2.y, self.p2.health, self.p2.angle, [(missile.x, missile.y, missile.dx, missile.dy) for missile in self.missiles]]
			
		self.p1_conn.send(str(info)+"|")
		self.p2_conn.send(str(info)+"|")

		p1_info=full_recv(self.p1_conn)
		p2_info=full_recv(self.p2_conn)
		
		if "end game" in p1_info:
			self.p2_conn.send("end game")
			games.screen.quit()
		
		elif "end game" in p2_info:
			self.p1_conn.send("end game")
			games.screen.quit()
			
		else:
			self.p1.keys, self.p2.keys=eval(p1_info), eval(p2_info)
	

def relay(p1, p2):
	games.init(1600*SCALE_RATIO, 900*SCALE_RATIO, 50, True)
	game=Game(p1, p2)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", 5000))
server.listen(5)

while True:
	player1,address=server.accept()
	player1.send("player 1|")
	print "first"
	player2,address=server.accept()
	player2.send("player 2|")
	print "second"

	player1.send("start|")
	player2.send("start|")
	print "start"

	game_thread=threading.Thread(target=relay, args=(player1, player2))
	game_thread.daemon=True
	game_thread.start()
