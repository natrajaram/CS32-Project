"""
feed_builder.py
---------------
Diversity-Aware Feed Builder

Generates a personalized content feed that balances relevance and diversity
using a Maximal Marginal Relevance (MMR) algorithm with Jaccard similarity.

Inspired by recommendation systems used in platforms like Pinterest.

"""

# ---------------------------------------------------------------------------
# Category dictionaries
# Each list maps keywords to a content category used for pin generation.
# ---------------------------------------------------------------------------

CATEGORY_MAP: dict[str, list[str]] = {
    "sports": [
        "tennis", "basketball", "soccer", "football", "baseball",
        "volleyball", "golf", "swimming", "skiing", "snowboarding",
        "boxing", "wrestling", "cricket", "rugby", "track", "cycling",
        "climbing", "hiking",
    ],
    "culinary": [
        "food", "cooking", "baking", "pasta", "coffee", "dessert",
        "cake", "bread", "smoothie", "recipe", "meal", "dinner",
        "lunch", "breakfast", "vegan", "vegetarian", "snacks", "sushi",
        "gluten free", "keto", "cookies", "ice cream", "pizza",
    ],
    "physical": [
        "fitness", "workout", "gym", "lifting", "running", "cardio",
        "pilates", "yoga", "exercise", "training", "stretching",
        "abs", "strength", "meditation",
    ],
    "material": [
        "fashion", "clothes", "outfits", "style", "shoes", "streetwear",
        "accessories", "jewelry", "bags", "photography", "runway",
    ],
}

# Pin templates per category — each interest generates several candidate pins.
PIN_TEMPLATES: dict[str, list[str]] = {
    "sports":   [
        "{w} drills for beginners",
        "advanced {w} technique tips",
        "{w} training plan 8 weeks",
        "best {w} gear guide",
        "{w} warm-up routine",
    ],
    "culinary": [
        "easy homemade {w} recipe",
        "best {w} spots in your city",
        "{w} for beginners",
        "healthy {w} ideas",
        "{w} masterclass tips",
    ],
    "physical": [
        "30-day {w} challenge",
        "{w} routine for beginners",
        "{w} for weight loss",
        "{w} core exercises",
        "advanced {w} training",
    ],
    "material": [
        "{w} outfit ideas for spring",
        "{w} style inspiration",
        "trending {w} looks 2024",
        "budget {w} finds",
        "{w} wardrobe essentials",
    ],
    "other":    [
        "{w} for beginners",
        "{w} inspiration gallery",
        "best {w} resources",
        "getting into {w}",
        "{w} ideas to try",
    ],
}

DIVERSITY_PRESETS = {"low": 0.2, "medium": 0.5, "high": 0.8}


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def categorize_interest(word: str) -> str:
    """Return the category of a keyword, or 'other' if unrecognised."""
    word = word.lower().strip()
    for category, keywords in CATEGORY_MAP.items():
        if word in keywords:
            return category
    return "other"


def tokenize(text: str) -> set[str]:
    """
    Split text into a set of lowercase tokens, filtering short stop-words.
    Short words (≤2 characters) are excluded to avoid noise in similarity scoring.
    """
    return {w.lower() for w in text.split() if len(w) > 2}


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """
    Compute Jaccard similarity between two strings based on token overlap.

    Jaccard(A, B) = |A ∩ B| / |A ∪ B|

    Returns a float in [0, 1]: 0 means no overlap, 1 means identical token sets.
    """
    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    intersection = tokens_a & tokens_b
    return len(intersection) / len(union)


