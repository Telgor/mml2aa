import re


class Lexer(object):
    def __init__(self):
        # define a subset of the MML grammar that we want to support:
        dict_re_elements = {
            'note': '(?P<extend_note>&)?(?P<Note>[cdefgab])(?P<accidental>[-+#])?' +
                    '(?P<note_note_value>\d+)?(?P<note_dot>\.)?',
            'num_note': '(?P<extend_num>&)?(?P<N>n)(?P<Note_num>\d+)(?P<num_note_dot>\.)?',
            'rest': '(?P<R>[r])(?P<rest_note_value>\d+)?(?P<rest_dot>\.)?',
            'default_note_value': '(?P<L>l)(?P<default_note_value>\d+)(?P<default_note_dot>\.)?',
            'volume': '(?P<V>[v])(?P<volume>\d+)',
            'volume_shift': '(?P<volume_shift>[\(\)])',
            'tempo': '(?P<T>[t])(?P<tempo>\d+)',
            'octave': '(?P<O>[o])(?P<octave>\d+)',
            'octave_shift': '(?P<octave_shift>[<>])'
        }

        str_re_element_grammar = '(' + ')|('.join(dict_re_elements.values()) + ')'
        self.re_element = re.compile(str_re_element_grammar)

    def process(self, tracks):
        ret = []
        for (i, track) in enumerate(tracks):
            print 'Track #' + str(i)
            ret += [self.process_tracks(track)]
        return ret

    def process_tracks(self, track):
        ret = []
        position = 0
        while True:
            match_result = self.re_element.match(track[position:])
            if not match_result:
                break

            parsed_note = match_result.groupdict(default=None)
            # remove empty keys
            parsed_note = dict((k, v) for k, v in parsed_note.iteritems() if v is not None)
            chars_matched_in_track = len(match_result.group(0))
            ret += [parsed_note]
            # debug print
            print chars_matched_in_track, '@', position, ':', parsed_note
            position += chars_matched_in_track
        return ret
