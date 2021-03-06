import socket
import socketserver
import threading

class Player:
    def __init__(self, id, ip, nickname, x=0, y=0, hp=100):
        self.nickname = nickname
        self.id = id
        self.ip = ip

        self.x = 0
        self.x_rate = 5
        self.y = 0
        self.y_rate = 5
        self.hp = 100

class GameInstance:
    def __init__(self):
        self.counter = -1
        self.players = {}
        self.ids_to_ips = {}
        self.ips_to_ids = {}
    
    def ping(self, s):
        b = bytes("b", "utf-8")
        return bytes(b+s)
    
    def join(self, s, ip):
        self.counter += 1
        #for i in self.players.keys():
        #    if self.players[i].ip == ip:
        if ip in self.ips_to_ids.keys():
            return bytes("jr%s" % self.ips_to_ids[ip], "utf-8")
        self.players.update({self.counter: Player(self.counter, ip, s)})
        self.ids_to_ips.update({self.counter: ip})
        self.ips_to_ids.update({ip: self.counter})
        return bytes("jc%s" % self.players[self.counter].id, "utf-8")

    def disconnect(self, ip):
        try:
            temp_id = self.ips_to_ids[ip]
            del self.ips_to_ids[ip]
            del self.ids_to_ips[temp_id]
            del self.players[temp_id]
            return bytes("dc%s" % temp_id, "utf-8")
        except ValueError:
            pass
        return bytes("dr", "utf-8")

    def update_pos(self, s, ip):
        print(s)
        try:
            pos = str(s, "utf-8").split(",")
            id_ = self.ips_to_ids[ip]
            self.players[id_].x = int(pos[0])
            self.players[id_].y = int(pos[1])
            return bytes("pc", "utf-8")+s
        except KeyError:
            pass
        return bytes("pr", "utf-8")+s

class Handler(socketserver.BaseRequestHandler):
    game = GameInstance()
    def handle(self):
        try:
            while True:
                self.data = self.request.recv(64)
                print("%s's data: " % self.client_address[0])
                print("\t%s" % self.data)
                modifier = self.data[0]
                only_data = self.data[1:]
                print(modifier, only_data)
               #ping
                if modifier == 97:
                    x = self.game.ping(only_data)
                    print(x)
                    self.request.sendall(x)
               #join
                if modifier == 106:
                    x = self.game.join(only_data, self.client_address[0])
                    print(x)
                    self.request.sendall(x)
                #disconnect
                if modifier == 100:
                    x = self.game.disconnect(self.client_address[0])
                    print(x)
                    self.request.sendall(x)
                #pos
                if modifier == 112:
                    x = self.game.update_pos(only_data, self.client_address[0])
                    print(x)
                    self.request.sendall(x)
        except IndexError:
            pass
        print("Disconnected from %s" % self.client_address[0])
        ##send the same shit, just upped
        #self.request.sendall(self.data.upper())

if __name__ == "__main__":
    host, port = "localhost", 9999
    server = socketserver.TCPServer((host, port), Handler)
    server.serve_forever()