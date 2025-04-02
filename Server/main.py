from fastapi import FastAPI, Response,status
from games import Game
from Vector2 import basic_boundary as bb, Vector2
from time import time

app = FastAPI()
games: list[Game] = [Game(bb), Game(bb), Game(bb), Game(bb), Game(bb), Game(bb), Game(bb), Game(bb)]


@app.get("/")
async def root():
    return {"message": "Hi, You have reached Leo's A-Level computer science projects server, for docs, go to /docs, "
                       "for ping, go to /ping, for a parrot test function go to /test"}


@app.get("/ping")
async def ping():
    return {"message": "pong", "Server Time (epoch)": time()}


@app.get("/test/{data}")
async def test(data: str):
    return {"message": f"{data}", "Server Time (epoch)": time()}


@app.post("/{game_num}/join/{name}", status_code=201)
async def join_game(game_num: int, name: str,response:Response):
    if 0 <= game_num < len(games):
        code = games[game_num].player_join(name)
        starting_position = games[game_num].start_position.tup()
        boundary = games[game_num].boundary
        if code == 0:
            response.status_code = status.HTTP_409_CONFLICT
            return {"message": f"Game {game_num} is full, Please try again Later"}
        return {"message": f"Player {name} successfully joined game {game_num}", "private_code": code,
                "start_position": starting_position,"boundary":{boundary}}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Invalid game number"}


@app.delete("/{game_num}/leave/{token}", status_code=205)
async def leave_game(game_num: int, token: int, response:Response):
    if 0 <= game_num < len(games):
        try:
            games[game_num].player_leave(token)
            return {"message": f"Player left game {game_num}"}
        except LookupError as lookup_error:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": f"Invalid token , Error: {lookup_error.args}"}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Invalid game number"}

@app.put("/{game_num}/update/{token}/{velx},{vely}/{posx},{posy}",status_code=200)
async def update_game(game_num: int, token: int, velx: float, vely: float, posx: float, posy: float,response:Response):
    if 0 <= game_num < len(games):
        try:
            velocity = Vector2(velx, vely)
            position = Vector2(posx, posy)
            games[game_num].player_update(token, velocity, position)
            return {"message": f"Player {token} updated their position in game {game_num}"}
        except LookupError as lookup_error:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": f"Invalid token, Error: {lookup_error.args}"}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Invalid game number"}


@app.get("/{game_num}/get/{excluded_names}",status_code=200)
async def get_game_state(game_num: int, excluded_names: str | None,response:Response):
    if isinstance(excluded_names, str):
        excluded_names = [excluded_names]
    if 0 <= game_num < len(games):
        return {"message": f"Game data delivered excluding {excluded_names}",
                "data": games[game_num].get_game_data(excluded_names=excluded_names)}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Invalid game number"}


@app.get("/games")
async def get_all_games():
    return {"message": "All games current players", "data": [game.poll() for game in games]}
