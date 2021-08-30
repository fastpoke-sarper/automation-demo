import argparse
from config import Config
from datetime import datetime, timedelta, timezone
import time

from events import Database
from app_service import open_meet, open_zoom
from constants import ZOOM, MEET, CONFIG_FILE_NAME
from google_calendar_service import GoogleCalendar
from setup import setup



CHECK_FREQUENCY_SECONDS = 60




def check_calendar(database_directory: str):
    """
    One of the two main functions of this program is to check the Google Calendar service for upcoming meetings
    
    this method encapsulates several methods to accomplish this
    """
    
    google_calendar = GoogleCalendar()
    events = google_calendar.get_all_events()
    
    

    database = Database(database_directory)
    
    database.delete_non_opened_events()
    database.add_events(events)
    
    
def open_events(database_directory: str, open_prior_to_event_minutes: int, use_zoom: bool=False, use_meet: bool=False, zoom_bin: str=None, browser_bin: str=None):
    
    """
    The other main function of this program is to opent the necessary meeting program (either Google Meet through Chrome or Zoom in this case)
    """
    
    database = Database(database_directory)
    
    
    now = datetime.now(timezone.utc)
    
    min_time = now.astimezone()
    max_time = (now + timedelta(minutes=open_prior_to_event_minutes)).astimezone()
    
    
    events = database.get_events(min_time, max_time)
    
    
    for event in events:
        if use_zoom and event.service == ZOOM and not event.opened: 
            open_zoom(event.url, zoom_bin)
            print('Event opened on Zoom: ', event.name)
        if use_meet and event.service == MEET and not event.opened: 
            open_meet(event.url, browser_bin)
            print('Event opened on Google Meet: ', event.name)
        
        database.set_event_as_opened(event)



    
    
    

def main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--setup', action='store_true')
    args = parser.parse_args()
    
    do_setup = args.setup


    # TODO: Add command line argument to get custom config file directory
    
    try:
        f = open(CONFIG_FILE_NAME)
        f.close()
    except FileNotFoundError:
        print('Config file not found. Starting setup.')
        do_setup = True
    
        
        
    
    
    config = None
    
    database_directory = None
    zoom_bin = None
    browser_bin = None
    open_prior_to_event_minutes = None
    use_zoom = False
    use_meet = False
    
    if(do_setup): 
        config = setup()
        
        
        
    if not config:
        
        config = Config()
        config.load_from_file(CONFIG_FILE_NAME)
        
      

    database_directory = config.CONFIG['database_directory']
    zoom_bin = config.CONFIG['zoom_bin']
    browser_bin = config.CONFIG['browser_bin']
    open_prior_to_event_minutes = config.CONFIG['open_prior_to_event_minutes']
    use_zoom = config.CONFIG['use_zoom']
    use_meet = config.CONFIG['use_meet']
        
    
    
    
    
    
    
    
    
    print('Enjoy your meetings!')
    
    while(True):  # Explain issue with cron. This had to be a service-like program
    
        try:
            check_calendar(database_directory)
            print('Checked calendar')
        except Exception as e: # TODO: more sophisticated exception handling
            print('Error in calendar check: ', str(e))
        
        
        
        try:
            open_events(database_directory, open_prior_to_event_minutes, use_zoom, use_meet, zoom_bin, browser_bin)
            print('Checked to see if any events needs to be opened')
        except Exception as e:
            print('Error in opening of meeting service: ', str(e))

        time.sleep(CHECK_FREQUENCY_SECONDS)
    

    return 0


if __name__ == '__main__':
    
    code = main()
    
    print('Terminated with ' + ('success.' if code == 0 else 'error code: ' + str(code)))
    
    
    