"""Evaluate measured pen observations; missing evidence never means pass.

CSV fields: condition,timestamp_us,reference_x_mm,reference_y_mm,x_mm,y_mm,
valid,contact,reference_contact,latency_ms. No hardware data is synthesized.
"""
import argparse
import csv
import json
import math
from collections import defaultdict


def percentile(values, q):
    if not values:
        return None
    values = sorted(values)
    i = (len(values) - 1) * q
    lo, hi = math.floor(i), math.ceil(i)
    return values[lo] + (values[hi] - values[lo]) * (i - lo)


def bit(row, key):
    if row[key] not in ('0', '1'):
        raise ValueError(f'{key} must be 0 or 1')
    return int(row[key])


def number(row, key):
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f'{key} must be finite')
    return value


def evaluate(rows):
    groups = defaultdict(list)
    for row in rows:
        if not row.get('condition', '').strip():
            raise ValueError('condition required')
        groups[row['condition']].append(row)
    result = {}
    for condition, samples in groups.items():
        errors, latencies, previous = [], [], None
        missing, false_contact, missed_contact = 0, 0, 0
        for row in samples:
            stamp = number(row, 'timestamp_us')
            if stamp < 0 or (previous is not None and stamp <= previous):
                raise ValueError('timestamps must increase within each condition')
            previous = stamp
            valid = bit(row, 'valid')
            contact = bit(row, 'contact')
            reference_contact = bit(row, 'reference_contact')
            false_contact += bool(contact and not reference_contact)
            missed_contact += bool(reference_contact and not contact)
            if reference_contact:
                if not valid:
                    missing += 1
                else:
                    errors.append(math.hypot(number(row, 'x_mm') - number(row, 'reference_x_mm'),
                                             number(row, 'y_mm') - number(row, 'reference_y_mm')))
                    latency = number(row, 'latency_ms')
                    if latency < 0:
                        raise ValueError('latency cannot be negative')
                    latencies.append(latency)
        n_contact = sum(bit(r, 'reference_contact') for r in samples)
        result[condition] = dict(samples=len(samples), contact_samples=n_contact,
                                decoded_contact_samples=len(errors), missing_contact_samples=missing,
                                missing_ratio=missing/n_contact if n_contact else None,
                                error_p50_mm=percentile(errors,.5), error_p95_mm=percentile(errors,.95),
                                error_max_mm=max(errors) if errors else None,
                                latency_p95_ms=percentile(latencies,.95),
                                false_contact_samples=false_contact, missed_contact_samples=missed_contact,
                                status='MEASURED_NOT_RELEASE_APPROVAL')
    return {'conditions':result, 'status':'NO_DATA' if not result else 'PARTIAL_EVIDENCE',
            'limitations':['Sample-weighted metrics are not stroke dropout rates.',
                          'Reference accuracy, clock alignment and test coverage require independent review.',
                          'No numeric threshold alone approves safety or manufacture.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv')
    parser.add_argument('--output')
    args=parser.parse_args()
    with open(args.csv, newline='', encoding='utf-8-sig') as stream:
        report=evaluate(csv.DictReader(stream))
    text=json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        with open(args.output,'w',encoding='utf-8') as out: out.write(text+'\n')
    else: print(text)

if __name__ == '__main__': main()
