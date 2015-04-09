from superwires import games
import math,os
from game_engine import *

class Player(Ship):
	def update(self):
		self.keys=[i for i in Ship.KEYS if games.keyboard.is_pressed(i)]
		Ship.update(self)

class Player2(Ship):
	TRANS={games.K_d: games.K_RIGHT, games.K_a: games.K_LEFT, games.K_w: games.K_UP, games.K_s: games.K_SPACE}
	
	def update(self):
		self.keys=[Player2.TRANS[i] for i in Player2.TRANS if games.keyboard.is_pressed(i)]
		Ship.update(self)

def main():
	games.init(1600*SCALE_RATIO, 850*SCALE_RATIO, 50)
	games.screen.background=load_scaled_image(resource_path('res/bg.png'), transparent=False)
	games.music.load(resource_path('res/music.mid'))
	games.music.play(-1)
	games.screen.add(Player(1))
	games.screen.add(Player2(2))
	games.screen.mainloop()

if __name__=='__main__':
	main()