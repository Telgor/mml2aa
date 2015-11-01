# mml2aa
Convert typical MML files to the Archeage MML format.

Currently supported:
- Numbered notes (e.g. `o3n51` -> `o3o5d#o3`)
- Dotted rests (`l4r.` -> `l4rr8`)
- Volume range (`v9` -> `v76`)
- Experimental: add r64 rests as a work around for Archeage's sync problem.

```
usage: mml2aa.py [-h] [-s N] [-v] [infile] [outfile]

positional arguments:
  infile                Input filename (default is stdin).
  outfile               Output filename (default is stdout).

optional arguments:
  -h, --help            show this help message and exit
  -s N, --sync-rest-every N
                        Adds an r64 rest every Nth event.
  -v, --verbosity       Increase output verbosity.

```