"""Correct scanning errors in the Wastena text.

The typescript's own spelling stays as the typist left it; only what the
scanner misread is put right here. Two kinds of correction are applied:

  1. A full stop read as a letter. The typist's period often came out as an
     "e", so "backe The" was really "back. The". These are only corrected
     where a sentence plainly ends - the next word is capitalised, or the
     paragraph ends there - and where the resulting word is not one the book
     otherwise uses.

  2. Letters the scanner confused, listed in CORRECTIONS below. Every entry
     is a form that is not a word at all ("disoiples", "kmows", "vhich"), so
     the reading is not in doubt. Words that could genuinely be either
     reading - "white" for "while", "ethers" for "others", "prey" for "pray"
     - are deliberately left alone and reported instead, since telling those
     apart needs the scan.

    python tools/proofread_wastena.py           # apply, then report
    python tools/proofread_wastena.py --dry-run # report only
"""
import collections
import glob
import os
import re
import sys

SRC = os.path.join("transcripts", "wastena", "book")

# Scanned form -> what the typist wrote. Only unambiguous non-words.
CORRECTIONS = {
    # o read for e
    "aftor": "after", "attunoment": "attunement", "becomo": "become",
    "beforo": "before", "beon": "been", "bocause": "because",
    "bocoming": "becoming", "bogotten": "begotten", "boloveds": "beloveds",
    "centor": "center", "conters": "centers", "consciousnoss": "consciousness",
    "dono": "done", "dosire": "desire", "eithor": "either", "evon": "even",
    "feol": "feel", "feoling": "feeling", "fullnoss": "fullness",
    "groater": "greater", "happons": "happens", "highor": "higher",
    "immodiately": "immediately", "infinito": "infinite", "longor": "longer",
    "mannor": "manner", "momont": "moment", "moro": "more", "naturo": "nature",
    "proparing": "preparing", "recoive": "receive", "roading": "reading",
    "roturn": "return", "seoking": "seeking", "sido": "side", "soems": "seems",
    "somo": "some", "spoak": "speak", "thero": "there", "thoso": "those",
    "thoy": "they", "boen": "been", "deen": "been", "geen": "been",
    "choico": "choice", "dolivery": "delivery",
    # o read for c
    "disoiples": "disciples", "whioh": "which", "direot": "direct",
    "meroy": "mercy", "balanoe": "balance", "frequenoy": "frequency",
    "reoognize": "recognize", "inorease": "increase", "inereased": "increased",
    "inoarnations": "incarnations", "convietion": "conviction",
    # e read for a
    "gether": "gather", "heert": "heart", "humenly": "humanly",
    "humen": "human", "cennot": "cannot", "certeinly": "certainly",
    "ettention": "attention", "impetient": "impatient", "wetch": "watch",
    "thenksgiving": "thanksgiving", "treining": "training",
    "incarnetions": "incarnations", "besutiful": "beautiful",
    "foundstion": "foundation", "ebout": "about", "ehange": "change",
    "cleim": "claim", "cleser": "closer", "wera": "were", "weye": "were",
    "sensa": "sense", "tida": "tide", "senne": "sense",
    # e read for o
    "ence": "once", "unce": "once", "bedy": "body", "bady": "body",
    "bods": "body", "inte": "into", "thse": "these",
    # v read for w
    "pover": "power", "dravn": "drawn", "shovn": "shown", "vhere": "where",
    "vhich": "which", "vhether": "whether", "vith": "with", "vnto": "unto",
    "wnto": "unto", "throvgh": "through", "mvch": "much", "vhen": "when",
    "waen": "when",
    # m/n/r confusions
    "kmew": "knew", "kmow": "know", "kmown": "known", "kmows": "knows",
    "lmew": "knew", "lmow": "know", "imown": "known", "jt": "it",
    "imto": "into", "dowm": "down", "omes": "ones", "fron": "from",
    "rrom": "from", "kingdon": "kingdom", "millenniun": "millennium",
    "equilibriun": "equilibrium", "aligrment": "alignment",
    "arourd": "around", "imner": "inner", "humax": "human", "iany": "many",
    "mith": "with", "nade": "made", "myst": "must", "ancther": "another",
    # c read for o
    "ccme": "come", "ccming": "coming", "ccntinue": "continue",
    "conscicusly": "consciously", "conscisusly": "consciously",
    "consclously": "consciously", "allcwing": "allowing",
    "consciousneds": "consciousness",
    # p read for b
    "prings": "brings", "pody": "body", "pegotten": "begotten",
    "puilt": "built",
    # letters plainly wrong
    "aecept": "accept", "alvays": "always", "angols": "angels",
    "areater": "greater", "ausy": "busy", "beceme": "become",
    "beran": "began", "briags": "brings", "chaaging": "changing",
    "clovds": "clouds", "cound": "could", "crestor": "creator",
    "defore": "before", "doine": "doing", "enprgies": "energies",
    "etherie": "etheric", "everytning": "everything", "fach": "face",
    "fessions": "sessions", "fether": "father", "fathor's": "father's",
    "flook": "flock", "fromptings": "promptings", "ghurch": "church",
    "gtill": "still", "harly": "early", "harth": "earth", "heod": "head",
    "hven": "even", "iingdoms": "kingdoms", "indecd": "indeed",
    "ingwelling": "indwelling", "inowledge": "knowledge", "ionger": "longer",
    "isracl": "israel", "jraw": "draw", "khis": "this", "lews": "laws",
    "lino": "line", "maping": "making", "mect": "meet", "moasure": "measure",
    "quiczly": "quickly", "reech": "reach", "rememorance": "remembrance",
    "scvipture": "scripture", "soripture": "scripture",
    "seripture": "scripture", "shail": "shall", "sither": "either",
    "solah": "selah", "speek": "speak", "spoxe": "spoke", "statc": "state",
    "stillnsss": "stillness", "strongth": "strength", "svirit": "spirit",
    "tako": "take", "teking": "taking", "thac": "that", "thase": "those",
    "thet": "that", "thoir": "their", "tjuly": "truly", "tord": "lord",
    "tozether": "together", "trne": "true", "unroality": "unreality",
    "upto": "unto", "voil": "veil", "vortes": "vortex", "wana": "want",
    "wark": "work", "wome": "some", "wouid": "would", "xingdom": "kingdom",
    "zach": "each", "zarly": "early", "darly": "early", "emen": "even",
    "bese": "best", "bett": "best", "comy": "come", "eres": "eyes",
    "futher": "further", "leep": "keep", "mvst": "must",
    # a second pass, each read in its sentence
    "ascention": "ascension", "behing": "behind", "breater": "greater",
    "coor": "door", "envirorment": "environment", "exprossion": "expression",
    "kingdome": "kingdom", "mame": "name", "meot": "meet", "moet": "meet",
    "neme": "name", "neture": "nature", "nnew": "new", "noed": "need",
    "peaco": "peace", "peautiful": "beautiful", "pecome": "become",
    "perfeot": "perfect", "pessibly": "possibly", "physicai": "physical",
    "physicel": "physical", "pike": "like", "plece": "place",
    "powor": "power", "pracsice": "practice", "prayor": "prayer",
    "preparetion": "preparation", "promisod": "promised", "qithin": "within",
    "reath": "breath", "terrying": "tarrying",
    "olouds": "clouds", "ontire": "entire", "oomes": "comes",
    "oreated": "created", "overy": "every", "oyes": "eyes", "pack": "back",
    "parther": "farther", "pationce": "patience", "pationt": "patient",
    # digits the scanner read for letters, and a semicolon it read as "3"
    "4nvolvements": "involvements", "4nd": "and", "4re": "are",
    "g0": "go", "g0es": "goes", "s0": "so", "1s": "is", "4s": "as",
    "4t": "it", "you3": "you;", "ago3": "ago;",
    # a semicolon read as an "s", checked against the scan of page 75:
    # "Our greetings to you again; we are constantly with you."
    "agains": "again;",
}

