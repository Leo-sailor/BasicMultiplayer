import traceback
from Client.BaseClasses import display_multi_line_text
from Server.Vector2 import Vector2
from Start import start
from Play import play
from os import linesep
import time
import pygame as pg
from pygame.locals import RESIZABLE
WHITE = (255,255,255)
GREEN = (0,255,0)
def error_screen(error:Exception, display:pg.Surface):
    display.fill((0, 0, 0))
    text = (f"There has been a major error, Press (ENTER) to restart app, "
            f"Press (ESCAPE) to quit{linesep}App will Automatically close in 1 minute{linesep}"
            f"Error Details:{linesep}"+ str(error))
    display_multi_line_text(20, text,display,(255,30,30),top_left_pos=Vector2(0,0))
    print(text)
    print(traceback.print_tb(error.__traceback__))
    pg.display.flip()
    for _ in range(0,int(60/0.1)):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "Quit",[0]
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return "Start",[0]
                elif event.key == pg.K_ESCAPE:
                    return "Quit",[0]
        time.sleep(0.1)
    return "Quit",[0]
def f_quit(display, code, *args):
    pg.quit()
    exit(code)

def setup_screen():
    scale_factor = 80
    screen_rect = pg.Rect(0, 0, 16 * scale_factor, 9 * scale_factor)
    windows_style = RESIZABLE
    best_color_depth = pg.display.mode_ok(screen_rect.size, windows_style, 32)
    new_screen = pg.display.set_mode(screen_rect.size, windows_style, best_color_depth)
    pg.display.set_caption("Pygame Window")
    pg.mouse.set_visible(True)
    new_screen.fill((255, 255, 255))
    return new_screen

pg.init()
screen = setup_screen()
mode = "Start"
func = f_quit
modes = {"Start": start,
         "Play": play,
         "Quit":f_quit}
data = [0]
while True:
    try:
        func = modes[mode]
    except KeyError:
        mode = ModuleNotFoundError(f"The {mode} tier 1 game mode has not been found")
    try:
        mode,data = func(screen,*data)
    except Exception as e:
        mode = e
    if isinstance(mode,Exception) or issubclass(type(mode),Exception):
        try:
            mode,data = error_screen(mode,screen)
        except Exception as e:
            print(f"A Fatal error occurred while trying to catch another error:{e}\nQuitting now:")
            f_quit(1)

