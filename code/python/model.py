import math
import pygame
import pymunk
from collections import OrderedDict # for keeping the order in which dictionaries were created
from random import gauss
from pygame.locals import *
from pymunk import Vec2d

# WARNING: pygame and pymunk have reverse labeling conventions along the Y axis.
# For pymunk the top is higher values and for pygame the top is lower values. Be
# aware when interpreting coordinates.

class MarbleWorld():

    # world constants
    full_length = 800
    full_height = 600
    marble_size = 60
    speed = 200        # scales how fast marbles are moving
    step_size = 1/50   # in seconds
    time_max = 15      # in seconds
    step_max = math.floor(time_max / step_size) # stop animation after time_max time has passed
    max_framerate = 100
    velocity_noise = 0.05 # standard deviation

    # user-defined collision types for pymunk
    collision_types = {
        'static': 0,
        'dynamic': 1
    }

    wall_thickness = 20
    exit_portion = 1/3  # what portion of the left side marbles can exit through
    exit_position = (wall_thickness / 2, full_height / 2)
    default_walls = [
        {'name': 'top_wall', 'position': (full_length / 2, full_height - wall_thickness / 2),
         'length': full_length, 'height': wall_thickness, 'color': 'black'},
        {'name': 'bottom_wall', 'position': (full_length / 2, wall_thickness / 2),
         'length': full_length, 'height': wall_thickness, 'color': 'black'},
        {'name': 'top_left_wall', 'position': (wall_thickness / 2, full_height * (1 - (1 - exit_portion) / 4)),
         'length': wall_thickness, 'height': full_height * (1 - exit_portion) / 2, 'color': 'black'},
        {'name': 'bottom_left_wall', 'position': (wall_thickness / 2, full_height * (1 - exit_portion) / 4),
         'length': wall_thickness, 'height': full_height * (1 - exit_portion) / 2, 'color': 'black'},
        {'name': 'exit', 'position': exit_position, 'length': wall_thickness,
         'height': full_height * exit_portion, 'color': 'red'}
    ]


    ### world initialization ###

    @classmethod
    def pymunk_to_pygame(cls, x, y, length=0, height=0):
        return (int(x - length/2), int(cls.full_height - y - height/2))

    # note that we always work with squared distance
    @classmethod
    def exit_dist(cls, pos):
        return (cls.exit_position[0] - pos[0])**2 + (cls.exit_position[1] - pos[1])**2


    def __init__(self, marbles={}, extra_walls=[], gate=False,
                 path_record_bodies=[], outcome_record_bodies=[]):
        self.step = 0
        self.space = pymunk.Space()
        self.events = {'collisions': [],
                       'wall_bounces': [],
                       'outcome': {},
                       'outcome_dists': {}} # used to record events
        # containers for bodies, shapes, and sprites, keyed by name
        # a body is a collection of shapes rigidly held together; in our case,
        # each body has only one shape, and is visualized as one sprite
        self.bodies = OrderedDict()
        self.shapes = OrderedDict()
        self.sprites = OrderedDict()

        self.path_record_bodies = path_record_bodies
        self.outcome_record_bodies = outcome_record_bodies

        # add walls
        self.walls = self.default_walls + extra_walls
        for wall in self.walls:
            if wall['name'] != 'exit':
                self.add_wall(wall['position'], wall['length'], wall['height'], wall['name'])
        for mname in marbles:
            marble = marbles[mname]
            self.add_marble(tuple(marble['position']), marble['velocity'], mname, marble['delay'], marble['noisy'])

        # setup collision handlers
        handler_dynamic = self.space.add_collision_handler(self.collision_types['dynamic'], self.collision_types['dynamic'])
        handler_dynamic.begin = self.marble_collision
        handler_dynamic = self.space.add_collision_handler(self.collision_types['dynamic'], self.collision_types['static'])
        handler_dynamic.begin = self.wall_collision


    def marble_collision(self, arbiter, space, data):
        self.events['collisions'].append({
            'objects': (arbiter.shapes[0].body.name, arbiter.shapes[1].body.name),
            'step': self.step
        })
        return True

    def wall_collision(self, arbiter, space, data):
        self.events['wall_bounces'].append({
            'objects': (arbiter.shapes[0].body.name, arbiter.shapes[1].body.name),
            'step': self.step
        })
        return True

    def add_wall(self, position, length, height, name):
        body = pymunk.Body(body_type = pymunk.Body.STATIC)
        body.position = position
        body.name = name

        wall = pymunk.Poly.create_box(body, size=(length, height))
        wall.elasticity = 1
        # wall.name = name
        wall.collision_type = self.collision_types['static']
        self.space.add(wall)
        return wall

    def add_marble(self, position, velocity, name, delay, noisy):
        body = pymunk.Body()

        shape = pymunk.Circle(body, self.marble_size/2)
        shape.elasticity = 1
        shape.friction = 0
        shape.mass = 1
        shape.collision_type = self.collision_types['dynamic']

        body.position = position
        body.angle = 0
        body.name = name

        self.space.add(body, shape)
        self.bodies[name] = body
        self.shapes[name] = shape

        # this function is called at every step (the default function is update_velocity)
        def delayed_velocity(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, damping, dt)
            if self.step == delay:
                body.apply_impulse_at_local_point([x*self.speed for x in velocity])
            if self.step == noisy:
                body.velocity = body.velocity[0]*gauss(1, self.velocity_noise), body.velocity[1]*gauss(1, self.velocity_noise)
        body.velocity_func = delayed_velocity

        return (body, shape)
        
    ### animation ###

    def animation_setup(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.full_length, self.full_height))
        pygame.display.set_caption("Marble World")
        self.pic_count = 0 # used for saving images
        for bname in self.bodies:
            self.sprites[bname] = pygame.image.load(self.image_path.format(bname))

    def animation_step(self):
        # quit conditions
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                animate = False

        if len(self.save_frames) == 0 or self.pic_count in self.save_frames:
            # draw screen, background and bodies
            self.screen.fill((255,255,255))
            for wall in self.walls:
                x, y = self.pymunk_to_pygame(*wall['position'], wall['length'], wall['height'])
                pygame.draw.rect(self.screen, pygame.Color(wall['color']), pygame.Rect(x, y, wall['length'], wall['height']))
            for bname in self.bodies:
                self.update_sprite(bname)

            # update the screen
            pygame.display.flip()
            self.clock.tick(self.max_framerate)

            if len(self.save_frames) != 0:
                pygame.image.save(self.screen, self.save_dir.format(self.pic_count))

        self.pic_count += 1

    def update_sprite(self, bname):
        body = self.bodies[bname]
        p = Vec2d(self.pymunk_to_pygame(body.position.x, body.position.y))
        angle_degrees = math.degrees(body.angle)
        rotated_shape = pygame.transform.rotate(self.sprites[bname], angle_degrees)
        offset = Vec2d(rotated_shape.get_size()) / 2.
        p = p - offset
        self.screen.blit(rotated_shape, p) # blit draws an image


    ### world simulation ###

    def simulate(self, image_path, save_dir, save_frames, animate):
        self.image_path = image_path
        self.save_dir = save_dir
        self.save_frames = save_frames

        paths = {}
        for bname in self.path_record_bodies:
            paths[bname] = {'position': [], 'velocity': []}
        outcome_dists = self.events['outcome_dists']
        for bname in self.outcome_record_bodies:
            outcome_dists[bname] = self.full_length**2

        # animation setup
        if animate:
            self.animation_setup()
            self.animation_step()
            pygame.time.wait(1000)

        while self.step <= self.step_max:
            # save the position and velocity for each body on the recording list
            for bname in self.path_record_bodies:
                paths[bname]['position'].append(self.bodies[bname].position)
                paths[bname]['velocity'].append(self.bodies[bname].velocity)

            # remember the minimum distance between exit and marble(s) on outcome list
            for bname in self.outcome_record_bodies:
                d = self.exit_dist(self.bodies[bname].position)
                if d < outcome_dists[bname]:
                    outcome_dists[bname] = d

            self.space.step(self.step_size)
            self.step += 1
            if animate:
                self.animation_step()

        for bname in self.outcome_record_bodies:
            if self.bodies[bname].position[0] > -self.marble_size/2:
                self.events['outcome'][bname] = False
            else:
                self.events['outcome'][bname] = True
        ## double check collisions are in temporal order and return
        # collisions = self.events['collisions']
        # assert all([collisions[i]['step'] <= collisions[i+1]['step'] for i in range(len(collisions) - 1)])
        pygame.quit()
        return (self.events, paths)