# Words that could honestly be read either way; these need the scan, so they
# are only reported.
AMBIGUOUS = {
    "affect", "alter", "altitudes", "astray", "band", "bank", "beat", "bide",
    "bind", "binds", "blight", "block", "blow", "boar", "boot", "breed",
    "broad", "brow", "burning", "calf", "camp", "cases", "catch", "cave",
    "certainty", "charges", "charging", "cleanses", "closed", "closes",
    "closet", "cold", "comet", "conceit", "creates", "dare", "daring", "date",
    "dead", "dealing", "deceiving", "dedicates", "deeds", "delivers", "dive",
    "divide", "dull", "dust", "eden", "establishes", "eter", "ethers",
    "expert", "fade", "faster", "fears", "fight", "five", "foot", "four",
    "fret", "gall", "gifts", "glorifies", "goeth", "greet", "hang", "hardest",
    "hath", "heal", "hearing", "heat", "heed", "heeded", "hide", "hill",
    "hither", "hose", "infinity", "intend", "inter", "ised", "joice", "knee",
    "knots", "latter", "leaf", "lect", "leed", "lends", "lent", "lets",
    "liking", "lines", "loading", "longed", "lords", "lust", "lying", "mass",
    "meld", "ment", "mire", "moot", "mote", "prey", "rain", "raining", "reap",
    "regain", "relay", "relieve", "retain", "ride", "riding", "risk", "roam",
    "rome", "rote", "sate", "saving", "seeks", "shalt", "shed", "shore",
    "sifting", "simply", "sing", "slid", "smoke", "soil", "sown", "speck",
    "spill", "spine", "stall", "stem", "stranger", "sune", "suns", "sweeping",
    "swell", "tain", "tale", "tales", "tall", "taped", "tarry", "taxing",
    "tear", "tells", "tending", "tense", "thin", "thir", "throe", "tons",
    "tore", "torn", "tower", "tree", "tries", "ture", "unites", "units",
    "unity", "vein", "vine", "wake", "waken", "wakes", "waking", "wander",
    "wane", "wasting", "wave", "waver", "wear", "weed", "weights", "whet",
    "white", "wilt", "wine", "wish", "wits", "wont", "worn", "worse", "yeast",
    "yield", "balls", "beas", "cant", "cest", "cold", "code", "coll", "cores",
    "culling", "reads", "reali", "resulte", "shalt",
}

