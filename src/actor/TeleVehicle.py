import random
import sys
from abc import ABC, abstractmethod

import carla
from carla import ActorBlueprint, Transform, Location, Rotation

from src.utils.utils import need_member


class TeleVehicle:

    def __init__(self, actor_filter, actor_id, attrs, start_position=None, modify_vehicle_physics=False):
        self._actor_filter = actor_filter
        self._actor_id = actor_id
        self._attrs = attrs
        self._start_position = start_position
        self.model = None
        self._show_vehicle_telemetry = False
        self._modify_vehicle_physics = modify_vehicle_physics

    def receive_instruction(self, command):
        # self.appl
        ...
    @need_member('model')
    def __getattr__(self, *args):
        return self.model.__getattribute__(*args)

    def spawn_in_world(self, map, world):

        blueprint: ActorBlueprint = random.choice(world.get_blueprint_library().filter(self._actor_filter))
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)

        if blueprint.has_attribute('speed'):
            self.player_max_speed = float(blueprint.get_attribute('speed').recommended_values[1])
            self.player_max_speed_fast = float(blueprint.get_attribute('speed').recommended_values[2])

        for key, value in self._attrs.items():
            blueprint.set_attribute(key, value)

        self.model = None
        if self._start_position is not None:
            self.model = world.try_spawn_actor(blueprint, self._start_position)
            if self.model is None:
                print("Error in spawning car in:", self._start_position)

        while self.model is None:
            if not map.get_spawn_points():
                print('There are no spawn points available in your map/town.')
                print('Please add some Vehicle Spawn Point to your UE4 scene.')
                sys.exit(1)
            spawn_points = map.get_spawn_points()
            spawn_point = spawn_points[1]
            # spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            # x=29.911945, y=-2.026154, z=0.000000
            # spawn_point = Transform(Location(x=299.399994, y=133.240036, z=0.300000), Rotation(pitch=0.000000, yaw=-0.000092, roll=0.000000))
            self.model = world.try_spawn_actor(blueprint, spawn_point)
            if self._modify_vehicle_physics:
                self.modify_vehicle_physics()
        self.set_light_state(carla.VehicleLightState.Position)

    def modify_vehicle_physics(self):
        try:
            physics_control = self.get_physics_control()
            physics_control.use_sweep_wheel_collision = True
            self.apply_physics_control(physics_control)
        except Exception:
            pass
