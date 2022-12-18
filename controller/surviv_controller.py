import pygame
import json
import requests

class Controller(object):

    def __init__(self):
        self.game_over = False
        self.p_name = None

    def initialize(self, p_name, p_rect, m_width):
        self.game_over = False
        self.p_name = p_name
        game_dict = {
            "p_name": p_name, 
            "p_left": p_rect.left,
            "p_top": p_rect.top, 
            "p_width": p_rect.width, 
            "p_height": p_rect.height,
            "m_width": m_width
        }
        url = "http://127.0.0.1:8080/init"
        r = requests.post(url, json.dumps(game_dict))

    def remove_player(self):
        url = "http://127.0.0.1:8080/remove_player"
        p_dict = { "name": self.p_name }
        r = requests.post(url, json.dumps(p_dict))

    def set_player(self, x, y):
        pos = {
            "name": self.p_name,
            "x": x,
            "y": y
        }
        url = "http://127.0.0.1:8080/set_player"
        r = requests.post(url, json.dumps(pos))

    def change_player_speed(self, x, y):
        url = "http://127.0.0.1:8080/change_player_speed"
        pos = {
            "name": self.p_name, 
            "change_x": x,
            "change_y": y
        }
        r = requests.post(url, json.dumps(pos))

    def move_player(self):
        url = "http://127.0.0.1:8080/move_player"
        p_dict = { "name": self.p_name }
        r = requests.post(url, json.dumps(p_dict))

    def get_positions(self):
        url = "http://127.0.0.1:8080/get_positions"
        p_dict = { "name": self.p_name }
        r = requests.post(url, json.dumps(p_dict))
        return r.json()

    @staticmethod
    def process_welcome_events(rect, events):
        done = 0
        for event in events:
            if event.type == pygame.QUIT:
                done = 1
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if rect.left < pos[0] < rect.right and rect.top < pos[1] < rect.bottom:
                    done = 2  # Play Solo button pressed.
        return done

    def process_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.change_player_speed(-5, 0)
                if event.key == pygame.K_RIGHT:
                    self.change_player_speed(5, 0)
                if event.key == pygame.K_UP:
                    self.change_player_speed(0, -5)
                if event.key == pygame.K_DOWN:
                    self.change_player_speed(0, 5)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.change_player_speed(5, 0)
                if event.key == pygame.K_RIGHT:
                    self.change_player_speed(-5, 0)
                if event.key == pygame.K_UP:
                    self.change_player_speed(0, 5)
                if event.key == pygame.K_DOWN:
                    self.change_player_speed(0, -5)

        self.move_player()
        return False
