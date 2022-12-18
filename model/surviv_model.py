import pygame
import random
import json
import bottle

class GameInterface(object):
    def __init__(self, g_dict):
        self.game = Game(g_dict['p_name'], pygame.Rect(g_dict['p_left'], g_dict['p_top'], g_dict['p_width'], g_dict['p_height']), g_dict['m_width'])

    def add_player(self, g_dict):
        self.game.add_player(g_dict['p_name'], pygame.Rect(g_dict['p_left'], g_dict['p_top'], g_dict['p_width'], g_dict['p_height']))

    def remove_player(self, pname_dict):
    	return self.game.remove_player(pname_dict['name'])

    def set_player(self, ppos_dict):
        self.game.get_player(ppos_dict['name']).startpos(ppos_dict['x'], ppos_dict['y'])

    def update_redzone_pos(self):
        self.game.redzone.update_redzone_pos()

    def get_redzone_pos(self):
        return self.game.redzone.get_redzone_pos()

    def get_player_pos(self, pname_dict):
        return self.game.get_player_pos(pname_dict['name'])

    def is_player_in_redzone(self, pname_dict):
        return self.game.is_player_in_redzone(pname_dict['name'])

    def change_player_speed(self, pspeed_dict):
        self.game.change_player_speed(pspeed_dict['name'], pspeed_dict['change_x'], pspeed_dict['change_y'])

    def move_player(self, pname_dict):
        self.game.move_player(pname_dict['name'])

    def move_player_pos(self, p_dict):
        self.game.move_player_pos(p_dict['name'], p_dict['change_x'], p_dict['change_y'])


class Game(object):
    def __init__(self, p_name, p_rect, m_width):
        self.players = [Player(p_name, p_rect)]
        self.redzone = Redzone(m_width)

    def add_player(self, p_name, p_rect):
        self.players.append(Player(p_name, p_rect))

    def remove_player(self, name):
        for p in self.players:
            if p.name == name:
                self.players.remove(p)

    def get_player(self, name):
        for p in self.players:
            if p.name == name:
                return p
        return None

    def update_redzone_pos(self):
        self.redzone.update_redzone_pos()

    def get_redzone_pos(self):
        return self.redzone.get_redzone_pos()

    def set_player(self, name, x, y):
        self.get_player(name).startpos(x, y)

    def get_player_pos(self, name):
        return self.get_player(name).get_player_pos()

    def change_player_speed(self, name, x, y):
        self.get_player(name).changespeed(x, y)

    def move_player(self, name):
        x = self.get_player(name).change_x
        y = self.get_player(name).change_y
        if self.will_player_collide(name, x, y):
            return
        self.get_player(name).move()

    def move_player_pos(self, name, x, y):
        if self.will_player_collide(name, x, y):
            return
        self.get_player(name).move_pos(x, y)

    def will_player_collide(self, name, x, y):
        p_rect = self.get_player_pos(name)
        l1x = p_rect.left + x
        l1y = p_rect.top + y
        r1x = l1x + p_rect.width
        r1y = l1y + p_rect.height
        for p in self.players:
            l2x = p.rect.left
            l2y = p.rect.top
            r2x = l2x + p.rect.width
            r2y = l2y + p.rect.height
            if p.name != name and self.do_overlap(l1x, l1y, r1x, r1y, l2x, l2y, r2x, r2y):
                return True
        return False

    def do_overlap(self, l1x, l1y, r1x, r1y, l2x, l2y, r2x, r2y):
#        print("do_overlap: ",l1x,l1y,r1x,r1y,": 2nd rect: ",l2x,l2y,r2x,r2y)
        # If one rectangle is on left side of other 
        if l1x > r2x or l2x > r1x: 
            return False
        # If one rectangle is above other 
        if r1y < l2y or r2y < l1y:
            return False 
        return True    

    def is_player_in_redzone(self, name):
        p_rect = self.get_player_pos(name)
        r_rect = self.get_redzone_pos()
        if p_rect.left > r_rect.left and p_rect.right < r_rect.right \
                and p_rect.top > r_rect.top and p_rect.bottom < r_rect.bottom:
            return True
        return False


