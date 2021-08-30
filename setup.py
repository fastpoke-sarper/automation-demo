from config import Config
import os
import json

from constants import DATABASE_NAME, CONFIG_FILE_NAME
from events import Database


def setup_config_file() -> str:
    ROOT_DIRECTORY = '.'
    USE_ZOOM = True
    ZOOM_BIN = None
    USE_MEET = True
    BROWSER_BIN = None
    OPEN_PRIOR_TO_EVENT_MINUTES = 5
    
    
    print('Setup for automated readiness of video conferences:')
    print('Enter root for source files, including your credentials for Google Calendar (enter for default):')
    user_input = input()
    ROOT_DIRECTORY = user_input if user_input else ROOT_DIRECTORY
    print('Open Zoom meetings? (y/n)')
    user_input = input()
    USE_ZOOM = True if user_input in ['y', 'yes', 'Y', 'YES'] else False
    if(USE_ZOOM):
        print('Specify Zoom executable directory (enter for system default):')
        user_input = input()
        if user_input: ZOOM_BIN = user_input
    print('Open Google Meet meetings? (y/n)')
    user_input = input()
    USE_MEET = True if user_input in ['y', 'yes', 'Y', 'YES'] else False
    if(USE_MEET):
        print('Specify browser executable directory? (enter for system default)')
        user_input = input()
        if user_input: BROWSER_BIN = user_input
    print('How many minutes prior should your meetings open? (enter for default: 5 min)')
    user_input = input()
    OPEN_PRIOR_TO_EVENT_MINUTES = int(user_input) if user_input else OPEN_PRIOR_TO_EVENT_MINUTES
        
    print('Make sure cron is running! Enjoy your meetings!')
    
    
    
    config = Config()
    
    config.setup_config(ROOT_DIRECTORY, CONFIG_FILE_NAME, DATABASE_NAME, USE_ZOOM, USE_MEET, ZOOM_BIN, BROWSER_BIN, OPEN_PRIOR_TO_EVENT_MINUTES)

    return config




def create_database(database_directory: str):
    
    database = Database(database_directory)
    database.initiate_database()
    
    


def setup():
    config = setup_config_file()
    create_database(config.CONFIG['database_directory'])
           
    return config

