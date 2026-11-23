# Independent story re-run, session 40 (2026-11-23)

Reviewers: a fresh Claude session (Orca worker) that did not translate, reading B00-B27 itself, plus six fresh
read-only forks for B28-B33, B34-B39, A0-A3, A4-A7, A8-A12 and the sys sheets. Every sheet in
work/qa/story/chapters was read in full, JP against EN, with glossary.md binding. Per-slice findings:
indep_s40_<slice>.tsv (V = chapter verdict, F = fix). Every F line was checked against the JP and context by the
main session before it was applied (JP / old EN / new EN side by side: indep_s40_fixes_review.txt).
Verdicts: work/qa/story/verdicts/zz_indep_s40_20261123.tsv (65 sheets; qa_gate check exits 0).

## Fixes applied (38 rows; tools/set_en.py)

- B05.0244 "...that's what it was!!" -> "...that's what they are!!" (じゃァ is the copula)
- B10.0034 "Here. This is..." -> "Here, take this..."
- B11.0367 "If that hits us, we'll be!!" -> "we're done for!!"
- B18.0719 / 0726 typo "centerd" -> "centered"
- B32.0401 / 0402 dangling "whose" after "what you claim--": "prey whose Great Sins..." / "for this Amanosagume of yours!!"
- A0.6.0002 苦み走った = rugged, stern looks, not "bittersweet"
- A3.8.0029 / 0060 subjectless "find a gap": "my arts find a gap to slip through."
- A3.8.0068 / 0069 repeated "Thou hast admitted": "Thou art angry..." / "at the ugliness of the human world."
- A4.3.0002 dangling "you...?" -> "huh...?"
- A5.0.0048 "Not even I" -> "It's not like I" (オレだって...思ってない)
- A5.6.0043 broken pair: "humans human, you know."
- A6.7.0018/0022/0027/0032/0037 subject-verb comma removed; 0020/0039 "but nobody's got cause..."
- A6.7.0044 "his tail" -> "your tail"; A7.1.0044 "a frightening man" -> "a frightening one, you are." (D10: shared rows neutral)
- A7.5.0016 capital at sentence start; A7.6.0004 "he said" -> "she told me" (the clinic director is a woman)
- A7.7.0035 broken pair: "this rotten to the core."
- A10.5.0020/0024/0028 doubled "I think" removed
- A11.0.0000 "I'm one to talk" (= hypocrite) -> "maybe I shouldn't say this"; A11.7.0019 non-human speaker: "are what make humans human"
- CF2D6C "Silent Darkness" -> "Silent Dark" (card name CF6E24)
- D6A124 命により "By my orders" -> "On orders"; D6D364 "Is this blood too" -> "In the blood, too"
- D7011C / D70220 / D702BC rules-help tables: letter then icon (B/D/S + icon), as on the card face (CF6730/CF6708/CF66D0);
  re-shot on build 2851823e: work/qa/s40_rules f004980 (Bane), f005130 (Dodge), f005310 (Slay)
