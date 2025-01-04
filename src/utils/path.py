#Class to store paths for all data folders
import os
import sys

class Path:
    #Can use outputs from sys.path to get the root directory
    #https://stackoverflow.com/questions/73699282/how-to-get-the-path-of-a-sub-folder-under-root-directory-of-the-project
    repo_dir = sys.path[4]
    data_dir = os.path.join(repo_dir, 'data')
    step_1 = os.path.join(data_dir, 'step_1')
    step_2 = os.path.join(data_dir, 'step_2')