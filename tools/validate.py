#!/usr/bin/env python3
"""Check every catalogue in lang/ against the rules in README.md.

    python3 tools/validate.py            # all catalogues
    python3 tools/validate.py zh_CN      # just one

No dependencies beyond the standard library. Exits non-zero if anything fails,
which is what the pull request check runs on.
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = os.path.join(ROOT, 'lang')
PLACEHOLDER = re.compile(r':[a-zA-Z_][a-zA-Z0-9_]*')
TAG = re.compile(r'</?([a-zA-Z][a-zA-Z0-9]*)')
META = ('lang_code', 'lang_name', 'lang_dir')


def load_reference():
    """The canonical string list, in order, from context/strings.csv."""
    with open(os.path.join(ROOT, 'context', 'strings.csv'), encoding='utf-8') as f:
        return [row['English'] for row in csv.DictReader(f)]


def load_english_only():
    path = os.path.join(ROOT, 'context', 'english-only.txt')
    with open(path, encoding='utf-8') as f:
        return {line.rstrip('\n') for line in f
                if line.strip() and not line.startswith('#')}


def check(locale, reference, english_only):
    """Return a list of problems with lang/<locale>.json."""
    problems = []
    add = problems.append
    path = os.path.join(LANG, locale + '.json')

    try:
        with open(path, encoding='utf-8') as f:
            cat = json.load(f)
    except json.JSONDecodeError as e:
        return ['not valid JSON: %s' % e]

    if not isinstance(cat, dict) or any(not isinstance(v, str) for v in cat.values()):
        return ['must be a flat object of string values']

    # 1. exactly the reference keys, no more and no fewer
    ref = set(reference)
    missing, extra = ref - set(cat), set(cat) - ref
    for k in sorted(missing)[:20]:
        add('missing string: %r' % k)
    if len(missing) > 20:
        add('...and %d more missing' % (len(missing) - 20))
    for k in sorted(extra)[:20]:
        add('unknown string, not in context/strings.csv: %r' % k)
    if len(extra) > 20:
        add('...and %d more unknown' % (len(extra) - 20))

    # 2. metadata
    for key in META:
        if not cat.get(key, '').strip():
            add('%s must not be empty' % key)
    if cat.get('lang_code') != locale:
        add('lang_code is %r but the file is named %s.json' % (cat.get('lang_code'), locale))
    if cat.get('lang_dir') not in ('ltr', 'rtl'):
        add('lang_dir must be "ltr" or "rtl", got %r' % cat.get('lang_dir'))

    for key in sorted(ref & set(cat)):
        value = cat[key]

        # 3. every :placeholder survives, spelled identically
        want, got = set(PLACEHOLDER.findall(key)), set(PLACEHOLDER.findall(value))
        for p in sorted(want - got):
            add('%r drops the placeholder %s' % (key, p))
        for p in sorted(got - want):
            add('%r invents the placeholder %s' % (key, p))

        # 4. HTML tags survive
        want_tags, got_tags = sorted(TAG.findall(key)), sorted(TAG.findall(value))
        if want_tags != got_tags:
            add('%r changes the HTML tags (%s -> %s)'
                % (key, ' '.join(want_tags) or 'none', ' '.join(got_tags) or 'none'))

        # 5. product and format names stay English
        if key in english_only and value != key:
            add('%r stays English in every language, got %r' % (key, value))

        # 6. an empty value renders as an empty screen, never as a fallback
        if key not in META and not value.strip():
            add('%r is empty — delete the line instead if you want the English' % key)

    return problems


def main():
    if os.path.exists(os.path.join(LANG, 'en.json')):
        print('FAIL  lang/en.json must never be committed — English is the source, not a translation')
        return 1

    reference, english_only = load_reference(), load_english_only()
    wanted = sys.argv[1:]
    locales = sorted(f[:-5] for f in os.listdir(LANG) if f.endswith('.json'))
    if wanted:
        unknown = [w for w in wanted if w not in locales]
        if unknown:
            print('FAIL  no such catalogue: %s' % ', '.join(unknown))
            return 1
        locales = wanted

    failed = 0
    for locale in locales:
        problems = check(locale, reference, english_only)
        if problems:
            failed += 1
            print('FAIL  %s — %d problem%s' % (locale, len(problems), '' if len(problems) == 1 else 's'))
            for p in problems:
                print('      %s' % p)
        else:
            print('ok    %s — %d strings' % (locale, len(reference)))

    print()
    print('%d of %d catalogues pass' % (len(locales) - failed, len(locales)))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
