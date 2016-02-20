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
        self.octaves = [5] * num_tracks
        self.time = [0] * num_tracks
        self.tempo = 120
        self.volumes = [8] * num_tracks
        self.active_tracks = num_tracks


class AAConverter(object):
    def __init__(self, tokens, sync_rest_every_nth, verbosity=False):
        self.sync_rest_every_nth = sync_rest_every_nth
        self.verbosity = verbosity
        self.tokens = tokens
        self.num_tracks = len(tokens)
        self.event_counts = [len(i) for i in self.tokens]
        self.state = TrackerState(self.num_tracks)
        self.track_start = [{'O': 'o', 'octave': '5'},
                            {'V': 'v', 'volume_127': '64'},
                            {'L': 'l', 'default_note_value': '4'},
                            # disabled because tempo should be sorted per channel beforehand.
                            # if future versions solve cross-tracks tempo changes, this could be enabled.
                            # {'T': 't', 'tempo': '120'}
                            ]
        self.new_tokens = [[_j.copy() for _j in self.track_start] for _i in xrange(self.num_tracks)]

    def process(self):
        ret_str = ''

        # add start and end times to each event
        while True:
            i = self.get_next_event_and_update_state(self.state)
            if not i:
                break
            if self.verbosity:
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
            # archeage plays one octave lower
            octave = int(event['octave']) + 1
            state.octaves[i] = octave
            event['octave'] = str(octave)
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

        self.add_new_tokens(i, [event])
        state.positions[i] += 1

    def process_note_event(self, event, i):
        state = self.state
        assert not self.is_control_event(event)
        # TODO: create multiple events for numbered notes and dotted rests.
        if 'N' in event:
            current_octave = int(state.octaves[i])
            note_num = int(event['Note_num'])
            new_event = self.numbered_note_to_named_note(event)
            # before adding the note, insert an octave change
            note_octave = note_num // 12 + 1
            if current_octave != note_octave:
                self.add_new_tokens(i, [{'O': 'o', 'octave': str(note_octave)},
                                        new_event,
                                        {'O': 'o', 'octave': str(current_octave)}])
            else:
                self.add_new_tokens(i, [new_event])

        elif 'R' in event:
            if 'rest_dot' in event:
                # split extended dotted breaks
                new_primary = {'R': 'r'}
                new_secondary = {'R': 'r'}
                if 'rest_note_value' in event:
                    primary_value = event['rest_note_value']
                    new_primary['rest_note_value'] = primary_value
                else:
                    primary_value = state.default_note_values[i]

                secondary_value = str(int(primary_value) * 2)
                new_secondary['rest_note_value'] = secondary_value
                self.add_new_tokens(i, [new_primary])
                self.add_new_tokens(i, [new_secondary])
            else:
                self.add_new_tokens(i, [event])

        elif 'extend_note' in event and 'note_dot' in event:
            # split extended dotted notes
            new_primary = event.copy()
            new_secondary = event.copy()
            del new_primary['note_dot']
            del new_secondary['note_dot']
            if 'note_note_value' in new_primary:
                primary_value = event['note_note_value']
            else:
                primary_value = state.default_note_values[i]
            secondary_value = str(int(primary_value) * 2)
            new_secondary['note_note_value'] = secondary_value
            self.add_new_tokens(i, [new_primary])
            self.add_new_tokens(i, [new_secondary])

        else:
            self.add_new_tokens(i, [event])

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
        list_track_strings = []
        for track in self.new_tokens:
            track_string = ''
            for event in track:
                track_string += self.event_to_string(event)
            list_track_strings += [track_string]
        return ','.join(list_track_strings)

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
            if 'note_dot' in event:
                str_ret += event['note_dot']
            return str_ret
        elif 'R' in event:
            str_ret = event['R']
            if 'rest_note_value' in event:
                str_ret += event['rest_note_value']
            return str_ret
        elif 'L' in event:
            str_ret = event['L'] + event['default_note_value']
            if 'default_note_dot' in event:
                str_ret += event['default_note_dot']
            return str_ret
        elif 'V' in event:
            return event['V'] + str(event['volume_127'])
        elif 'T' in event:
            return event['T'] + event['tempo']
        elif 'O' in event:
            return event['O'] + event['octave']
        elif 'octave_shift' in event:
            return event['octave_shift']
        elif 'white_space' in event:
            return ''

    @staticmethod
    def note_name(note_num):
        note_num_modulus = note_num % 12
        note_string = ['c', 'c', 'd', 'd', 'e', 'f', 'f', 'g', 'g', 'a', 'a', 'b'][note_num_modulus]
        note_num_sharp = note_num_modulus in [1, 3, 6, 8, 10]
        return note_string, '#' if note_num_sharp else ''

    @classmethod
    def numbered_note_to_named_note(cls, event):
        assert 'Note_num' in event
        note_num = int(event['Note_num'])
        note_string, note_accidental = cls.note_name(note_num)
        # create a new event
        new_event = {'Note': note_string}
        if note_accidental:
            new_event['accidental'] = note_accidental
            # use default note_note_value
        if 'extended_num' in event:
            new_event['extend_note'] = event['extend_num']
        if 'num_note_dot' in event:
            new_event['note_dot'] = event['num_note_dot']
        return new_event

    def add_new_tokens(self, i, event_list):
        old_length = len(self.new_tokens[i])
        self.new_tokens[i] += event_list
        new_length = len(self.new_tokens[i])
        # if we wrapped past the specified number of events, add 'r64' to workaround sync problem
        if self.sync_rest_every_nth:
            if old_length % self.sync_rest_every_nth > new_length % self.sync_rest_every_nth:
                self.new_tokens[i] += [{'R': 'r', 'rest_note_value': '64'}]
