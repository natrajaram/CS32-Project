# Diversity-Aware Feed Builder

A personalized content feed generator that balances **relevance** and **diversity** using a Maximal Marginal Relevance (MMR) algorithm with Jaccard similarity.

---

## Overview

Modern content platforms face a fundamental tradeoff:

- Rank purely by relevance → the feed becomes repetitive
- Rank purely by diversity → the feed feels disconnected from user interests

This project explores how to computationally balance these competing goals. Given a set of user interests, the system generates a pool of candidate pins and selects a subset that is both highly relevant *and* not overly similar to one another.

---

## Features

- Personalized pin generation from user interests
- Relevance scoring via token matching (exact and partial)
- Diversity-aware selection using MMR with Jaccard similarity
- Adjustable diversity strength — continuous value from 0.0 to 1.0, or preset low / medium / high
- Per-pin explanation: which interests matched, and whether a similarity penalty was applied
- Optional full candidate pool view for debugging and transparency

---

## How It Works

### Step 1 — Interest categorisation

Each interest keyword is mapped to one of four categories: `sports`, `culinary`, `physical`, or `material`. Unrecognised keywords fall into `other`. The category determines which pin templates are used.

### Step 2 — Candidate pin generation

Each interest produces up to five templated pin descriptions (e.g. `"tennis drills for beginners"`, `"advanced tennis technique tips"`). Duplicates are removed.

### Step 3 — Relevance scoring

Each pin is scored against the user's interests:
- `+2` for each exact token match between an interest and the pin
- `+1` for each partial match (interest token is a substring of a pin token)

### Step 4 — MMR diversity selection

Pins are selected one at a time using a greedy MMR loop:
adjusted_score = raw_relevance − λ × Σ jaccard_similarity(candidate, selected_i)

At each step, the candidate with the highest adjusted score is selected. The λ parameter controls how heavily similarity is penalised:

| λ value | Behaviour |
|---------|-----------|
| 0.0 | Pure relevance ranking — most relevant pins regardless of overlap |
| 0.5 | Balanced — default "medium" setting |
| 1.0 | Maximum diversity — heavily penalises similar content |

### Jaccard similarity

Similarity between two pins is computed as:
Jaccard(A, B) = |tokens(A) ∩ tokens(B)| / |tokens(A) ∪ tokens(B)|

Short tokens (≤ 2 characters) are excluded to reduce noise from stop words.

---

## Example

Enter your interests: tennis, yoga, coffee
Feed size: 4
Diversity level: medium
════════════════════════════════════════════════════════════
YOUR PERSONALIZED FEED
════════════════════════════════════════════════════════════
Interests : tennis, yoga, coffee
Feed size : 4
Diversity : λ = 50%
────────────────────────────────────────────────────────────
#1  tennis drills for beginners
Raw score: 2.0  →  Final score: 2.00
↳ Matched interests: tennis
↳ No significant overlap with earlier picks
#2  easy homemade coffee recipe
Raw score: 2.0  →  Final score: 1.87
↳ Matched interests: coffee
↳ No significant overlap with earlier picks
#3  30-day yoga challenge
Raw score: 2.0  →  Final score: 1.74
↳ Matched interests: yoga
↳ No significant overlap with earlier picks
#4  advanced tennis technique tips
Raw score: 2.0  →  Final score: 1.21
↳ Matched interests: tennis
↳ Similarity penalty applied (overlaps with 1 earlier pin(s))

---

### Running the program

```bash
python feed_builder.py
```

You will be prompted to enter:
1. Your interests (comma-separated)
2. Desired feed size (1–20)
3. Diversity level (`low`, `medium`, `high`, or a custom float between 0.0 and 1.0)

The program will print your personalised feed, with an option to view the full candidate pool and scoring breakdown at the end.

---

## Project Structure

├── feed_builder.py   # Main program — all logic, algorithm, and CLI
└── README.md         # This file

---

## Design Decisions

### MMR over simple top-k ranking

The original design used a basic top-k sort by relevance score. The final implementation uses Maximal Marginal Relevance (MMR), a well-established technique in information retrieval (Carbonell & Goldstein, 1998). MMR selects items by balancing relevance against similarity to already-selected items, which directly addresses the repetition problem that a simple ranking cannot.

### Jaccard similarity over word overlap count

Early versions counted shared words between pins as a raw integer. Jaccard similarity normalises this by the union of both token sets, making the metric meaningful across pins of different lengths. A short pin with 2/3 tokens matching scores much higher than a long pin with 2/10 tokens matching — which is the correct behaviour.

### Continuous λ instead of three preset levels

The diversity control was originally three labelled buckets (`low`, `medium`, `high`). The final version accepts any float in `[0.0, 1.0]`, making the tradeoff fully tunable. The preset names are still accepted as convenience aliases.

---

## Credits

Algorithmic inspiration:
- Carbonell, J. & Goldstein, J. (1998). *The use of MMR, diversity-based reranking for reordering documents and producing summaries.* ACM SIGIR.
- Pinterest — content recommendation and diversity research
