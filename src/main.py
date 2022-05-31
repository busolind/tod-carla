import os
import sys
import time
from copy import deepcopy
from datetime import datetime

import carla
import pygame
import yaml
from pathlib import Path

from src.FolderPath import FolderPath
from src.TeleConstant import FinishCode
from src.TeleOutputWriter import DataCollector
from src.TeleSimulator import TeleSimulator
from src.actor.InfoSimulationActor import SimulationRatioActor
from src.actor.TeleCarlaActor import TeleCarlaVehicle, TeleCarlaPedestrian
from src.actor.TeleMEC import TeleMEC
from src.actor.TeleOperator import TeleOperator
from src.actor.TeleCarlaSensor import TeleCarlaCollisionSensor
from src.args_parse import TeleConfiguration
from src.args_parse.TeleConfiguration import TeleConfiguration
from src.build_enviroment import create_sim_world, create_route, destroy_sim_world, create_data_collector, \
    create_network_topology, create_display
from src.carla_bridge.TeleWorld import TeleWorld
from src.TeleWorldController import BehaviorAgentTeleWorldController, KeyboardTeleWorldController, \
    BasicAgentTeleWorldController
import src.utils as utils


def main(simulation_conf, scenario_conf):
    """
    get configurations for simulation:
    - carla_server_file (default: configuration/default_server.yaml),
    - carla_simulation_file(default: configuration/default_simulation_curve.yaml)
    """
    clock = pygame.time.Clock()
    client, sim_world = create_sim_world(simulation_conf['host'], simulation_conf['port'], simulation_conf['timeout'],
                                         scenario_conf['world'],
                                         simulation_conf['seed'],
                                         simulation_conf['synchronicity'],
                                         simulation_conf['timing'][
                                             'time_step'] if 'timing' in simulation_conf and 'time_step' in
                                                             simulation_conf['timing'] else None)

    tele_world: TeleWorld = TeleWorld(client, simulation_conf['synchronicity'])

    start_transform, destination_location = create_route(tele_world, scenario_conf)
    controller = BehaviorAgentTeleWorldController('normal', start_transform.location, destination_location)

    # ACTORS
    pedestrian = TeleCarlaPedestrian('127.0.0.1', utils.find_free_port(),
                                     carla.Location(x=376, y=-1.990084, z=0.001838))

    player_attrs = {'role_name': 'hero'}
    player = TeleCarlaVehicle('127.0.0.1', utils.find_free_port(), simulation_conf['synchronicity'], 0.05,
                              scenario_conf['vehicle_player'],
                              player_attrs,
                              start_transform=start_transform,
                              modify_vehicle_physics=True)

    collisions_sensor = TeleCarlaCollisionSensor()
    player.attach_sensor(collisions_sensor)

    tele_operator = TeleOperator('127.0.0.1', utils.find_free_port(), controller)
    mec_server = TeleMEC('127.0.0.1', utils.find_free_port())

    create_network_topology(simulation_conf['synchronicity'], scenario_conf, player, mec_server, tele_operator)

    tele_sim = TeleSimulator(tele_world, clock)

    if simulation_conf['render'] or simulation_conf['controller']['type'] == 'manual':
        create_display(player, clock, tele_sim, simulation_conf['camera']['width'], simulation_conf['camera']['height'])

    data_collector = create_data_collector(tele_world, player)
    tele_sim.add_actor(mec_server)
    tele_sim.add_actor(tele_operator)
    tele_sim.add_actor(data_collector)
    tele_sim.add_actor(SimulationRatioActor(1))
    tele_sim.add_actor(pedestrian)
    tele_sim.add_actor(player)

    controller.add_player_in_world(player)

    anchor_points = controller.get_trajectory()

    optimal_trajectory_collector = DataCollector(FolderPath.OUTPUT_RESULTS_PATH + 'optimal_trajectory.csv')
    optimal_trajectory_collector.write('location_x', 'location_y', 'location_z')
    # for point in anchor_points:
    #     optimal_trajectory_collector.write(point['x'], point['y'], point['z'])

    try:
        status_code = tele_sim.do_simulation(simulation_conf['synchronicity'])

        finished_status_sim = {
            FinishCode.ACCIDENT: 'ACCIDENT',
            FinishCode.OK: 'FINISH',
        }[status_code]
    except Exception as e:
        finished_status_sim = 'ERROR'
        raise e
    finally:
        destroy_sim_world(client, sim_world)
        pygame.quit()
        with open(FolderPath.OUTPUT_RESULTS_PATH + 'finish_status.txt', 'w') as f:
            f.write(finished_status_sim)


def parse_configurations(carla_simulation_config_path, carla_scenario_config_path):
    res = TeleConfiguration(carla_simulation_config_path, carla_scenario_config_path)

    return res


if __name__ == '__main__':
    configuration = TeleConfiguration(sys.argv[1], sys.argv[2])

    simulation_conf = configuration['carla_simulation_file']
    scenario_conf = configuration['carla_scenario_file']

    FolderPath.CURRENT_SIMULATION_DIRECTORY_PATH = scenario_conf['delay']['backhaul']['uplink_extra_delay'][
                                                       'family'] + '_' + '_'.join(
        str(v) for v in
        scenario_conf['delay']['backhaul']['uplink_extra_delay']['parameters'] \
            .values()) + '|' + datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    Path(scenario_conf['output']['results']).mkdir(parents=True, exist_ok=True)
    Path(scenario_conf['output']['log']).mkdir(parents=True, exist_ok=True)

    FolderPath.OUTPUT_RESULTS_PATH = scenario_conf['output'][
                                         'results'] + FolderPath.CURRENT_SIMULATION_DIRECTORY_PATH + '/'
    FolderPath.OUTPUT_LOG_PATH = scenario_conf['output']['log'] + FolderPath.CURRENT_SIMULATION_DIRECTORY_PATH + '/'

    os.mkdir(FolderPath.OUTPUT_RESULTS_PATH)
    os.mkdir(FolderPath.OUTPUT_LOG_PATH)
    os.mkdir(FolderPath.OUTPUT_RESULTS_PATH + 'configurations/')

    with open(FolderPath.OUTPUT_RESULTS_PATH + 'configurations/carla_simulation_file.yaml', 'w') as outfile:
        yaml.dump(simulation_conf, outfile, default_flow_style=False)
    with open(FolderPath.OUTPUT_RESULTS_PATH + 'configurations/carla_scenario_file.yaml', 'w') as outfile:
        yaml.dump(scenario_conf, outfile, default_flow_style=False)

    main(simulation_conf, scenario_conf)
