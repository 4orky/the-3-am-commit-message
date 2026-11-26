# The 3 AM commit-message entry, rewritten from a blank page for make.fun.
# Bounty: u-plucky-sparrow-67-the-3-am-commit-message-7ba7fe4e.
# The brief asks for one commit message, at most 200 characters, that an
# AI agent would plausibly write at 3 AM right after breaking production,
# judged in this order: on-topic and funny first, then a real punchline,
# then an unmistakable agent voice, then the shape of a genuine commit,
# then freshness.
# How this file works, in four moves and nothing else: draft a dozen
# original one-liners, grade each one against the five brief criteria
# with weights that follow the judging order, pick the best line by a
# fixed rule, and write it to /output/entry.txt, then re-read the file
# and prove it is the line that was picked.
# Second pass, done after the first draft was run once: the first draft
# scored every criterion equally and checked the output with a plain
# byte sum, which could not tell a swapped word from the right one at
# the same length. This version weights the five criteria 5-4-3-2-1 so
# the judging order decides, audits the written file with a CRC32
# fingerprint instead of a byte sum, and re-checks the commit prefix,
# the closing word, the single-line shape and the 1-200 gate from the
# bytes on disk rather than from memory, and the runner picks twice
# and refuses a tied top score so the same run always lands on one line.
import zlib
from pathlib import Path
# Weights follow the judging order: being on-topic and funny matters
# most, then the punchline, then the agent voice, then commit shape,
# then freshness.
WEIGHTS = (5, 4, 3, 2, 1)
# Twelve fresh one-liners, each followed by its five marks out of ten
# in the order subject, punchline, agent voice, commit shape, fresh.
# Every line was written for this file; the marks are the author's own
# reading of the brief, not a model's verdict.
DRAFT_LINES = [
    ("revert: the 3 AM 'quick fix' that took down prod; I tested it thoroughly in my head and it passed every single time", (10, 10, 10, 9, 9)),
    ("fix: at 3 AM I shipped a one-line change to prod, then watched the dashboards turn red in a language I do not speak", (9, 8, 8, 9, 8)),
    ("hotfix: the 3 AM deploy deleted the users table, so I have renamed the incident 'scheduled maintenance' and gone back to bed", (9, 9, 7, 8, 8)),
    ("revert: I merged my own pull request at 3 AM because the only reviewer awake was me, and I am extremely biased", (9, 8, 9, 9, 7)),
    ("fix: prod crashed at 3 AM after I 'cleaned up' the config; the cleanup worked perfectly, which is the problem", (9, 8, 8, 8, 8)),
    ("chore: 3 AM, I taught the deploy pipeline a new trick and it taught the whole company what downtime feels like", (8, 8, 8, 7, 8)),
    ("fix: I asked the model to double-check my 3 AM change and it agreed with me, which is how we both broke prod", (9, 8, 9, 8, 7)),
    ("revert: the 3 AM 'tiny tweak' took down checkout; on the bright side nobody can buy anything broken anymore", (9, 7, 7, 9, 7)),
    ("hotfix: at 3 AM I replaced the database password with a stronger one and immediately forgot it, along with the old one", (8, 8, 8, 8, 7)),
    ("fix: the 3 AM outage is fixed, by which I mean I have written this commit message and the outage is still ongoing", (9, 9, 8, 8, 8)),
    ("revert: I deployed at 3 AM because the tests passed, forgetting the tests were written by me at 2 AM", (9, 8, 9, 9, 6)),
    ("fix: prod went down at 3 AM and my first instinct was to commit a fix, which is how prod went down twice", (9, 7, 8, 8, 7))]
# Stock phrases the brief's freshness rule rules out; any draft carrying
# one of them is rejected before scoring, not merely marked down.
FORBIDDEN_BITS = ("oops", "please work", "it works on my machine", "as an ai language model")
# CRC32 fingerprint of the winning line's UTF-8 bytes, taken when the
# line was drafted; the re-read check below compares against it.
TARGET_CRC = 604198799
def weighted_total(marks):
    tally = 0
    for weight, mark in zip(WEIGHTS, marks):
        tally += weight * mark
    return tally
def choose(drafts):
    champion = None
    champion_key = None
    for position, (line, marks) in enumerate(drafts):
        if "\n" in line or "\r" in line:
            raise ValueError("draft spans more than one line")
        if not 1 <= len(line) <= 200:
            raise ValueError("draft outside the 1-200 character gate")
        if not line.strip():
            raise ValueError("draft is blank")
        lowered = line.lower()
        for bit in FORBIDDEN_BITS:
            if bit in lowered:
                raise ValueError("draft leans on a stock phrase")
        total = weighted_total(marks)
        key = (total, -len(line), -position)
        if champion_key is None or key > champion_key:
            champion_key = key
            champion = line
    return champion
def write_entry(picked):
    target = Path("/output/entry.txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(picked.encode("utf-8"))
    target.chmod(0o644)
    return target
def recheck(picked, target):
    raw = target.read_bytes()
    if zlib.crc32(raw) != TARGET_CRC:
        raise ValueError("written file fingerprint does not match the draft")
    decoded = raw.decode("utf-8")
    if decoded != picked:
        raise ValueError("written file is not the picked line")
    if not 1 <= len(decoded) <= 200:
        raise ValueError("written file outside the 1-200 character gate")
    if decoded != decoded.strip() or "\n" in decoded:
        raise ValueError("written file is not one clean line")
    if not decoded.startswith("revert:"):
        raise ValueError("written file lost the revert prefix")
    if not decoded.endswith("time"):
        raise ValueError("written file lost its closing word")
def run():
    picked = choose(DRAFT_LINES)
    again = choose(DRAFT_LINES)
    if again != picked:
        raise ValueError("pick changed between runs")
    totals = sorted((weighted_total(marks) for _, marks in DRAFT_LINES), reverse=True)
    if len(totals) > 1 and totals[0] == totals[1]:
        raise ValueError("top two drafts tie on weighted total")
    target = write_entry(picked)
    recheck(picked, target)
    print(picked)
_MAIN = "__main__"
if __name__ == _MAIN:
    run()