def score_relevance(pin: str, interests: list[str]) -> tuple[float, list[str]]:
    """
    Score a pin's relevance to the user's interests using token matching.

    Scoring rules:
        +2  for each exact interest token found in the pin
        +1  for each partial match (interest word appears as substring of a pin token)

    Returns:
        score   — numeric relevance score (higher is more relevant)
        matches — list of interest tokens that contributed to the score
    """
    pin_tokens = tokenize(pin)
    score = 0.0
    matches: list[str] = []

    for interest in interests:
        interest_tokens = tokenize(interest)

        for tok in interest_tokens:
            if tok in pin_tokens:
                score += 2
                matches.append(tok)
            else:
                # Partial match: interest token appears inside a pin token
                for pin_tok in pin_tokens:
                    if tok in pin_tok and tok not in matches:
                        score += 1
                        matches.append(tok)
                        break

    return score, matches


# ---------------------------------------------------------------------------
# Pin generation
# ---------------------------------------------------------------------------

def generate_candidate_pins(interests: list[str]) -> list[str]:
    """
    Generate a pool of candidate pins from the user's interests.

    Each interest produces several templated pin strings based on its category.
    Duplicates are removed while preserving insertion order.
    """
    pins: list[str] = []
    seen: set[str] = set()

    for word in interests:
        category = categorize_interest(word)
        templates = PIN_TEMPLATES.get(category, PIN_TEMPLATES["other"])

        for template in templates:
            pin = template.format(w=word)
            if pin not in seen:
                pins.append(pin)
                seen.add(pin)

    return pins


# ---------------------------------------------------------------------------
# Core MMR algorithm
# ---------------------------------------------------------------------------

def build_feed(
    interests: list[str],
    feed_size: int,
    diversity_lambda: float,
) -> list[dict]:
    """
    Select a diverse, relevant feed using Maximal Marginal Relevance (MMR).

    Algorithm:
        1. Score all candidate pins by relevance to the user's interests.
        2. Select pins one at a time:
           a. For each remaining candidate, compute an adjusted score:
              adjusted = relevance - λ × Σ sim(candidate, already_selected)
           b. Pick the candidate with the highest adjusted score.
           c. Add it to the selected set and repeat.

    Args:
        interests        — list of user interest keywords
        feed_size        — number of pins to select
        diversity_lambda — λ in [0, 1]; 0 = pure relevance, 1 = pure diversity

    Returns:
        List of dicts, each containing:
            pin           — pin text
            raw_score     — relevance score before diversity penalty
            final_score   — adjusted score after penalty
            matches       — interest tokens that matched this pin
            penalty_from  — list of (pin, similarity) pairs causing penalties
    """
    candidates = generate_candidate_pins(interests)

    if not candidates:
        return []

    # Step 1: compute raw relevance scores for all candidates
    scored = []
    for pin in candidates:
        raw_score, matches = score_relevance(pin, interests)
        scored.append({
            "pin": pin,
            "raw_score": raw_score,
            "final_score": raw_score,
            "matches": matches,
            "penalty_from": [],
        })

    selected: list[dict] = []
    remaining = list(scored)

    # Step 2: MMR selection loop
    while len(selected) < feed_size and remaining:

        # Recompute adjusted scores based on current selected set
        for candidate in remaining:
            penalty = 0.0
            penalty_from = []

            for sel in selected:
                sim = jaccard_similarity(candidate["pin"], sel["pin"])
                penalty += diversity_lambda * sim * candidate["raw_score"]
                if sim > 0.05:  # only record meaningful similarity contributions
                    penalty_from.append((sel["pin"], round(sim, 3)))

            candidate["final_score"] = candidate["raw_score"] - penalty
            candidate["penalty_from"] = penalty_from

        # Pick the candidate with the highest adjusted score
        remaining.sort(key=lambda c: c["final_score"], reverse=True)
        best = remaining.pop(0)
        selected.append(best)

    return selected


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_separator(char: str = "─", width: int = 60) -> None:
    print(char * width)


