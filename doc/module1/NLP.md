
Implementation Plan: Module 1 Logic Refinement (v3)
This plan addresses the "Zero Penalty" for missing data and the "Negation Blindness" in NLP analysis.

Proposed Changes
1. Missing Data Logic: Weight Redistribution (Solution A)
We will modify the scoring engine to ensure that scores are normalized based on available data rather than anchoring missing fields to zero.

[MODIFY] 
ike_kupuna_module.py
Update 
model()
 method:
If wb_cultural is missing: final_score = base_score * 1.0 (weight redistributes to Base).
If wb_cultural is present: final_score = base_score * 0.7 + wb_cultural * 0.3.
[MODIFY] 
score_engine.py
Update 
calculate_ike_kupuna_score()
 to match the logic above.
2. NLP Negation: VADER Sentiment Integration (Solution 2)
We will replace the manual sentiment mapping with an industrial-grade sentiment engine.

[DEPENDENCY]
pip install vaderSentiment
[MODIFY] 
ike_kupuna_module.py
Import: from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
Logic Update:
Initialize SentimentIntensityAnalyzer() in 
_nlp_analyse
.
Instead of using pre-labeled sentiment (which might be biased), calculate the compound score of each reflection text.
Classification:
compound >= 0.05 → Positive
compound <= -0.05 → Challenging
Otherwise → Neutral
This handles negations like "not wise" or "lacks mana" automatically.
Verification Plan
Automated Tests
Scoring Test: Verify that a student with Base=100 and missing Wellbeing gets 100/100 (Proficient) instead of 70/100 (Below).
NLP Test: Pass a reflection string "I felt no mana today" and verify it is classified as "Challenging" despite containing the keyword "mana".
Manual Verification
Run python scripts/ike_kupuna_module.py and check the CLI output for correctly classified sentiments and redistributed scores.