from BaseClasses import Vector2, Boundary,display_text
ZERO_VEC = Vector2(0, 0)
import pygame as pg
class ViewportManager:
    def __init__(self,display:pg.Surface,boundary:Boundary,starting_position:Vector2):
        self.game_boundary = boundary
        self.screen_boundary = Boundary(display.get_width(),0,display.get_height,0)
        self.center = starting_position
        self.zoom = 3
        self.screen = display
    def update_viewport_center(self,player_position:Vector2,player_velocity:Vector2):
        self.check_zoom()
        self.center = player_position - (player_velocity*0.5)
        if not self.check_if_screen_coord_is_inside_game(ZERO_VEC):
            bad_game_coord = self.screen_coords_to_game_coords(ZERO_VEC)
            self.center -= self.game_boundary.boundary_to_outside_point(bad_game_coord)
        elif not self.check_if_screen_coord_is_inside_game(Vector2(self.screen.get_width(),self.screen.get_height())):
            bad_game_coord = self.screen_coords_to_game_coords(Vector2(self.screen.get_width(),self.screen.get_height()))
            self.center -= self.game_boundary.boundary_to_outside_point(bad_game_coord)
    def adjust_zoom(self,amount):
        self.zoom *= amount
        self.check_zoom()
    def check_zoom(self):
        horizontal_zoom_min = self.screen.get_width() / self.game_boundary.get_width()
        vertical_zoom_min = self.screen.get_height() / self.game_boundary.get_height()
        zoom_min = max(horizontal_zoom_min, vertical_zoom_min)
        if self.zoom <= zoom_min:
            self.zoom = zoom_min
        if self.zoom >= 100:
            self.zoom = 100
    def game_coords_to_screen_coords(self,game_coords:Vector2):
        screen_coords = (game_coords - self.center) * self.zoom
        screen_coords.y = -screen_coords.y
        screen_coords += Vector2(self.screen.get_width() / 2,self.screen.get_height() / 2)
        screen_coords.round()
        return screen_coords
    def screen_coords_to_game_coords(self,game_coords:Vector2):
        screen_coords = game_coords - Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        screen_coords /= self.zoom
        screen_coords.y = -screen_coords.y
        screen_coords += self.center
        return screen_coords
    def check_if_point_is_inside_viewport(self,point:Vector2):
        screen_coords = self.game_coords_to_screen_coords(point)
        return self.screen_boundary.contains(screen_coords)
    def check_if_screen_coord_is_inside_game(self,coord:Vector2):
        game_coords = self.screen_coords_to_game_coords(coord)
        return self.game_boundary.contains(game_coords)
    def render_ball(self,radius:float|int,color:tuple[int,int,int],name:str,center:Vector2):
        screen_coords = self.game_coords_to_screen_coords(center)
        pg.draw.circle(self.screen, color, screen_coords.x, screen_coords.y, round(radius*self.zoom))
        display_text(16,name,self.screen,(0,0,0),center_pos=screen_coords)
