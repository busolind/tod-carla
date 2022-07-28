import os
from typing import Type


class FolderPath:
    PROJECT_PATH = ''.join(map(lambda x: x + '/', os.path.abspath(__file__).split('/')[:-2]))
    SRC_PATH = PROJECT_PATH + 'src/'

    CONFIGURATION_PATH = PROJECT_PATH + 'configuration/'
    CONFIGURATION_ACTORS = CONFIGURATION_PATH + 'actor/'
    CONFIGURATION_AGENTS = CONFIGURATION_PATH + 'agent/'

    OUTPUT_RESULTS_PATH = None
    OUTPUT_LOG_PATH = None
    OUTPUT_IMAGES_PATH = None

    def __new__(cls: Type):
        raise Exception("Can't create instance of this class")



