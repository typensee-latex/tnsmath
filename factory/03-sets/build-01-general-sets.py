#! /usr/bin/env python3

import re

from mistool.os_use import PPath
from mistool.string_use import between, joinand
from orpyste.data import ReadBlock

BASENAME = PPath(__file__).stem.replace("build-", "")

THIS_DIR = PPath(__file__).parent
STY_FILE = THIS_DIR / f'{BASENAME}.sty'
TEX_FILE = STY_FILE.parent / (STY_FILE.stem + "[fr].tex")

PATTERN_FOR_PEUF = re.compile("\d+-(.*)")
match            = re.search(PATTERN_FOR_PEUF, STY_FILE.stem)
PEUF_FILE        = STY_FILE.parent / (match.group(1).strip() + ".peuf")

DECO = " "*4


# ----------- #
# -- TOOLS -- #
# ----------- #

SUFFIXES = {
    '+': "p",
    '-': "n",
    '*': "s"
}

def latex_classical(setdef):
    setname, *suffixes = setdef[::1]
    latexname          = setname*2

    latexdef = [
        f"\\newcommand\\{latexname}{{\\ensuremath{{\\setalge{{{setname}}}}}}}"
    ]

    latexsuffixes = [SUFFIXES[s] for s in suffixes]

    if 's' in latexsuffixes:
        for sign in "np":
            if sign in latexsuffixes:
                latexsuffixes.append(f's{sign}')

    for onesuf in latexsuffixes:
        latexdef.append(
            f"\\newcommand\\{latexname}{onesuf}{{\\ensuremath{{\\setspecial{{\\{latexname}}}{{{onesuf}}}}}}}"
        )

    latexdef = "\n".join(latexdef)

    return latexdef


# -------------------------- #
# -- THE CONSTANTS TO ADD -- #
# -------------------------- #

with ReadBlock(
    content = PEUF_FILE,
    mode    = "verbatim"
) as data:
    config = {
        k: " ".join(v).split()
        for k, v in data.mydict("std mini").items()
    }

classicalsets = config["classical-sets"]


# ------------------------- #
# -- TEMPLATES TO UPDATE -- #
# ------------------------- #

with open(
    file     = STY_FILE,
    mode     = 'r',
    encoding = 'utf-8'
) as styfile:
    template_sty = styfile.read()


with open(
    file     = TEX_FILE,
    mode     = 'r',
    encoding = 'utf-8'
) as docfile:
    template_tex = docfile.read()


# --------------------- #
# -- UPDATING MACROS -- #
# --------------------- #

text_start, _, text_end = between(
    text = template_sty,
    seps = [
        "% List of classical sets - START",
        "% List of classical sets - END"
    ],
    keepseps = True
)

alldefs = []

for setdef in classicalsets:
    alldefs.append(latex_classical(setdef))

alldefs = "\n\n".join(alldefs)
alldefs = f"\n\n{alldefs}\n\n"

template_sty = text_start + alldefs + text_end


# ----------------------- #
# -- TABLE OF SUFFIXES -- #
# ----------------------- #

text_start, _, text_end = between(
    text = template_tex,
    seps = [
        "% == Table of suffixes - START == %",
        "% == Table of suffixes - END == %"
    ],
    keepseps = True
)

suffix_header = [x for x in "n p s sn sp".split()]
sexiffus      = {v: k for k,v in SUFFIXES.items()}

table_header = DECO*3 + "  & {0} \\\\".format(
    " & ".join(
        f"\\verb+{s}+" for s in suffix_header
    )
)

table_lines = []

for onesetdef in classicalsets:
    cells = [f"\\verb+\\{onesetdef[0]*2}+"]

    for s in suffix_header:
        hassuffix = True

        for char in s:
            if sexiffus[char] not in onesetdef:
                hassuffix = False
                break

        if hassuffix:
            cells.append(r'$\times$')

        else:
            cells.append('        ')

    table_lines.append(" & ".join(cells) + r' \\')

table_lines = f'{DECO*3}\\hline ' \
            + f'\n{DECO*3}\\hline '.join(table_lines)


latextable = f"""

\\begin{{table}}[h]
    \\caption{{Suffixes}}
    \\begin{{center}}
        \\begin{{tabular}}{{c|c|c|c|c|c}}
{table_header}
{table_lines}
        \\end{{tabular}}
    \\end{{center}}
    \\label{{table:suffixes-sets}}
\\end{{table}}

"""

template_tex = text_start + latextable + text_end


# ------------------- #
# -- DOCUMENTATION -- #
# ------------------- #

text_start, _, text_end = between(
    text = template_tex,
    seps = [
        "% == Docs for classical sets - START == %",
        "% == Docs for classical sets - END == %"
    ],
    keepseps = True
)

allmacros = []

for onesetdef in classicalsets:
    allmacros.append(f"{onesetdef[0]}")

    for s in suffix_header:
        hassuffix = True

        for char in s:
            if sexiffus[char] not in onesetdef:
                hassuffix = False
                break

        if hassuffix:
            allmacros.append(f"{onesetdef[0]}{s}")

template_tex = text_start + f"""

\\foreach \\k in {{{", ".join(allmacros)}}}{{

	\\IDmacro*{{\k}}{{0}}

}}
""" + "\n" + text_end


# -------------------------- #
# -- UPDATES OF THE FILES -- #
# -------------------------- #

with open(
    file     = TEX_FILE,
    mode     = 'w',
    encoding = 'utf-8'
) as docfile:
    docfile.write(template_tex)

with open(
    file     = STY_FILE,
    mode     = 'w',
    encoding = 'utf-8'
) as docfile:
    docfile.write(template_sty)
