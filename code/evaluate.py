#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from main import run

COLMAP = {
    'status': 'Status',
    'product_area': 'Product Area',
    'request_type': 'Request Type',
}

def n(v): return (v or '').strip().lower()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data', default='data')
    ap.add_argument('--sample', default='support_tickets/sample_support_tickets.csv')
    args=ap.parse_args()
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'pred.csv'
        run(Path(args.data), Path(args.sample), out)
        pred=list(csv.DictReader(open(out,encoding='utf-8')))
    gold=list(csv.DictReader(open(args.sample,encoding='utf-8')))
    print(f'Rows: {len(gold)}')
    for pc,gc in COLMAP.items():
        ok=sum(1 for p,g in zip(pred,gold) if n(p[pc])==n(g[gc]))
        print(f'{pc}: {ok}/{len(gold)} = {ok/len(gold):.1%}')
    print('\nPredictions:')
    for i,(p,g) in enumerate(zip(pred,gold),1):
        print(i, 'status', p['status'], '/', n(g['Status']), '| area', p['product_area'], '/', n(g['Product Area']), '| type', p['request_type'], '/', n(g['Request Type']))
if __name__=='__main__': main()