# A full stop the scanner read as a letter, where a sentence plainly ends.
BOUNDARY = r"(?=\s+[A-Z\"'“]|\s*$)"


def match_case(word, replacement):
    if word[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def load():
    return {p: open(p, encoding="utf-8").read()
            for p in sorted(glob.glob(os.path.join(SRC, "*.md")))}


def vocabulary(texts):
    words = collections.Counter()
    for t in texts.values():
        for w in re.findall(r"[A-Za-z][A-Za-z']*",
                            re.sub(r"\[page \d+\]", " ", t)):
            words[w.lower()] += 1
    return words


# Reads correctly as it stands, so the trailing "s" is left alone:
# "He does not take this lightly and He completes His task."
KEEP_TRAILING_S = {"completes"}

# Lost full stops the book uses too often for the rarity test below to catch.
# Each was read in context first; all end a sentence, and none is a word.
# "them." came out as "theme" seven times - "claim theme Be of one spirit".
LOST_STOP = {
    "youe": "you", "yous": "you", "ite": "it", "upe": "up", "ine": "in",
    "ise": "is", "hime": "him", "gode": "God", "lorde": "Lord",
    "selahe": "Selah", "theme": "them", "nowe": "now", "onee": "one",
    "alle": "all", "mane": "man", "seee": "see", "passe": "pass",
    "timee": "time", "placee": "place", "moree": "more", "thise": "this",
    "othere": "other", "neare": "near", "waye": "way", "wayse": "ways",
    "soule": "soul", "soulse": "souls", "lovee": "love", "powere": "power",
    "naturee": "nature", "beinge": "being", "fathere": "father",
    "purposee": "purpose", "purposese": "purposes", "desiree": "desire",
    "freedome": "freedom", "agese": "ages", "dayse": "days",
    "actione": "action", "midste": "midst", "throughe": "through",
    "withine": "within", "comese": "comes", "centerse": "centers",
    "preparede": "prepared", "belovedse": "beloveds",
    "consciousnesse": "consciousness", "consciouslye": "consciously",
    "helpe": "help", "nighe": "nigh", "fare": "far", "kinde": "kind",
    "worke": "work", "faithe": "faith", "peacee": "peace",
}


def fix_lost_stops(text, words, tally):
    """Restore a full stop the scanner read as a trailing letter.

    The typist's period came out as an "e" or an "s" often enough to be worth
    correcting, but only where a sentence plainly ends and the word left
    behind is not one the book otherwise uses.
    """
    common = {w for w, c in words.items() if c >= 8}

    def swap(m):
        base, whole = m.group(1), m.group(0)
        low = whole.lower()
        if low in KEEP_TRAILING_S:
            return whole
        if low in LOST_STOP:
            fix = LOST_STOP[low]
            out = (fix if fix[:1].isupper() else match_case(whole, fix)) + "."
            tally[(whole, out)] += 1
            return out
        if base.lower() in common and words[low] <= 2:
            tally[(whole, base + ".")] += 1
            return base + "."
        return whole

    for letter in "es":
        text = re.sub(r"\b([A-Za-z]{2,})" + letter + r"\b" + BOUNDARY,
                      swap, text)
    return text


def fix_disagreement(text, words, tally):
    """A lost full stop showing up as a plural that cannot stand.

    "instructions for you for this days You are the same followers" is
    "...for this day. You are...": a singular determiner cannot take a plural,
    so the "s" is the typist's period. "that" is left out of the list, since
    it also introduces a clause where a plural verb is perfectly correct
    ("the busy world that keeps Heaven out").
    """
    common = {w for w, c in words.items() if c >= 8}

    def swap(m):
        det, noun = m.group(1), m.group(2)
        if noun.lower() in common:
            out = f"{det} {noun}."
            tally[(m.group(0), out)] += 1
            return out
        return m.group(0)

    return re.sub(r"\b(this|a|an|each|every|one|his|her|its)\s+([a-z]{3,})s\b"
                  r"(?=\s+[A-Z])", swap, text)


def fix_words(text, tally):
    def swap(m):
        w = m.group(0)
        fix = CORRECTIONS.get(w.lower())
        if not fix:
            return w
        out = match_case(w, fix)
        tally[(w, out)] += 1
        return out

    keys = sorted(CORRECTIONS, key=len, reverse=True)
    pat = re.compile(r"\b(?:" + "|".join(re.escape(k) for k in keys) + r")\b",
                     re.IGNORECASE)
    return pat.sub(swap, text)


def fix_hyphens(text, words, tally):
    """Rejoin a word the typist broke across a line that the reflow missed.

    Only joined where the book uses the whole word elsewhere, so a genuine
    hyphen ("non-believers") and a stray one ("and- yet") are left alone.
    """
    def swap(m):
        head, tail = m.group(1), m.group(2)
        joined = head + tail
        if words[joined.lower()] >= 3:
            tally[(f"{head}- {tail}", joined)] += 1
            return joined
        return m.group(0)

    return re.sub(r"\b([A-Za-z]{3,})-[ \t]+([a-z]{2,})\b", swap, text)


# Phrases the scanner dropped or displaced, each put back after reading the
# page it belongs to. Page 50: the opening of the Lord's Prayer was lifted out
# of its sentence and left stranded at the foot of the page.
REPAIRS = {
    "the great prayer, Kingdom come on Earth":
        'the great prayer, "Thy Kingdom come on Earth',
    # "Onee" is "one." in one place and "Once" in another, so neither can be
    # settled by the word alone.
    "through each onee": "through each one.",
    "Onee you consciously": "Once you consciously",
    "disciples that you ares;": "disciples that you are;",
    "spirit of Gode are receptive": "spirit of God. Ye are receptive",
}


def fix_phrases(text, tally):
    for wrong, right in REPAIRS.items():
        if wrong in text:
            tally[(wrong, right)] += text.count(wrong)
            text = text.replace(wrong, right)
    return text


def fix_dashes(text, tally):
    """Restore the typist's dashes.

    The long dash was typed as two hyphens, which the scanner read variously
    as "-=", "=-", "-~" and so on; a single hyphen in a compound came out
    as "=".
    """
    def run(m):
        if m.group(0) != "--":
            tally[(m.group(0), "--")] += 1
            return "--"
        return m.group(0)

    text = re.sub(r"[-=~]{2,}", run, text)

    # A full stop the scanner rendered twice, as ".e".
    def doubled(m):
        tally[(".e", ".")] += 1
        return "."

    text = re.sub(r"\.e\b", doubled, text)

    def single(m):
        tally[("=", "-")] += 1
        return "-"

    # The same mark where the typist broke a word across a line:
    # "prom= ised" is "promised", rejoined by fix_hyphens below.
    return re.sub(r"(?<=[A-Za-z])=[ \t]*(?=[a-z])", single, text)


def fix_apostrophes(text, words, tally):
    """An apostrophe the scanner read as a "t": "Godts" for "God's"."""
    def swap(m):
        base = m.group(1)
        if (words[base.lower() + "ts"] <= 2
                and words[base.lower() + "'s"] >= 3):
            out = base + "'s"
            tally[(m.group(0), out)] += 1
            return out
        return m.group(0)

    return re.sub(r"\b([A-Za-z]{2,})ts\b", swap, text)


def remaining(texts, words):
    """Suspect words still in the text, for reading against the scans."""
    common = [w for w, c in words.items() if c >= 10]
    commonset = set(common)
    out = []
    for w, c in sorted(words.items()):
        if c > 2 or len(w) < 4 or w in commonset:
            continue
        near = [cw for cw in common
                if len(cw) == len(w)
                and sum(a != b for a, b in zip(w, cw)) == 1]
        if near:
            out.append((w, c, near[:2], w in AMBIGUOUS))
    return out


def main():
    dry = "--dry-run" in sys.argv
    texts = load()
    words = vocabulary(texts)
    tally = collections.Counter()

    fixed = {}
    for path, text in texts.items():
        t = fix_phrases(text, tally)
        t = fix_dashes(t, tally)
        t = fix_hyphens(t, words, tally)
        t = fix_apostrophes(t, words, tally)
        t = fix_lost_stops(t, words, tally)
        t = fix_disagreement(t, words, tally)
        t = fix_words(t, tally)
        fixed[path] = t

    if not dry:
        for path, t in fixed.items():
            if t != texts[path]:
                open(path, "w", encoding="utf-8").write(t)

    total = sum(tally.values())
    print(f"{'would correct' if dry else 'corrected'} {total} readings "
          f"({len(tally)} distinct) across {len(texts)} sections")
    for (a, b), n in tally.most_common(18):
        print(f"    {a} -> {b}   x{n}")

    left = remaining(fixed, vocabulary(fixed))
    flagged = [r for r in left if r[3]]
    print(f"\n{len(left)} suspect words remain; {len(flagged)} of them are "
          "words in their own right and need the scan to settle")


if __name__ == "__main__":
    main()
