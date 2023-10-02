import json
import argparse
from datetime import datetime, timedelta


class Event:
    def __init__(self, timestamp: datetime, duration):
        self.timestamp = timestamp
        self.duration = duration

    # Fetches all the events in a file
    # And maps each one to an event
    @staticmethod
    def fetch_events(filename):
        # Import file to events list
        events_list = []

        with open(filename, 'r') as json_file:
            events_obj = json.loads(json_file.read())
            for event_obj in events_obj:
                events_list.append(Event(datetime.strptime(event_obj['timestamp'], '%Y-%m-%d %H:%M:%S.%f'),
                                         event_obj['duration']))

        return events_list

    # Computes the moving average for the provided file
    @staticmethod
    def moving_average(events, window_size, output_filename):
        # Getting the first and last events
        # The first one has to have the seconds reset for the desired output
        # The second one has to have 1 more minute
        begin = events[0].timestamp.replace(second=0)
        end = events[-1].timestamp + timedelta(minutes=1)
        right_bound = begin
        results = []

        while right_bound <= end:
            # Changes the left pointer according to the right one
            left_bound = right_bound - timedelta(minutes=window_size)

            # Gets all the events within the window and compute the average
            events_in_bounds = list(filter(lambda e: left_bound <= e.timestamp <= right_bound, events))
            moving_sum = sum(map(lambda event: event.duration, events_in_bounds))
            result = moving_sum / len(events_in_bounds) if len(events_in_bounds) > 0 else 0

            result = {"date": right_bound.strftime('%Y-%m-%d %H:%M:%S'), 'average_delivery_time': result}
            print(result)
            results.append(result)

            # Increases the right boundary
            right_bound += timedelta(minutes=1)

        # Saving the output to a json file
        with open(output_filename, "w") as json_file:
            json.dump(results, json_file, indent=2)


if __name__ == "__main__":
    # Parsing the arguments from console
    parser = argparse.ArgumentParser(description="Events Moving Average")
    parser.add_argument("--input_file", help="Input file to compute the average")
    parser.add_argument("--window_size", help="Window size")
    args = parser.parse_args()

    events = Event.fetch_events(args.input_file)
    Event.moving_average(events, int(args.window_size), "output/output.json")