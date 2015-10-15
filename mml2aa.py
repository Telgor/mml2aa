import re


def get_note_time(tempo, measure_part):
    return 60. / tempo / measure_part


strMML = 'c16t90r8a&aa,cn100,dr'
# strMML = raw_input("MML String:")

voices = strMML.split(",")

num_voices = len(voices)
assert num_voices <= 3
char_limit = 200
print strMML
print voices

dict_re_elements = {
    'note': '(?P<extend_note>&)?(?P<note>[cdefgab])(?P<accidental>[-+#]?)(?P<note_measure_part>\d+)?(?P<note_dot>\.?)',
    'num_note': '(?P<extend_num>&)?(?P<n>n)(?P<note_num>\d+)?(?P<num_note_dot>\.?)',
    'rest': '(?P<r>r)(?P<rest_measure_part>\d+)?(?P<rest_dot>\.?)',
    'volume': '(?P<v>v)(?P<volume>\d+)?',
    'tempo': '(?P<t>t)(?P<tempo>\d+)?',
}

str_re_element_grammar = '(' + ')|('.join(dict_re_elements.values()) + ')'
re_element = re.compile(str_re_element_grammar)

eof = False
positions = [0] * num_voices
time = [0] * num_voices
cur_tempo = 120
volumes = [100] * num_voices
while not eof:
    chars_matched_in_round = 0
    # find nearest note end
    for (i, voice) in enumerate(voices):
        match_result = re_element.match(voice[positions[i]:])
        if match_result:
            parsed_note = match_result.groupdict(default=None)
            # remove empty keys
            parsed_note = dict((k, v) for k, v in parsed_note.iteritems() if v is not None)
            chars_matched_in_voice = len(match_result.group(0))
            print i, ',', chars_matched_in_voice, '@',  positions[i], ':', parsed_note
            positions[i] += chars_matched_in_voice
            chars_matched_in_round += chars_matched_in_voice

    eof = chars_matched_in_round == 0
