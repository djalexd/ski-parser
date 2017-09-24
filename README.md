# ski-parser
a set of very simple Python3 scripts that aggregate
public data of ski resorts from bergfex.com

## used variables
* environment `GOOGLE_API_KEY` of a Google project that has Maps APIs enabled
* for `parser.py` the first argument is considered origin (from) for the
distance calculation.

If any of these parameters are missing, the distance will be `0`.
