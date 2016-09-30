import mml_lexer
import mml_conv
import re
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sync-rest-every", type=int, metavar='N',
                    help="Adds an r64 rest every Nth event.")
parser.add_argument("-v", "--verbosity", action="count", default=0,
                    help="Increase output verbosity.")
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                    default=sys.stdin, help="Input filename (default is stdin).")
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                    default=sys.stdout, help="Output filename (default is stdout).")
args = parser.parse_args()


def get_note_time(tempo, measure_part):
    return 60. / tempo / measure_part


# TODO: allow multiple lines.
# Test string for debugging.
# Eventually this should change to reading from standard input.
# strMML = 'r1.rv9l8<an78.rbr4.>crdr4.cr<br4.a(rg+)r4.arbr4.>crdr4.cr<br4.ar>cr4.crcr4.cr.,eeeeeeeeeeeeee'
list_strMML = []
# remove all whitespaces, the "MML@" header and the trailing ";"
re_to_remove = re.compile(r'\s+|MML@|;')
for line in args.infile:
    list_strMML.append(re.sub(re_to_remove, '', line))
strMML = ''.join(list_strMML)

tracks = strMML.split(",")

num_tracks = len(tracks)
assert num_tracks <= 3
# TODO: character limit should probably be a command line option.
char_limit = 200

if args.verbosity:
    print(tracks)

lexer = mml_lexer.Lexer()
tokens = lexer.process(tracks)
if args.verbosity:
    print(tokens)

converter = mml_conv.AAConverter(tokens, sync_rest_every_nth=args.sync_rest_every, verbosity=args.verbosity)
converter.process()
print(converter)
