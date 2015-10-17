import mml_lexer
import mml_conv


def get_note_time(tempo, measure_part):
    return 60. / tempo / measure_part


# TODO: allow multiple lines.
# Test string for debugging.
# Eventually this should change to reading from standard input.
strMML = 'r1.rv9l8<arbr4.>crdr4.cr<br4.arg+r4.arbr4.>crdr4.cr<br4.ar>cr4.crcr4.c,eeeeeeeeeeeeee'
# strMML = raw_input()

tracks = strMML.split(",")

num_tracks = len(tracks)
assert num_tracks <= 3
# TODO: character limit should probably be a command line option.
char_limit = 200

print tracks

lexer = mml_lexer.Lexer()
tokens = lexer.process(tracks)
print tokens

conv = mml_conv.AAConverter(tokens)
conv.process()