
import json
import os

import constants

class Config():
    
    FILE_PATH = '.'
    CONFIG = {}
    
    
    def __init__(self) -> None:
        pass
    
    def load_from_file(self, file_path: str='.') -> dict:
        self.FILE_PATH = file_path
        
        with open(self.FILE_PATH) as config_file:
            loaded_config_file = json.load(config_file)
            self.CONFIG['database_directory'] = loaded_config_file['database_directory']
            self.CONFIG['zoom_bin'] = loaded_config_file['zoom_bin']
            self.CONFIG['browser_bin'] = loaded_config_file['browser_bin']
            self.CONFIG['open_prior_to_event_minutes'] = loaded_config_file['open_prior_to_event_minutes']
            self.CONFIG['use_zoom'] = loaded_config_file['use_zoom']
            self.CONFIG['use_meet'] = loaded_config_file['use_meet']
            
        return self.CONFIG
        
    
    def setup_config(self, root_directory: str, config_file_name: str, database_name: str, use_zoom: bool, use_meet: bool, zoom_bin: str=None, browser_bin: str= None, open_prior_to_event_minutes: int=5, file_path: str='.'):
        
        self.FILE_PATH = root_directory
        
        database_directory = os.path.join(root_directory, database_name)
    
        self.CONFIG = {
            'root_directory': root_directory,
            'use_zoom': use_zoom,
            'use_meet': use_meet,
            'zoom_bin': constants.DEFAULT_ZOOM_BIN if not zoom_bin else zoom_bin,
            'browser_bin': constants.DEFAULT_BROWSER_BIN if not browser_bin else browser_bin,
            'database_directory': database_directory,
            'open_prior_to_event_minutes': open_prior_to_event_minutes
            
        }
        
        
        with open(os.path.join(root_directory, config_file_name), 'w+') as json_data_file:
            json.dump(self.CONFIG, json_data_file)
    