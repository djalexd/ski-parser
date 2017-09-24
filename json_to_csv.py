#!/usr/bin/env python3
import json
import csv

def flattenjson( b, delim ):
    val = {}
    for i in b.keys():
        if isinstance( b[i], dict ):
            get = flattenjson( b[i], delim )
            for j in get.keys():
                val[ i + delim + j ] = get[j]
        else:
            val[i] = b[i]

    return val

with open('resorts_parsed.json') as input:
    raw_csv = [flattenjson(r, '_') for r in json.load(input)]

    columns = [ x for row in raw_csv for x in row.keys() ]
    columns = list( set( columns ) )

    with open( 'resorts.csv', 'w' ) as out_file:
        csv_w = csv.writer( out_file )
        csv_w.writerow( columns )

        for i_r in raw_csv:
            csv_w.writerow( map( lambda x: i_r.get( x, "" ), columns ) )