def print_feed(feed: list[dict], interests: list[str], diversity_lambda: float) -> None:
    """Pretty-print the final selected feed with per-pin explanations."""
    print_separator("═")
    print("  YOUR PERSONALIZED FEED")
    print_separator("═")
    print(f"  Interests : {', '.join(interests)}")
    print(f"  Feed size : {len(feed)}")
    print(f"  Diversity : λ = {diversity_lambda:.0%}")
    print_separator()

    for i, item in enumerate(feed, start=1):
        penalty_note = (
            f"  ↳ Similarity penalty applied (overlaps with {len(item['penalty_from'])} earlier pin(s))"
            if item["penalty_from"]
            else "  ↳ No significant overlap with earlier picks"
        )
        match_note = (
            f"  ↳ Matched interests: {', '.join(item['matches'])}"
            if item["matches"]
            else "  ↳ No direct keyword matches (category-based selection)"
        )

        print(f"\n  #{i}  {item['pin']}")
        print(f"       Raw score: {item['raw_score']:.1f}  →  Final score: {item['final_score']:.2f}")
        print(match_note)
        print(penalty_note)

    print()
    print_separator("═")


def print_full_scoring(
    interests: list[str],
    selected_pins: set[str],
    diversity_lambda: float,
) -> None:
    """Show the full candidate pool with raw scores for debugging/demo purposes."""
    candidates = generate_candidate_pins(interests)

    print_separator()
    print("  FULL CANDIDATE POOL (sorted by raw relevance)")
    print_separator()

    all_scored = []
    for pin in candidates:
        raw_score, _ = score_relevance(pin, interests)
        all_scored.append((pin, raw_score))

    all_scored.sort(key=lambda x: x[1], reverse=True)

    for pin, score in all_scored:
        status = "[SELECTED]" if pin in selected_pins else "[filtered]"
        bar = "█" * int(score * 2)
        print(f"  {status:<12} {score:>4.1f}  {bar:<20}  {pin}")

    print()


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def get_interests() -> list[str]:
    print("\n  Enter your interests (comma-separated, e.g. tennis, yoga, coffee):")
    raw = input("  > ").strip()
    interests = [w.strip().lower() for w in raw.split(",") if w.strip()]
    if not interests:
        print("  No interests detected — using defaults: tennis, yoga, coffee")
        return ["tennis", "yoga", "coffee"]
    return interests


def get_feed_size() -> int:
    raw = input("\n  How many pins in your feed? (default 5; between 1-20): ").strip()
    try:
        n = int(raw)
        return max(1, min(n, 20))  # clamp between 1 and 20
    except ValueError:
        return 5


def get_diversity_level() -> float:
    print("\n  Diversity level — how much to penalise similar content?")
    print("  Options: low (0.2) | medium (0.5) | high (0.8)")
    print("  Or enter a custom value between 0.0 and 1.0")
    raw = input("  > ").strip().lower()

    if raw in DIVERSITY_PRESETS:
        return DIVERSITY_PRESETS[raw]
    try:
        val = float(raw)
        return max(0.0, min(val, 1.0))  # clamp to [0, 1]
    except ValueError:
        print("  Unrecognised input — using medium (0.5)")
        return 0.5


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print_separator("═")
    print("  DIVERSITY-AWARE FEED BUILDER")
    print("  Balancing relevance and diversity")
    print_separator("═")

    # Gather user inputs
    interests = get_interests()
    feed_size = get_feed_size()
    diversity_lambda = get_diversity_level()

    # Show interest categorisation
    print()
    print_separator()
    print("  INTEREST CATEGORISATION")
    print_separator()
    for word in interests:
        cat = categorize_interest(word)
        print(f"  {word:<20} → {cat}")

    # Run the MMR feed builder
    feed = build_feed(interests, feed_size, diversity_lambda)

    if not feed:
        print("\n  No pins could be generated for the given interests.")
        return

    # Print results
    print_feed(feed, interests, diversity_lambda)

    # Optionally show full scoring pool
    show_pool = input("  Show full candidate scoring pool? (y/n): ").strip().lower()
    if show_pool == "y":
        selected_pins = {item["pin"] for item in feed}
        print_full_scoring(interests, selected_pins, diversity_lambda)

    print("  Done!\n")


if __name__ == "__main__":
    main()
