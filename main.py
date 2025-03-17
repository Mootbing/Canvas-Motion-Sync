from src import iCalGrabber, MotionHandler
import time
import datetime

grabber = iCalGrabber.iCalGrabber()
motion = MotionHandler.MotionHandler()

if (grabber.load_calendar()):
    events = grabber.get_events()
    
    for event in events:

        if (event.end < datetime.datetime.now(datetime.timezone.utc)):
            continue

        print(f"Creating task for event: {event.summary}")

        time.sleep(10) #12 req/min rate limit

        try:
            motion.create_task(
                name=event.summary,
                workspace_id=motion.workspace_id,
                due_date=event.end.isoformat(),
                description=event.get_detailed_desc()
            )
        except Exception as e:
            print(f"Status: {e}")