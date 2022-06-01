from datetime import datetime
import os
from pathlib import Path
from typing import Type


class FolderPath:
    PROJECT_PATH = ''.join(map(lambda x: x + '/', os.path.abspath(__file__).split('/')[:-2]))
    SRC_PATH = PROJECT_PATH + 'src/'

    OUTPUT_RESULTS_PATH = None
    OUTPUT_LOG_PATH = None
    OUTPUT_IMAGES_PATH = None

    def __new__(cls: Type):
        raise Exception("Can't create instance of this class")



