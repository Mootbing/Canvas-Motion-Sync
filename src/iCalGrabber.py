import os
from datetime import datetime, timezone, timedelta
import requests
from icalendar import Calendar
from dotenv import load_dotenv
from pathlib import Path

class Event:
    def __init__(self, uid, summary, description, start, end, location=None, url=None, created=None, last_modified=None):
        self.uid = uid
        self.summary = summary
        self.description = description
        self.start = start
        self.end = end
        self.location = location
        self.url = url
        self.created = created
        self.last_modified = last_modified
        
    def __str__(self):
        return f"{self.summary} ({self.start:%Y-%m-%d %H:%M} - {self.end:%Y-%m-%d %H:%M})"
    
    def get_detailed_desc(self):
        return f"""
{self.start} - {self.end}
{self.url or ''}
{self.location or ''}
{self.description}
"""
    
    def get_details(self):
        return f"""
{self.summary}
{self.get_detailed_desc()}
ID: {self.uid}
"""
    
    def __repr__(self):
        return self.__str__()

def load_calendar_url():
    dotenv_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path)
    
    calendar_url = os.getenv("CANVAS_ICAL_LINK")
    if not calendar_url:
        raise ValueError("CANVAS_ICAL_LINK not found in .env file")
    
    return calendar_url

def fetch_calendar_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch calendar data: Status code {response.status_code}")
    
    return response.text

def parse_ical_data(ical_data):
    cal = Calendar.from_ical(ical_data)
    events = []
    
    for component in cal.walk():
        if component.name == "VEVENT":
            uid = str(component.get('uid', ''))
            summary = str(component.get('summary', ''))
            description = str(component.get('description', ''))
            
            dtstart = component.get('dtstart')
            dtend = component.get('dtend')
            
            if not dtstart or not dtend:
                continue
                
            start = dtstart.dt
            end = dtend.dt
            
            if isinstance(start, datetime) and start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if isinstance(end, datetime) and end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            
            location = str(component.get('location', '')) or None
            url = str(component.get('url', '')) or None
            
            created = None
            if component.get('created'):
                created = component.get('created').dt
                
            last_modified = None
            if component.get('last-modified'):
                last_modified = component.get('last-modified').dt
            
            event = Event(
                uid=uid,
                summary=summary,
                description=description,
                start=start,
                end=end,
                location=location,
                url=url,
                created=created,
                last_modified=last_modified
            )
            events.append(event)
            
    return events

class iCalGrabber:
    def __init__(self):
        self.events = []
        self.calendar_url = None
        
    def load_calendar(self):
        try:
            self.calendar_url = load_calendar_url()
            ical_data = fetch_calendar_data(self.calendar_url)
            self.events = parse_ical_data(ical_data)
            return True
        except Exception as e:
            print(f"Error loading calendar: {e}")
            return False
    
    def get_events(self):
        return self.events
    
    def get_upcoming_events(self, days=7):
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days)
        
        upcoming = []
        for event in self.events:
            if now <= event.start <= future:
                upcoming.append(event)
        
        return upcoming

def main():
    grabber = iCalGrabber()
    if (grabber.load_calendar()):
        events = grabber.get_events()
        print(f"== Found {len(events)} events ==")
        
        for event in events:
            print(event.get_details())
    
if __name__ == "__main__":
    main()