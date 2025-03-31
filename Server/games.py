from os import urandom
from Server.Vector2 import Vector2, Boundary
from time import time, time_ns
from hashlib import scrypt
from math import floor
from typing import Any
ARCHIVE_TIME = 10
QUIT_TIME = 90


class Game:
    def __init__(self,boundary:Boundary,*, start_position:Vector2 = None):
        self.players: list[Player] = []
        self.boundary:Boundary = boundary
        if start_position is None:
            start_position = Vector2(0,0)
        self.start_position:Vector2 = start_position
        self.last_iteration = time_ns()
    def player_join(self,name:str)-> int:
        self.iterate()
        if len(self.players) >= 10:
            return 0
        for player in self.players:
            if player.name == name:
                raise ValueError(f"Player name '{name}' is already taken")
        private_session_token = int.from_bytes(urandom(8))
        player = Player(name, private_session_token, self.start_position)
        self.players.append(player)
        return private_session_token
    def player_update(self, submitted_token:int, position:Vector2, velocity:Vector2):
        self.iterate()
        updated = False
        for player in self.players:
            if submitted_token in player.hash_token():
                player.client_update(position, velocity)
                updated = True
                break
        if not updated:
            raise LookupError(f"The player with hash_token {submitted_token} cannot be found in any player")
    def get_game_data(self, *, excluded_names:list[str] | str):
        self.iterate()
        if isinstance(excluded_names, str):
            excluded_names = [excluded_names]
        game_data: list[dict[str,Any]] = []
        for player in self.players:
            if player.name in excluded_names:
                continue
            game_data.append({
                'name': player.name,
                'position': player.position.to_list(),
               'velocity': player.velocity.to_list(),
                'archived': player.archived
            })
        return game_data
    def player_leave(self,submitted_token:int):
        self.iterate()
        found = False
        for n,player in enumerate(self.players):
            if submitted_token in player.hash_token():
                self.players.pop(n)
                found = True
                break
        if not found:
            raise LookupError(f"The player with hash_token {submitted_token} cannot be found in any player")
    def iterate(self):
        current_time = time_ns()
        delta_time = (current_time - self.last_iteration) / 10**9
        self.last_iteration = current_time
        to_remove = []
        for n,player in enumerate(self.players):
            if not player.iterate(delta_time, self.boundary):
                to_remove.append(n)
        for n in reversed(to_remove):
            self.players.pop(n)
    def poll(self):
        self.iterate()
        return len(self.players)



class Player:
    def __init__(self, name, private_session_token:int, start_position: Vector2):
        self.name = name
        self.private_session_token = private_session_token
        self.position = start_position
        self.velocity = Vector2(0,0)
        self.last_connect_time = time()
        self.archived = False
    def client_update(self, position:Vector2, velocity:Vector2):
        self.last_connect_time = time()
        self.position = position
        self.velocity = velocity
        self.archived = False
    def iterate(self,delta_time:float,boundary:Boundary):
        if time()-self.last_connect_time > ARCHIVE_TIME:
            self.archived = True
        elif time()-self.last_connect_time > QUIT_TIME:
            return False
        else:
            self.position += self.velocity * delta_time
            if not boundary.contains(self.position):
                self.position = boundary.clamp(self.position)
        return True
    def hash_token(self)-> [int,int]:
        correct_time = floor(time())
        alt_time = correct_time - 1
        salt = str(correct_time).encode()
        alt_salt = str(alt_time).encode()
        key = str(self.private_session_token).encode()
        hash_one = scrypt(key, salt=salt, n=16384, r=8, p=1, dklen=32)
        hash_two = scrypt(key, salt=alt_salt, n=16384, r=8, p=1, dklen=32)
        return [int.from_bytes(hash_one), int.from_bytes(hash_two)]


