# Contributing

Short version: fix what reads wrong in `lang/<code>.json`, run `python3 tools/validate.py`, open a pull
request. Partial is welcome — one corrected word is worth sending.

## Before you start

Read the rules in [README.md](README.md). The three that trip people up:

1. **Never edit the left side of a line.** The English key is how the app finds the string.
2. **Keep every `:placeholder`** exactly as spelled. Move it, do not rename it.
3. **Product and format names stay English** — the list is in `context/english-only.txt`.

## Working on a language

```sh
git clone https://github.com/linkrobins/Languages.git
cd Languages
git checkout -b fix-japanese-uptime

# edit lang/ja.json

python3 tools/validate.py ja
```

`context/strings.csv` tells you which screen each string appears on. If a string is still ambiguous, say so
in the pull request and we will tell you exactly where it renders — the English being unclear is a bug on
our side, not yours.

If you would rather work in a browser than in JSON, `python3 tools/review-sheet.py ja` builds an offline
editor that produces the finished file for you. See the README.

## Consistency beats individual strings

The 962 strings rest on maybe a hundred recurring words — monitor, uptime, incident, alert, key, dashboard.
If one of those is wrong, it is wrong in fifty places. Say so once in the pull request ("監視 should be
モニター throughout") rather than editing fifty rows by hand, and we will apply it everywhere.

## What happens next

The check runs automatically. Once it passes and the change looks sane, it is merged and copied into the
application by hand, usually within a day or two. You will get a note on the pull request when it is live.

Disagreements about wording are settled in favour of the person who speaks the language.
