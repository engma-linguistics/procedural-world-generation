p = 'planet/language/lect.py'
s = open(p, encoding='utf-8').read()
old = '''SIGNATURE_SKIP = frozenset({"tone", "hiatus", "epenthesis"})   # (tone and repairs are not a branch's mark; epenthesis feeds itself)'''
new = '''SIGNATURE_SKIP = frozenset({"tone", "hiatus", "epenthesis"})   # (tone and repairs are not a branch's mark; epenthesis feeds itself)
# One-off rows a branch may still take as its mark (PW-1647): wholesale final-consonant loss (S099), the way Polynesian
# lost the Proto-Oceanic finals (*ikan > iʻa) and Italian the Latin ones. As a signature it is not capped at one firing
# and the word-shape anchor does not resist it, so the branch goes open and stays open (its anchor follows the words).
# Before, under the anchor, a coda line reached open syllables only by luck: 0 of a24559's coda lines did on lane 14b.
SIGNATURE_ONE_OFFS = frozenset({"S099"})'''
assert old in s; s = s.replace(old, new)
old = '''            if r.weight <= 0 or r.family in SIGNATURE_SKIP or one_off(r) or b in have or not self.may_fire(r, kyr):'''
new = '''            if r.weight <= 0 or r.family in SIGNATURE_SKIP or (one_off(r) and b not in SIGNATURE_ONE_OFFS) or b in have \\
                    or not self.may_fire(r, kyr):'''
assert old in s; s = s.replace(old, new)
old = '''        if one_off(rule) and len(h) >= ONE_OFF_MAX:
            return False'''
new = '''        if one_off(rule) and len(h) >= ONE_OFF_MAX and not any(s["rule"] == b for s in self.signatures):
            return False   # (a one-off the branch took as its signature keeps firing: SIGNATURE_ONE_OFFS)'''
assert old in s; s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
