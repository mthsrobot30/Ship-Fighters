import socket, threading, sys, time
from game_engine import *

def relay(sender, to):
	while True:
		x=full_recv(sender, 4096)
		if x=="end game":
			print "releasing thread"
			return
		try:
			to.send(x+'|')
		except:
			print "releasing thread"
			return

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", int(sys.argv[1])))
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

	p1_thread=threading.Thread(target=relay, args=(player1, player2))
	p2_thread=threading.Thread(target=relay, args=(player2, player1))
	p1_thread.daemon=p2_thread.daemon=True
	p1_thread.start()
	p2_thread.start()