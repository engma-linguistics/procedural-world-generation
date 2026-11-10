---
title: "Language contact: the run's trade triggers make nearly all contact between peoples count as trade"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: s
impact: med
found_by: lang-lane13
blocked_by: []
relates: [PW-1636, PW-1561]
refs: ["planet/language/inputs.py::Run._trade_triggers", "planet/language/history.py::History.loan_kinds", "planet/language/contact.py::RAW", "planet/language/contact.py::TRADE_NUMERALS", "run a24559", "run de1cc6"]
---

## Description
In plain words: lane 13 (PW-1636) made borrowing depend on who lends the word: rulers, traders, or plain
neighbours. On a24559 the "trader" label covers more loans than plain neighbours do (56,700 trade loans against
46,400 neighbour loans and 18,900 from rulers; de1cc6: 55,300 / 35,000 / 22,400). Most of it comes from the run's
trade triggers (`inputs.Run._trade_triggers`): any two peoples that share enough cells for TRADE_SHIFT_KYR get one,
and many last the whole window ("the aarakocra and dwarf shared land from 20.0 to 0.0 kyr ago"). On a24559, 4,697
of the 7,935 contact layers the living languages record are such triggers. So "trade" now means "a neighbour of
another people", not "a trading partner".

Today this is mild: the trade profile only raises commerce, goods and drink and lowers body and kin words. What breaks
if it is never done: the day desk card p.numerals switches the trade numerals on (`contact.TRADE_NUMERALS`), HUNDRED
and THOUSAND will be borrowed from almost every neighbour of another people, not from trading partners, and a
Swahili-like numeral layer will be everywhere instead of on trade coasts.

What I'd try: count as trade only (a) trade triggers whose pair also has trade-route traffic (crop, herd or technology
hand-overs between the two peoples, `History.partners`), or (b) the pairs with a market town or city on their shared
cells; keep the long shared-land pairs as plain neighbours. Measure the trade/neighbour split on a24559 and de1cc6.
- [ ] trade loans fewer than neighbour loans on both test worlds
- [ ] the trade numerals hook, switched on in a scratch pass, lifts HUNDRED/THOUSAND loans mostly where routes run
