import mml_lexer


def get_note_time(tempo, measure_part):
    return 60. / tempo / measure_part


# TODO: allow multiple lines.
# Test string for debugging.
# Eventually this should change to reading from standard input.
strMML = 'r1.rv90l8<arbr4.>crdr4.cr<br4.arg+r4.arbr4.>crdr4.cr<br4.ar>cr4.crcr4.c,eeeee'
# strMML = raw_input()

tracks = strMML.split(",")

num_tracks = len(tracks)
assert num_tracks <= 3
# TODO: character limit should probably be a command line option.
char_limit = 200

print tracks




eof = False
positions = [0] * num_tracks
time = [0] * num_tracks
cur_tempo = 120
volumes = [100] * num_tracks

lexer = mml_lexer.Lexer()
print lexer.process(tracks)
