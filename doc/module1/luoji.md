文件               │                     作用                     │
├─────────────────────────────────┼──────────────────────────────────────────────┤
│ scripts/ike_kupuna_module.py    │ Module 1 专属 OSEMN 分析主模块               │
├─────────────────────────────────┼──────────────────────────────────────────────┤
│ scripts/score_engine.py         │ 计算 ROOT_IKE 复合评分、输出 CSV             │
├─────────────────────────────────┼──────────────────────────────────────────────┤
│ scripts/seed_data_enterprise.py │ 生成种子数据（含 indicator_key=1 因果逻辑）  │
├─────────────────────────────────┼──────────────────────────────────────────────┤
│ scripts/seed_data.py            │ 早期种子数据脚本（已被 enterprise 版替代）   │
├─────────────────────────────────┼──────────────────────────────────────────────┤
│ scripts/archmage_refinement.py  │ 初始化 cfg_indicator_weights 权重配置        │
├─────────────────────────────────┼──────────────────────────────────────────────┤
│ scripts/patch_data_gaps.py      │ Phase 1 数据修补（indicator_key=1 相关缺口） │
├─────────────────────────────────┼──────────────────────────────────────────────┤
│ scripts/patch_data_gaps_p2.py   │ Phase 2 数据修补                             │
├─────────────────────────────────┼──────────────────────────────────────────────┤
│ scripts/seed_reflections.py     │ 生成文化反思文本（NLP 分析素材）              │
└─────────────────────────────────┴──────────────────────────────────────────────┘

---

# Module 1 Logic Review: Data Science Perspective

This report evaluates the analytics logic within the `'Ike Kūpuna` (Ancestral Wisdom) module, specifically examining `scripts/ike_kupuna_module.py` and `scripts/score_engine.py`.

## Summary of Findings

Overall, the module implements a structured OSEMN pipeline (Obtain, Scrub, Explore, Model, iNterpret) that is transparent and well-documented. However, from a rigorous data science perspective, there are several "unperceived errors" and logical pitfalls that could lead to biased reporting or misleading insights.

### 1. 因果推断与偏差 (Causal Inference & Selection Bias)
Interpretation 环节基于 T-检验（参与者 vs 非参与者）得出了文化项目有“显著效果”的结论。

> [!WARNING]
> **逻辑谬误：相关性 $\neq$ 因果性**
> 在教育观察数据中，选择参加夏威夷语或 Hula 的学生通常本身就具有更高的文化认约度（Baseline）。如果不控制这些基准差异（Selection Bias），将得分差距完全归功于项目是一个严重的统计误区。

**建议：** 采用拟实验方法（如 Propensity Score Matching）来分离真正的“干预效果”。

### 2. 评分逻辑中的重复计算 (Double-Counting)
目前的综合评分公式为：
$$Score = 60\% \times Base + 25\% \times Bonus + 15\% \times Wellbeing$$

*   **Base Score:** 已经包含了参加项目带来的能力提升。
*   **Bonus Points:** 直接奖励给参加同一项目的学生。

**问题：** 参加项目的学生在同一活动上被“奖励了两次”。这会人为拔高活跃学生的得分，而可能掩盖了那些能力达标但因客观原因无法参加课外项目的学生。

### 3. 权重科学性与“数学修饰” (Variance Compression)
`Wellbeing Adjustment` 组件被严重稀释：
1.  Wellbeing 原始分（0-100）被映射到 -10 到 +10 的区间。
2.  该区间再乘以 15% 的权重。

**结果：** 最终 100 分的量表上，Wellbeing 的极端差异（0分 vs 100分）仅能贡献 **3分**。这使得该指标在等级评估（Proficiency Classification）中几乎完全失效。

### 4. 缺失数据的基准偏移 (Baseline Shift)
在 `ike_kupuna_module.py` 中，缺失的 wellbeing 数据被自动填充为中位数 **50**。

**影响：** 这会导致一个没有任何表现数据的学生依然能获得 **6分**（$40 \times 0.15 = 6$）的“保底分”，从而产生虚假的数据底座。

### 5. NLP 局限性
关键词提取采用简单的正则匹配，无法识别否定句（如 *"I did not feel mana"* 会被计入正面词频）。同时，它高度依赖预生成的 Sentiment Label，缺乏对新文本的动态情感分析能力。

### 6. 数据清洗中的幸存者偏差 (Survivorship Bias)
直接剔除“严重异常”的学生（如缺失分的学生）而不分析其缺失原因，会导致分析结果仅反映了“表现良好且数据完整”的群体，从而高估了总体的平均水平。

-------
## fix

---
  What was done

  P1 — Issue 2: Double-counting (Critical Bug) ✅

  scripts/score_engine.py and scripts/ike_kupuna_module.py:
  - Removed program_bonus from WEIGHTS entirely
  - New formula: Score = 0.70 × Base_Score + 0.30 × Wellbeing_Score
  - Base score already encodes programme participation effects via the causal seed model — the old 25% bonus channel
   was rewarding the same effect twice

  P2 — Issue 3: Wellbeing variance compression ✅

  Both files now use wb_cultural × 0.30 directly (raw 0–100 scale), replacing the previous compressed
  ((score-50)/50)×10 formula in score_engine.py and the inconsistent raw-50 midpoint fallback in
  ike_kupuna_module.py. Both modules now use the same formula.

  P2 — Issue 4: Baseline shift from missing wellbeing ✅

  When wb_cultural is NULL/missing: wellbeing_contribution = 0.0 and wellbeing_missing = True is flagged on the
  record. The old code silently imputed 50 (gifting 7.5 phantom points to every unmatched student).

  P2 — Issue 6: Survivorship bias logging ✅

  scripts/ike_kupuna_module.py: Added dropped_records_log attribute populated in scrub() — tracks total dropped,
  drop rate %, reasons, and affected student keys. Included in the JSON report under
  data_quality.dropped_records_log and printed in the CLI output.

  scripts/score_engine.py: Added dropped_log dict after the cleaning step, printed to console and saved in
  anomaly_report.json.

  P3 — Issue 1: Selection bias caveat ✅

  ui/ike_kupuna_dashboard.html: Added a ⚠️ Selection Bias Caveat note in the Programme Impact section explaining
  that t-test comparisons are unadjusted for pre-existing baseline differences (self-selection). Updated formula
  chip and anatomy bar to reflect the new 70/30 split with a v2 change callout.

  Next verification steps

  To regenerate composite scores with the corrected formula, run:
  python scripts/seed_data_enterprise.py   # regenerate DB
  python scripts/ike_kupuna_module.py      # check composite mean shifts (expect ~lower)
  python scripts/score_engine.py           # verify alignment