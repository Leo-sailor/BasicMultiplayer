import asyncio
from time import time_ns
from typing import Literal
import pygame as pg
from requests import Response
from Client.BaseClasses import IP, PORT, Vector2, gen_token,basic_boundary
from aiohttp import ClientSession, ClientResponse
from random import randrange
import requests
from Client.ViewportManager import ViewportManager


class ObjectHolder:
    def __init__(self, val):
        self.value = val
    def set_value(self,new_val):
        self.value = new_val
    def get_value(self):
        return self.value
    def __getitem__(self, item):
        return self.value[item]
    def __setitem__(self, key, value):
        self.value[key] = value
    def __iter__(self):
        return iter(self.value)
def play(screen:pg.Surface,server_num:int)->tuple[Literal["Quit","Start"],list[int]]:
    assert isinstance(server_num, int)
    return asyncio.run(play_async(screen,server_num))

async def play_async(screen:pg.Surface,server_num:int)->tuple[Literal["Quit","Start"],list[int]]:
    name = "Player" + str(randrange(0,1000))
    response: Response = requests.post(f'http://{IP}:{PORT}/{server_num}/join/{name}')
    json:dict = response.json()
    try:
        assert response.status_code == 201
    except:
        raise ConnectionError
    code = json.get('private_code')
    others_state = ObjectHolder([])
    client_state = ObjectHolder([Vector2(0,0),Vector2(0,0)])
    runners = [asyncio.create_task(ui(screen,others_state,client_state)),
               asyncio.create_task(sender(server_num,code,client_state)),
               asyncio.create_task(receiver(server_num, name, others_state))]
    main,waiting = await asyncio.wait(runners,return_when=asyncio.FIRST_COMPLETED)
    for task in waiting:
        task.cancel()
    result = "Quit",0
    for task in main:
        result = task.result()
    return result
async def sender(server_num: int,private_code:int,client_state:ObjectHolder)->tuple[Literal["Quit","Start"],list[int]]:
    async with ClientSession() as session:
        error_count = 0
        while error_count<100:
            velocity:Vector2 = client_state[0]
            velx = velocity.x
            vely = velocity.y
            position:Vector2 = client_state[1]
            posx = position.x
            posy = position.y
            token = gen_token(private_code)
            response = await session.put(f"http://{IP}:{PORT}/{server_num}/update/{token}/{velx},{vely}/{posx},{posy}")
            json = await response.json()
            if response.status != 200:
                print("ERROR: Failed to send position to server")
                print(f"Request: http://{IP}:{PORT}/{server_num}/update/{token}/{velx},{vely}/{posx},{posy}")
                print(f"Response: {response.status}, {json}")
                error_count += 1
    return "Quit",[0]

async def receiver(server_num, name, others_state:ObjectHolder)->tuple[Literal["Quit", "Start"],list[int]]:
    async with ClientSession() as session:
        error_count = 0
        while error_count<100:
            response:ClientResponse = await session.get(f"http://{IP}:{PORT}/{server_num}/get/{name}")
            json:dict = await response.json()
            try:
                assert response.status == 200
            except AssertionError:
                print("ERROR: Failed to send position to server")
                print(f"Request: http://{IP}:{PORT}/{server_num}/get/{name}")
                print(f"Response: {response.status}, {json}")
                error_count += 1
            else:
                others_state.set_value(json['data'])
    return "Quit",[0]
async def ui(screen:pg.Surface,others_state,client_state) -> tuple[Literal["Quit","Start"],list[int]]:
    viewport = ViewportManager(screen,basic_boundary,Vector2(0,0))
    last_time = time_ns()
    while True:
        current_time = time_ns()
        delta_time = (current_time - last_time) / 10**9
        last_time = current_time
        speed = abs(client_state[0])
        direction = client_state[0].direction()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "Quit",[0]
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return "Start",[1]
        keys = pg.key.get_pressed()
        if keys[pg.K_UP] or keys[pg.K_w]:
            speed += 100 * delta_time
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            speed -= 100 * delta_time
            speed = 0 if speed<0 else speed
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            direction -= 180 * delta_time
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            direction += 180 * delta_time
        if keys[pg.K_EQUALS]:
            viewport.adjust_zoom(1+ 1*delta_time)
        if keys[pg.K_MINUS]:
            viewport.adjust_zoom(1-(1*delta_time))
        screen.fill((0, 0, 0))
        viewport.render_background()
        client_state[0] = Vector2.from_dir_mag(direction, speed)
        client_state[1] = basic_boundary.clamp(client_state[1] + (client_state[0] * delta_time))
        viewport.update_viewport_center(client_state[1], client_state[0])
        for i,player in enumerate(others_state):
            velocity = Vector2(player['velocity'][0],player['velocity'][1])
            position = Vector2(player['position'][0],player['position'][1])
            new_position = position + velocity * delta_time
            player['position'] = new_position.tup()
            others_state[i] = player
            color = (127,127,127) if player['archived'] else (255,255,255)
            viewport.render_ball(30,color,player['name'],new_position)
        viewport.render_ball(30,(255,255,255),'You',client_state[1])
        pg.display.flip()
        await asyncio.sleep(0.01)