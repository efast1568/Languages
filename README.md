# Link Robins — Languages

The translations for the [Link Robins](https://linkrobins.com) dashboard and status pages, open for
corrections. Nine languages, 962 strings each.

| Language | File | |
|---|---|---|
| Deutsch | [`lang/de.json`](lang/de.json) | |
| Español | [`lang/es.json`](lang/es.json) | |
| Français | [`lang/fr.json`](lang/fr.json) | |
| 日本語 | [`lang/ja.json`](lang/ja.json) | |
| 한국어 | [`lang/ko.json`](lang/ko.json) | |
| Polski | [`lang/pl.json`](lang/pl.json) | |
| Русский | [`lang/ru.json`](lang/ru.json) | |
| 简体中文 | [`lang/zh_CN.json`](lang/zh_CN.json) | first pass, unreviewed |
| 繁體中文 | [`lang/zh_TW.json`](lang/zh_TW.json) | first pass, unreviewed |

**Every one of these was drafted without a native speaker reading it.** They shipped that way on purpose —
a rough translation you can correct beats a perfect one that never arrives. So corrections are the point of
this repository, and no correction is too small: one awkward word is a welcome pull request.

Merged corrections go live on linkrobins.com within a day or two. You get credit in the commit that carries
them across.

## What gets translated, and what does not

**The key is the English string.** `"Add monitor": "监测添加"` — the left side is what the app asks for, the
right side is what it shows. Never edit the left side: change it and the app stops finding the string and
falls back to English.

**Product and format names stay English in every language.** Birdseye, Warble, Sandbox, Uptime Monitoring,
Extensions, Flarum — plus technical names like API, URL, PHP, Redis, Markdown, CPU, RAM, and date formats
like `Y-m-d`. The full list is [`context/english-only.txt`](context/english-only.txt) and the check enforces
it. The reason is legibility: a reader should always be able to tell which words *name* a product and which
merely *describe* one. The words around a product name do get translated — in `Realtime — Warble`, the left
half is yours and the right half is not.

**Placeholders must survive.** `:count`, `:name`, `:target` and friends are filled in by the app at runtime.
Keep them spelled exactly as they are; move them wherever your language needs them.

**HTML tags must survive too.** A handful of strings contain `<a>` or `<b>`. Translate the text between the
tags, leave the tags alone.

**English is not in this repository and never will be.** `lang/en.json` is the source, it lives in the
application, and the check rejects any pull request that adds it.

## Context: where each string appears

A word can be a noun on one screen and a verb on another. [`context/strings.csv`](context/strings.csv) lists
every string with the screen it renders on (`monitors/edit`, `status-pages/edit`, `Email`, `Message after an
action`), the placeholders it carries, and a note for the ones whose English is ambiguous on its own — that
`Store` is the create verb rather than a shop, that `Index` is the SEO setting rather than the REST verb.

## Two ways to contribute

**If you use git**, edit `lang/<code>.json` directly and open a pull request. Run the check first:

```sh
python3 tools/validate.py          # every language
python3 tools/validate.py ja       # just yours
```

It needs nothing but Python 3, and it runs on every pull request anyway.

**If you would rather not**, build yourself an offline review sheet:

```sh
python3 tools/review-sheet.py zh_CN zh_TW    # one or more languages
```

That writes `review-zh_CN-zh_TW.html`: open it in any browser, with or without internet. Every string sits
next to the screen it appears on, you type corrections into the boxes, your work saves in the browser as you
go, and **Download** hands back finished `.json` files plus a CSV of your comments. Drop the files into
`lang/` and open a pull request — or email them to karl@linkrobins.com and they will be committed for you,
with credit.

## Adding a language that is not here yet

Copy an existing catalogue, translate the values, and name the file after the locale code (`pt_BR.json`,
`nl.json`). Set `lang_code` to match the filename, `lang_name` to the language's own name for itself
(`Português`, not `Portuguese`), and `lang_dir` to `ltr` or `rtl`. Then open a pull request — the
application side needs one small change from us before a new language appears in the switcher, and that is
our job, not yours.

## How a correction reaches the site

Pull requests are merged here and then copied by hand into the application, which is a separate private
repository. That is deliberate: the application deploys on push, and translations should not deploy
themselves. Expect a day or two, and a note on the pull request when it is live.

## Licence

The English source text and the translations are © Link Robins. By opening a pull request you are giving us
permission to use your contribution in the product, in every language, without further conditions. The files
are published here so they can be corrected, not as a general-purpose translation memory.

Questions: karl@linkrobins.com, or [the forum](https://linkrobins.com/forum).
