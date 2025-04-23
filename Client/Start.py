from typing import Literal
import pygame as pg
import requests
from BaseClasses import Vector2,display_text,LINK
def start(screen:pg.Surface,*args)->tuple[pg.Surface,Literal["Quit","Play"],list[int]]:
    running = True
    screen.fill((0, 0, 0))
    selected = 0
    display_text(50,"Pinging all servers...",screen,(255,255,255),"Arial",top_left_pos=Vector2(0,0))
    pg.display.flip()
    print(f"{LINK}/games")
    response = requests.get(f"{LINK}/games",timeout=5)
    games = response.json()["data"]
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return screen,"Quit",[0]
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    selected = (selected - 1) % 8
                if event.key == pg.K_DOWN:
                    selected = (selected + 1) % 8
                if event.key == pg.K_RETURN:
                    return screen,"Play",[selected]
                if event.key == pg.K_ESCAPE:
                    return screen,"Quit",[0]
        screen.fill((0, 0, 0))
        display_text(40,"Press (ENTER) to select a server, Press (UP/DOWN ARROW) to change selection, Press"
                        "(ESCAPE) to QUIT",screen,(255,255,255),"Arial",top_left_pos=Vector2(0,0))
        for server_num,players in enumerate(games):
            background = None
            color = (255, 255, 255)
            if server_num == selected:
                background = (255, 255, 255)
                color = (0, 0, 0)
            display_text(36,f"Server {server_num} with {players} Players",screen,color,"Arial"
                         ,top_left_pos=Vector2(0,100+server_num*40), background=background)
        pg.display.flip()
    return screen,"Quit",[0]