#!/usr/bin/env python

import glob

outfile = open("../securities.csv","w")

special = {
   'BRK/A': 'BRK-A',
   'BWL': None,
   'ZXX': None,
   'BRK': None,
   'BF': None,
   'CRD': None,
   'AKO': None,
   'FCE': None,
   'HUB': None,
   'JW': None,
   'KV': None,
   'MOG': None,
   'RDS': None,
   'ZYY': None,
   'ZZA': None,
   'ZZB': None,
   'ZZD': None,
   'ZZE': None,
   'ZZF': None,
   'ZZG': None,
   'ZZH': None,
   'ZZI': None,
   'ZZJ': None,
   'ZZJJ': None,
   'WRS': None,

   'WBS-WS': None,
   'VLY-WS': None,
   'COF-WS': None,
   'SEMG-WS': None,
   'OC-WS-B': None,
   'CRMD-WS': None,
   'CHC-WS': None,
   'STI-WS-B': None,
   'STI-WS-A': None,
   'ARR-WS': None,
   'GM-WS-B': None,
   'GM-WS-A': None,
   'NBS-WS': None,
   'C-WS-B': None,
   'REN-WS': None,
   'BAC-WS-B': None,
   'BAC-WS-A': None,
   'IGC-WS': None,
   'TTTM-WS-W': None,
   'TTTM-WS-Z': None,
   'HIG-WS': None,
   'PNC-WS': None,
   'NNA-WS': None,
   'MDGN-WS': None,
   'FPP-WS': None,
   'TWO-WS': None,
   'TCB-WS': None,
   'AIG-WS': None,
   'WFC-WS': None,
   'SOA-WS': None,
   'F-WS': None,
   'IDI-WS': None,
   'VRNG-WS': None,
   'LNC-WS': None,
   'CMA-WS': None,
   'TLB-WS': None,
   'C-WS-A': None,
   'JPM-WS': None,

}

for f in glob.glob("*.csv"):
    for i,line in enumerate(file(f)):
        if i==0: continue
        symbol = line.split(',')[0][1:-1].replace('/','-')
        if '^' in symbol: continue
        if symbol in special:
            if special[symbol]:
                symbol = special[symbol]
            else: continue
        outfile.write( symbol+"\n" )
