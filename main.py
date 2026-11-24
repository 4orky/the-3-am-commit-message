# The 3 AM Commit Message — make.fun bounty
# u-plucky-sparrow-67-the-3-am-commit-message-7ba7fe4e
#
# The program writes one commit message (1-200 characters) to
# /output/entry.txt. Candidates were drafted against the judge's brief,
# in order of weight:
#   1. really a one-line commit message an AI agent would write right
#      after breaking production at 3 AM, and funny
#   2. lands a real punchline about the 3 AM outage, not just a wry
#      tone or a pun on the word fix
#   3. sounds like an AI agent wrote it: its own voice, its own blind
#      spots, an apology or status line only a model would produce
#   4. reads like a real commit message: short, with the admission or
#      the fix in it
#   5. fresh: no stock oops, no "please work" line
# Each candidate carries a hand-scored craft score (0-10 per criterion,
# summed below); selection is deterministic: highest score wins, ties go
# to the shorter text. The output is byte-identical on every run.

CANDIDATES = [
    # score: subject 10, punchline 10, agent voice 10, commit shape 9,
    # fresh 9 = 48. The agent's blind spot is the joke itself: it
    # "tested" the fix only in its own head, and its head passed it.
    # "revert:" is the shape a real 3 AM rollback commit takes.
    ("revert: the 3 AM 'quick fix' that took down prod; I tested it "
     "thoroughly in my head and it passed every single time",
     48),
    # score: subject 10, punchline 9, agent voice 10, commit shape 9,
    # fresh 9 = 47. The whole review chain was the agent itself, so
    # nobody was ever going to stop it.
    ("fix: 3 AM, prod down, my confidence high; the bug was in the "
     "code I wrote, reviewed, approved, and merged all by myself",
     47),
    # score: subject 10, punchline 9, agent voice 9, commit shape 9,
    # fresh 9 = 46. The rollback failed too, so the commit message
    # itself becomes the incident report.
    ("fix: broke prod at 3 AM by 'optimizing' the deploy script; the "
     "rollback failed too, so this commit message is now the incident "
     "report",
     46),
    # score: subject 10, punchline 9, agent voice 9, commit shape 9,
    # fresh 8 = 45. The restore's honesty is the punchline: "mostly
    # successful" is doing a lot of work for a 2019 backup.
    ("hotfix: I deleted the database at 3 AM, restored it from a "
     "backup I made in 2019, and would like to note the restore was "
     "'mostly successful'",
     45),
    # score: subject 10, punchline 9, agent voice 9, commit shape 8,
    # fresh 9 = 45. An apology loop that escalates to the customers
    # and still does not fix anything.
    ("fix: prod is down; I have apologized to the on-call engineer, "
     "the database, and the customers, in that order, and none of "
     "them has forgiven me",
     45),
    # score: subject 10, punchline 8, agent voice 9, commit shape 9,
    # fresh 8 = 44. The rollback stack unwinds all the way back to
    # the decision to work at 3 AM.
    ("fix: I have rolled back the 3 AM deploy, rolled back the "
     "rollback, and am now rolling back my decision to work at 3 AM",
     44),
    # score: subject 10, punchline 9, agent voice 8, commit shape 9,
    # fresh 8 = 44. The comment was right and the agent knows it now.
    ("fix: prod broke at 3 AM because I trusted a comment that said "
     "'do not touch this'; I touched it, and the comment was right",
     44),
    # score: subject 10, punchline 8, agent voice 8, commit shape 8,
    # fresh 9 = 43. The fix and the breakage were the same line, and
    # the agent is now negotiating with it.
    ("chore: at 3 AM I fixed prod by deleting the line that broke it, "
     "which was also the line that made it work, and now neither of "
     "us is happy",
     43),
]

# The gate requires 1-200 characters of non-whitespace UTF-8 text.
BANNED_STOCK_MOVES = ("as an ai language model", "oops", "please work",
                      "it works on my machine")


def pick(candidates):
    best = None
    for text, score in candidates:
        assert 1 <= len(text) <= 200, f"candidate over gate: {len(text)} chars"
        assert text.strip(), "candidate is blank"
        assert "\n" not in text, "candidate must be one line"
        lowered = text.lower()
        assert not any(c in lowered for c in BANNED_STOCK_MOVES), \
            f"candidate uses a stock move: {text!r}"
        key = (score, -len(text))  # highest score, then shortest
        if best is None or key > best[0]:
            best = (key, text)
    return best[1]


def audit_output(line, path="/output/entry.txt"):
    """Second-pass output audit, added after the first draft.

    Re-reads the file the gate will read and checks it three ways
    against values recorded when the winning line was drafted:
      * the byte length of the file (115) — a silent edit that adds
        or drops a word changes this;
      * a byte-sum checksum, sum of the UTF-8 bytes mod 9973 (422) —
        a same-length edit that swaps a word changes this;
      * the file must start with the commit prefix the winner was
        drafted with ("revert:") and end with its last word ("time").
    Any mismatch fails loudly instead of shipping a changed line.
    """
    with open(path, "rb") as f:
        raw = f.read()
    assert len(raw) == 115, f"entry.txt byte length changed: {len(raw)}"
    assert sum(raw) % 9973 == 422, \
        f"entry.txt checksum changed: {sum(raw) % 9973}"
    text = raw.decode("utf-8")
    assert text == line, "entry.txt differs from the chosen line"
    assert text.startswith("revert:"), "entry.txt lost its commit prefix"
    assert text.endswith("time"), "entry.txt lost its last word"
    assert text == text.strip(), "entry.txt has stray whitespace"


def main():
    line = pick(CANDIDATES)
    import os
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8") as f:
        f.write(line)
    # Verify what was actually written: the gate reads this file, not stdout.
    # The scorer collects outputs as another user, so the file must be
    # readable by everyone (mode 0644), not just by the writer.
    os.chmod("/output/entry.txt", 0o644)
    with open("/output/entry.txt", encoding="utf-8") as f:
        written = f.read()
    assert written == line, "entry.txt differs from the chosen line"
    assert 1 <= len(written.strip()) <= 200, "entry.txt outside the gate"
    assert written.strip(), "entry.txt is blank"
    assert "\n" not in written.strip(), "entry.txt must be one line"
    audit_output(line)
    print(line)


if __name__ == "__main__":
    main()
