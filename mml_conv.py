"""
There is a useful reddit post describing the differences here:
https://www.reddit.com/r/archebards/comments/3bwgj7/howto_fix_archeagemml_desyncs/
"""

import sys


def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]


def argmin(iterable):
    return min(enumerate(iterable), key=lambda x: x[1])[0]


class TrackerState(object):
    """
    Holds all the variables that can be change through MML.
    Tempo in 3MLE is shared between all tracks, but it is per-track in AA.
    We use the 3MLE behavior, and will update tempo in all channels manually.
    """

    def __init__(self, num_tracks):
        self.num_tracks = num_tracks
        self.positions = [0] * num_tracks
        self.measures = [0] * num_tracks
        self.multipliers = [1.] * num_tracks
        self.default_note_values = [4] * num_tracks
        self.octaves = [4] * num_tracks
        self.time = [0] * num_tracks
        self.tempo = 120
        self.volumes = [100] * num_tracks
        self.active_tracks = num_tracks


class AAConverter(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.num_tracks = len(tokens)
        self.event_counts = [len(i) for i in self.tokens]
        self.state = TrackerState(self.num_tracks)
        self.new_tokens = [[] for _i in xrange(self.num_tracks)]

    def process(self):
        ret_str = ''

        # add start and end times to each event
        while True:
            i = self.get_next_event_and_update_state(self.state)
            if not i:
                break
            print i
            print self.state.measures

        return ret_str

    def get_next_event_and_update_state(self, state):
        i = 0
        while state.active_tracks > 0:
            i = argmin(state.measures)
            if state.positions[i] >= self.event_counts[i]:
                state.measures[i] = sys.maxsize
                state.active_tracks -= 1
            else:
                break
        if not state.active_tracks > 0:
            return None

        event = self.tokens[i][state.positions[i]]
        if self.is_control_event(event):
            self.process_control_event(event, i)
        else:
            self.process_note_event(event, i)
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

    @staticmethod
    def is_control_event(event):
        return not ('Note' in event or 'R' in event or 'N' in event)

    def process_control_event(self, event, i):
        state = self.state
        assert self.is_control_event(event)
        if 'O' in event:
            state.octaves[i] = event['octave']
        elif 'octave_shift' in event:
            change = 1 if event['octave_shift'] == '>' else -1
            state.octaves[i] += change
        elif 'volume_shift' in event:
            change = 1 if event['volume_shift'] == ')' else -1
            state.volumes[i] += change
            # convert to volume event
            event['V'] = 'v'
            event['volume'] = str(state.volumes[i])
            event['volume_127'] = self.convert_volume(state.volumes[i])
        elif 'T' in event:
            state.tempo = event['tempo']
        elif 'V' in event:
            new_volume = int(event['volume'])
            state.volumes[i] = new_volume
            event['volume'] = str(new_volume)
            event['volume_127'] = self.convert_volume(int(event['volume']))
        elif 'L' in event:
            state.multipliers[i] = 1.5 if 'default_note_dot' in event else 1.
            state.default_note_values[i] = event['default_note_value']

        self.new_tokens[i] += [event]
        state.positions[i] += 1

    def process_note_event(self, event, i):
        state = self.state
        assert not self.is_control_event(event)
        # TODO: create multiple eventsfor numbered notes and dotted rests.
        if 'N' in event:
            octave = state.octaves[i]

        self.new_tokens[i] += [event]
        state.positions[i] += 1
        state.measures[i] += self.get_event_note_value(event, state.default_note_values[i], state.multipliers[i])

    @staticmethod
    def convert_volume(volume):
        """
        the volume in 3MLE is 0 to 15, but 0 to 127 in AA as in:
        https://www.reddit.com/r/archebards/comments/3bwgj7/howto_fix_archeagemml_desyncs/cu5gizt
        :param volume:
        :return:
        """
        return int(round(volume * (127. / 15.)))

    def __str__(self):
        str_ret = ''
        for track in self.new_tokens:
            for event in track:
                str_ret += self.event_to_string(event)
            str_ret += ','
        return str_ret

    @staticmethod
    def event_to_string(event):
        str_ret = ''
        if 'Note' in event:
            if 'extend_note' in event:
                str_ret += '&'
            str_ret += event['Note']
            if 'accidental' in event:
                str_ret += event['accidental']
            if 'note_note_value' in event:
                str_ret += event['note_note_value']
            return str_ret
        elif 'R' in event:
            str_ret = event['R']
            if 'rest_note_value' in event:
                str_ret += event['rest_note_value']
            return str_ret
        elif 'L' in event:
            return event['L'] + event['default_note_value']
        elif 'V' in event:
            return event['V'] + str(event['volume_127'])
        elif 'T' in event:
            return event['T'] + event['tempo']
        elif 'O' in event:
            return event['O'] + event['octave']
        elif 'octave_shift' in event:
            return event['octave_shift']