class Redzone(object):
    def __init__(self, m_width):
        self.max_width = m_width
        self.rect = pygame.Rect(m_width, random.randrange(0, 400),
                                random.randrange(300, 1500), random.randrange(200, 1000))

    def get_redzone_pos(self):
        return self.rect

    def update_redzone_pos(self):
        self.rect.centerx -= 20
        if self.rect.left < 0:
            self.rect.width -= 20
            if self.rect.width < 0:
                self.rect.left = self.max_width
                self.rect.width = random.randrange(300, 1500)
                self.rect.height = random.randrange(200, 1000)
                self.rect.top = random.randrange(0, 400)


class Player(object):
    def __init__(self, name, p_rect):
        # set speed vector
        self.change_x = 0
        self.change_y = 0
        self.name = name
        self.rect = p_rect

    def get_player_pos(self):
        return self.rect

    def startpos(self, x, y):
        # Make our top-left corner the passed-in location.
        self.rect.x = x
        self.rect.y = y

    def changespeed(self, x, y):
        self.change_x += x
        self.change_y += y

    def move(self):
        # Move left/right
        self.rect.x += self.change_x
        # Move up/down
        self.rect.y += self.change_y

    def move_pos(self, x, y):
        self.rect.x += x
        self.rect.y += y


game_interface = None

@bottle.hook('after_request')
def enable_cors():
    bottle.response.headers['Access-Control-Allow-Origin'] = '*'

@bottle.post('/init')
def do_init():
    global game_interface
    content = bottle.request.body.read().decode()
    content = json.loads(content)
    if game_interface == None:
        game_interface = GameInterface(content)
    else:
        game_interface.add_player(content)
    return json.dumps(True)

@bottle.post('/remove_player')
def do_remove_player():
    if game_interface == None:
        return json.dumps(False)
    content = bottle.request.body.read().decode()
    pname_dict = json.loads(content)
    game_interface.remove_player(pname_dict)
    return json.dumps(True)

@bottle.post('/set_player')
def do_set_player():
    if game_interface == None:
        return json.dumps(False)
    content = bottle.request.body.read().decode()
    ppos_dict = json.loads(content)
    game_interface.set_player(ppos_dict)
    return json.dumps(True)

@bottle.post('/change_player_speed')
def do_change_player_speed():
    if game_interface == None:
        return json.dumps(False)
    content = bottle.request.body.read().decode()
    pspeed_dict = json.loads(content)
    game_interface.change_player_speed(pspeed_dict)
    return json.dumps(True)

@bottle.post('/move_player')
def do_move_player():
    if game_interface == None:
        return json.dumps(False)
    content = bottle.request.body.read().decode()
    pname_dict = json.loads(content)
    game_interface.move_player(pname_dict)
    return json.dumps(True)

@bottle.post('/get_positions')
def do_get_positions():
    if game_interface == None:
        return json.dumps(None)
    content = bottle.request.body.read().decode()
    pname_dict = json.loads(content)
    p_rect = game_interface.get_player_pos(pname_dict)
    game_interface.update_redzone_pos()
    r_rect = game_interface.get_redzone_pos()
    op_positions = []
    for p in game_interface.game.players:
        if p.name != pname_dict['name']:
            o_dict = { "o_left": p.rect.left, "o_top": p.rect.top, "o_width": p.rect.width, "o_height": p.rect.height }
            op_positions.append(o_dict)
    a_dict = {
        "p_left": p_rect.left,
        "p_top": p_rect.top, 
        "p_width": p_rect.width, 
        "p_height": p_rect.height,
        "r_left": r_rect.left,
        "r_top": r_rect.top, 
        "r_width": r_rect.width, 
        "r_height": r_rect.height,
        "b_in_redzone": game_interface.is_player_in_redzone(pname_dict), 
        "op_positions": op_positions
    }
    return json.dumps(a_dict)

@bottle.post('/get_new_position')
def do_get_new_position():
    if game_interface == None:
        return json.dumps(None)
    content = bottle.request.body.read().decode()
    p_pos = json.loads(content)
    game_interface.move_player_pos(p_pos)
    pname_dict = {
        "name": p_pos['name']
    }
    p_rect = game_interface.get_player_pos(pname_dict)
    p_dict = {
        "p_left": p_rect.left,
        "p_top": p_rect.top, 
        "p_width": p_rect.width, 
        "p_height": p_rect.height,
    }
    return json.dumps(p_dict)

bottle.run(host='127.0.0.1', port=8080)
#bottle.run(host='127.0.0.1', port=8080, quiet=True)
#bottle.run(host='127.0.0.1', port=8080, debug=True)
