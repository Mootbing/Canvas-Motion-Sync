from src import iCalGrabber, MotionBridge
import time
import datetime

grabber = iCalGrabber.iCalGrabber()
motion = MotionBridge.MotionBridge()

if (grabber.load_calendar()):
    events = grabber.get_events()
    already_existing_events = motion.get_tasks()
    
    for event in events:

        if (event.summary in [task['name'] for task in already_existing_events]):
            print(f"Task for event already exists")

            existing = already_existing_events[[task['name'] for task in already_existing_events].index(event.summary)]

            if (existing['completed']):
                print(f"Task for event is already completed")
                continue

            parsed_due_date = datetime.datetime.fromisoformat(existing['dueDate'][:-1])
            parsed_due_date = parsed_due_date.replace(tzinfo=datetime.timezone.utc)

            if (event.end > parsed_due_date):
                print(f"Updating task for event: {event.summary}")
                motion.update_deadline(
                    event=existing,
                    due_date=event.end.isoformat()
                )
            else:
                print(f"Skipping...")
            continue

        yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)

        if (event.end < yesterday):
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