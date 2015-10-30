import mml_lexer
import mml_conv
import fileinput
import re

def get_note_time(tempo, measure_part):
    return 60. / tempo / measure_part


# TODO: allow multiple lines.
# Test string for debugging.
# Eventually this should change to reading from standard input.
# strMML = 'r1.rv9l8<an78.rbr4.>crdr4.cr<br4.a(rg+)r4.arbr4.>crdr4.cr<br4.ar>cr4.crcr4.cr.,eeeeeeeeeeeeee'
list_strMML = []
# remove all whitespaces, the "MML@" header and the trailing ";"
re_to_remove = re.compile(r'\s+|MML@|;')
for line in fileinput.input():
    list_strMML.append(re.sub(re_to_remove, '', line))
strMML = ''.join(list_strMML)

tracks = strMML.split(",")

num_tracks = len(tracks)
assert num_tracks <= 3
# TODO: character limit should probably be a command line option.
char_limit = 200

print tracks

lexer = mml_lexer.Lexer()
tokens = lexer.process(tracks)
print tokens

converter = mml_conv.AAConverter(tokens)
converter.process()
print converter
