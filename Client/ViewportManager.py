import random
from BaseClasses import Vector2, Boundary,display_text
import pygame as pg
ZERO_VEC = Vector2(0, 0)
class ViewportManager:
    def __init__(self,display:pg.Surface,boundary:Boundary,starting_position:Vector2):
        self.game_boundary = boundary
        self.screen_boundary = Boundary(display.get_width(),0,display.get_height(),0)
        self.center = starting_position
        self.zoom = 3
        self.screen = display
    def update_viewport_center(self,player_position:Vector2,player_velocity:Vector2):
        if not(isinstance(player_position,Vector2) and isinstance(player_velocity,Vector2)):
            raise ValueError("Both player_position and player_velocity must be Vector2 instances.")
        self.check_zoom()
        self.center = player_position - (player_velocity*0.5)
        if not self.check_if_screen_coord_is_inside_game(ZERO_VEC):
            bad_game_coord = self.screen_coords_to_game_coords(ZERO_VEC)
            self.center -= self.game_boundary.boundary_to_outside_point(bad_game_coord)
        elif not self.check_if_screen_coord_is_inside_game(Vector2(self.screen.get_width(),self.screen.get_height())):
            bad_game_coord = self.screen_coords_to_game_coords(Vector2(self.screen.get_width(),self.screen.get_height()))
            self.center -= self.game_boundary.boundary_to_outside_point(bad_game_coord)
    def adjust_zoom(self, scale_factor):
        self.zoom *= scale_factor
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
    def screen_coords_to_game_coords(self,game_coords:Vector2)-> Vector2:
        screen_coords = game_coords - Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        screen_coords /= self.zoom
        screen_coords.y = -screen_coords.y
        screen_coords += self.center
        return screen_coords
    def check_if_point_is_inside_viewport(self,point:Vector2)-> bool:
        screen_coords = self.game_coords_to_screen_coords(point)
        return self.screen_boundary.contains(screen_coords)
    def check_if_screen_coord_is_inside_game(self,coord:Vector2) -> bool:
        game_coords = self.screen_coords_to_game_coords(coord)
        return self.game_boundary.contains(game_coords)
    def render_ball(self,radius:float|int,color:tuple[int,int,int],name:str,center:Vector2):
        screen_coords = self.game_coords_to_screen_coords(center)
        if screen_coords in self.screen_boundary:
            pg.draw.circle(self.screen, color, [screen_coords.x, screen_coords.y], round(radius*self.zoom))
            display_text(16,name,self.screen,(0,0,0),center_pos=screen_coords)

    def render_background(self):
        for x in range(self.game_boundary.min_x,self.game_boundary.max_x,round(self.game_boundary.get_width()/50)):
            for y in range(self.game_boundary.min_y,self.game_boundary.max_y,round(self.game_boundary.get_height()/50)):
                screen_coords = self.game_coords_to_screen_coords(Vector2(x,y))
                if screen_coords in self.screen_boundary:
                    pg.draw.circle(self.screen, (100,0,200),[screen_coords.x,screen_coords.y],3)
if __name__ == "__main__":
    class Mock:
        def __init__(self):
            pass

        def get_width(self):
            return 800

        def get_height(self):
            return 600
    mock_display = Mock()
    boundary = Boundary(1000, 0, 1000, 0)
    starting_position = Vector2(500, 500)
    viewport_manager = ViewportManager(mock_display, boundary, starting_position)


    viewport_manager.center = Vector2(0, 0)
    viewport_manager.zoom = 1

    game_coords = Vector2(-100, -200)
    screen_coords = viewport_manager.game_coords_to_screen_coords(game_coords)
    expected_coords = Vector2(300, 500)
    assert screen_coords == expected_coords
    print("test 1 passed")

    game_coords = Vector2(0,0)
    screen_coords = viewport_manager.game_coords_to_screen_coords(game_coords)
    expected_coords = Vector2(400, 300)
    assert screen_coords == expected_coords
    print("test 2 passed")
    for x in range(0,100):
        game_coords = Vector2((random.random()-0.5)*2000,(random.random()-0.5)*2000)
        screen_coords = viewport_manager.game_coords_to_screen_coords(game_coords)
        new_game_coords = viewport_manager.screen_coords_to_game_coords(screen_coords)
        print(new_game_coords,game_coords)
        assert abs(new_game_coords - game_coords)<=0.71
        print(f"test {x+3} passed")
    for x in range(0,100):
        screen_coords = Vector2((random.random()-0.5)*2000,(random.random()-0.5)*2000)
        screen_coords.round()
        game_coords = viewport_manager.screen_coords_to_game_coords(screen_coords)
        new_screen_coords = viewport_manager.game_coords_to_screen_coords(game_coords)
        print(new_screen_coords,screen_coords)
        assert new_screen_coords == screen_coords
        print(f"test {x+103} passed")