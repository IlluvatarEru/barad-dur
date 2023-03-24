"""
The variable used to resolve all paths, typically this will be set in a launch script by doing the below:

import os
import sys
from core import root_folder

dir_path = os.path.dirname(os.path.realpath(__file__))
root_folder.ROOT_FOLDER = dir_path + '/../' # modify to get to the right place

"""
global ROOT_FOLDER

ROOT_FOLDER_LINUX = '/home/dev/'
ROOT_FOLDER_WINDOWS = 'C:/dev/'
