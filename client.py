from superwires import games
import threading,socket,sys
from Tkinter import *
from game_engine import *

SERVER_ADDRESS="SolarSailor"
over=False

class Player(Ship):
	def update(self):
		self.keys=[i for i in Ship.KEYS if games.keyboard.is_pressed(i)]
		self.conn.send(str(self.keys)+', |')
		Ship.update(self)

class Game(object):
	def __init__(self):
		self.conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((SERVER_ADDRESS, 5000))
		
		print "Connecting to Server..."
		num=int(full_recv(self.conn).split()[1])
		print "You are Player "+str(num)
		print "Waiting for Opponent..."
		full_recv(self.conn)
		print "Starting Game..."
		
		games.init(1600, 800, 50)
		
		self.player=Player(num)
		self.player.conn=self.conn
		self.opponent=Ship(1 if num==2 else 2)
		
		thread=threading.Thread(target=self.opponent_thread)
		thread.daemon=True
		thread.start()
		
		games.screen.background=games.load_image(resource_path('res/bg.png'), transparent=False)
		games.music.load(resource_path('res/music.mid'))
		games.music.play(-1)
		
		games.screen.add(self.player)
		games.screen.add(self.opponent)
		
		games.screen.mainloop()
		global over
		over=True
		sys.exit(1)
		
	def opponent_thread(self):
		while not over:
			msg=full_recv(self.conn, 4096)
			print msg
			self.opponent.keys=eval('['+msg+']')[-1]

def main():
	Game()

if __name__=="__main__":
	main()