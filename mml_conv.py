import sys


def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]


def argmin(iterable):
    return min(enumerate(iterable), key=lambda x: x[1])[0]


class TrackerState(object):
    def __init__(self, num_tracks):
        self.num_tracks = num_tracks
        self.positions = [0] * num_tracks
        self.measures = [0] * num_tracks
        self.multipliers = [1.] * num_tracks
        self.default_note_values = [4] * num_tracks
        self.time = [0] * num_tracks
        self.cur_tempo = 120
        self.volumes = [100] * num_tracks
        self.active_tracks = num_tracks


class AAConverter(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.num_tracks = len(tokens)
        self.event_counts = [len(i) for i in self.tokens]

    def process(self):
        ret_str = ''
        state = TrackerState(self.num_tracks)

        # add start and end times to each event
        while True:
            i = self.get_next_event_and_update_state(state)
            if not i:
                break
            print i
            print state.measures

        return ret_str

    def get_next_event_and_update_state(self, state):
        while state.active_tracks > 0:
            i = argmin(state.measures)
            if state.positions[i] >= self.event_counts[i]:
                state.positions[i] = sys.maxsize
                state.active_tracks -= 1
            else:
                break
        if not state.active_tracks > 0:
            return None

        event = self.tokens[i][state.positions[i]]
        state.positions[i] += 1
        state.measures[i] += self.get_event_note_value(event, state.default_note_values[i], state.multipliers[i])
        return event

    @staticmethod
    def get_event_note_value(event, default_note_value, default_note_multiplier):
        note_value = 0
        multiplier = 0
        if 'Note' in event:
            multiplier = 1.5 if 'note_dot' in event else default_note_multiplier
            note_value = event['note_note_value'] if 'note_note_value' in event else default_note_value
        elif 'R' in event:
            multiplier = 1.5 if 'rest_dot' in event else default_note_multiplier
            note_value = event['rest_note_value'] if 'rest_note_value' in event else default_note_value
        elif 'N' in event:
            multiplier = 1.5 if 'num_note_dot' in event else default_note_multiplier
            note_value = default_note_value
        return multiplier / int(note_value) if note_value else 0
