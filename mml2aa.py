import re


def get_note_time(tempo, measure_part):
    return 60. / tempo / measure_part


# TODO: allow multiple lines.
# Test string for debugging.
# Eventually this should change to reading from standard input.
strMML = 'r1.rv90l8<arbr4.>crdr4.cr<br4.arg+r4.arbr4.>crdr4.cr<br4.ar>cr4.crcr4.c,eeeee'
# strMML = raw_input()

voices = strMML.split(",")

num_voices = len(voices)
assert num_voices <= 3
# TODO: character limit should probably be a command line option.
char_limit = 200

print voices


def lexer(voices):
    # define a subset of the MML grammar that we want to support:
    dict_re_elements = {
        'note': '(?P<extend_note>&)?(?P<Note>[cdefgab])(?P<accidental>[-+#])?(?P<note_measure_part>\d+)?(?P<note_dot>\.)?',
        'num_note': '(?P<extend_num>&)?(?P<N>n)(?P<Note_num>\d+)(?P<num_note_dot>\.)?',
        'rest': '(?P<R>[r])(?P<rest_measure_part>\d+)?(?P<rest_dot>\.)?',
        'default_length': '(?P<L>l)(?P<default_length>\d+)',
        'volume': '(?P<V>[v])(?P<volume>\d+)',
        'tempo': '(?P<T>[t])(?P<tempo>\d+)',
        'octave': '(?P<O>[o])(?P<octave>\d+)',
        'octave_shift': '(?P<octave_shift>[<>])'
    }

    str_re_element_grammar = '(' + ')|('.join(dict_re_elements.values()) + ')'
    re_element = re.compile(str_re_element_grammar)
    for (i, voice) in enumerate(voices):
        while True:
            match_result = re_element.match(voice[positions[i]:])
            if not match_result:
                break

            parsed_note = match_result.groupdict(default=None)
            # remove empty keys
            parsed_note = dict((k, v) for k, v in parsed_note.iteritems() if v is not None)
            chars_matched_in_voice = len(match_result.group(0))
            # debug print
            print i, ',', chars_matched_in_voice, '@', positions[i], ':', parsed_note
            positions[i] += chars_matched_in_voice


eof = False
positions = [0] * num_voices
time = [0] * num_voices
cur_tempo = 120
volumes = [100] * num_voices

lexer(voices)
