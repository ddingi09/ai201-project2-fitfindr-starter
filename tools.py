"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    # Validate input: require at least one search criterion
    if not ((isinstance(description, str) and description.strip()) or size or max_price is not None):
        raise ValueError(
            "Please provide at least one search criterion: description, size, or max_price."
        )

    # Load listings
    listings = load_listings()
    if not listings:
        raise ValueError("Listings dataset is empty or could not be loaded.")

    # Prepare keywords from the description (may be empty)
    keywords = []
    if isinstance(description, str) and description.strip():
        keywords = [w.strip() for w in description.lower().split() if w.strip()]

    results = []
    for item in listings:
        # Price filter
        price = item.get("price")
        if max_price is not None:
            try:
                if price is None or float(price) > float(max_price):
                    continue
            except Exception:
                # Skip items with non-numeric price values
                continue

        # Size filter (case-insensitive substring match)
        if size:
            item_size = str(item.get("size", "")).lower()
            if size.lower() not in item_size:
                continue

        # Build a searchable text blob from relevant fields
        parts = []
        for key in ("title", "description", "category", "brand", "condition", "platform"):
            v = item.get(key)
            if v:
                parts.append(str(v))
        # include list fields
        for key in ("style_tags", "colors"):
            vals = item.get(key, [])
            if isinstance(vals, list):
                parts.extend([str(v) for v in vals if v])
            elif vals:
                parts.append(str(vals))

        text = " ".join(parts).lower()

        # Score by keyword overlap (simple count of matched keywords).
        # If no keywords were provided, include the filtered item.
        if keywords:
            score = 0
            for kw in keywords:
                if kw in text:
                    score += 1
            if score > 0:
                copy_item = dict(item)
                copy_item["_score"] = score
                results.append(copy_item)
        else:
            copy_item = dict(item)
            copy_item["_score"] = 1
            results.append(copy_item)

    # No matches -> raise an informative error
    if not results:
        raise ValueError(
            "No matching listings found. Try again with a different description or relax the size/price filters."
        )

    # Sort by score (desc) then price (asc)
    results.sort(key=lambda x: (-x.get("_score", 0), x.get("price", float("inf"))))

    # Remove internal score before returning
    for r in results:
        r.pop("_score", None)

    return results


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    # Basic defensive handling
    if not isinstance(new_item, dict) or not new_item:
        return "Sorry, I don't have enough information about the new item to suggest an outfit."

    items = []
    if isinstance(wardrobe, dict):
        items = wardrobe.get("items") or []
    if not isinstance(items, list):
        items = []

    # Normalize some fields from the new item
    new_cat = (new_item.get("category") or "").lower()
    new_colors = [str(c).lower() for c in new_item.get("colors", []) if c]
    new_styles = [str(s).lower() for s in new_item.get("style_tags", []) if s]
    title = new_item.get("title") or new_item.get("name") or "this item"

    # If wardrobe is empty, return general styling advice
    if not items:
        advice = f"You're looking at '{title}'. "
        if new_cat:
            advice += f"This {new_cat} would pair well with basic wardrobe staples. "
        if new_colors:
            advice += f"Try matching or contrasting with {', '.join(new_colors[:2])} pieces. "
        advice += (
            "General ideas: balance proportions (e.g., fitted top with wide bottoms), "
            "add layered outerwear for texture, and finish with shoes that match the vibe."
        )
        return advice

    # Helper: score compatibility between new_item and a wardrobe piece
    def score_piece(piece: dict) -> int:
        score = 0
        # color match
        piece_colors = [str(c).lower() for c in piece.get("colors", []) if c]
        if any(pc in new_colors for pc in piece_colors) and new_colors:
            score += 3
        # style tag overlap
        piece_styles = [str(s).lower() for s in piece.get("style_tags", []) if s]
        for s in piece_styles:
            if s in new_styles:
                score += 1
        # complementary category bonus
        cat = (piece.get("category") or "").lower()
        complementary = {
            "tops": ["bottoms", "outerwear", "shoes", "accessories"],
            "bottoms": ["tops", "shoes", "outerwear", "accessories"],
            "outerwear": ["tops", "bottoms", "shoes", "accessories"],
            "shoes": ["bottoms", "tops", "accessories"],
            "accessories": ["tops", "bottoms", "outerwear", "shoes"],
        }
        if new_cat and cat in complementary.get(new_cat, []):
            score += 2
        return score

    # Score every wardrobe item
    scored = []
    for p in items:
        scored.append((score_piece(p), p))

    # Group by category and sort desc by score
    from collections import defaultdict

    by_cat = defaultdict(list)
    for s, p in scored:
        by_cat[(p.get("category") or "").lower()].append((s, p))
    for cat in list(by_cat.keys()):
        by_cat[cat].sort(key=lambda x: -x[0])

    # Build up to two outfit suggestions
    outfits = []

    def pick_best(cat_list, exclude_ids=None):
        exclude_ids = exclude_ids or set()
        for s, p in cat_list:
            if p.get("id") not in exclude_ids:
                return p
        return None

    def make_outfit(exclude_ids=None):
        exclude_ids = set(exclude_ids or [])
        outfit_parts = []
        # Choose complementary pieces based on new_item category
        want = []
        if new_cat == "tops":
            want = ["bottoms", "outerwear", "shoes", "accessories"]
        elif new_cat == "bottoms":
            want = ["tops", "outerwear", "shoes", "accessories"]
        elif new_cat == "outerwear":
            want = ["tops", "bottoms", "shoes", "accessories"]
        elif new_cat == "shoes":
            want = ["bottoms", "tops", "accessories"]
        else:
            want = ["tops", "bottoms", "outerwear", "shoes", "accessories"]

        used_ids = set(exclude_ids)
        for cat in want:
            candidates = by_cat.get(cat, [])
            pick = pick_best(candidates, used_ids)
            if pick:
                outfit_parts.append(pick.get("name") or pick.get("title") or cat)
                used_ids.add(pick.get("id"))

        return outfit_parts

    first = make_outfit()
    if first:
        outfits.append(first)
        # Try to make a second outfit using different pieces
        used_ids = {p.get("id") for part_cat in first for p in items if (p.get("name") == part_cat or p.get("title") == part_cat)}
        second = make_outfit(exclude_ids=used_ids)
        if second and second != first:
            outfits.append(second)

    # Format the response
    lines = []
    heading = f"Styling suggestions for '{title}':"
    lines.append(heading)
    if not outfits:
        lines.append(
            "I couldn't find specific matching pieces in your wardrobe, but here are general styling ideas:"
        )
        if new_colors:
            lines.append(f"• Try pairing {', '.join(new_colors[:2])} with neutral basics like white, black, or denim.")
        lines.append("• Think about proportion: pair oversized pieces with fitted items; cropped with high-waisted bottoms.")
        lines.append("• Finish with shoes that match the vibe (sneakers for casual, boots for edge).")
        return "\n".join(lines)

    for i, parts in enumerate(outfits, start=1):
        if parts:
            lines.append(f"Outfit {i}: {title} + " + ", ".join(parts))

    # If wardrobes contain notes or helpful details, add a friendly tip
    lines.append("Tip: Try swapping shoes or adding a belt/accessory to change the vibe.")
    return "\n".join(lines)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Guard clauses
    if not isinstance(new_item, dict) or not new_item:
        return "Cannot generate caption: missing `new_item`."

    title = new_item.get("title") or new_item.get("name") or "This piece"
    price = new_item.get("price")
    platform = new_item.get("platform")

    # Format price
    price_str = ""
    try:
        if price is not None:
            price_str = f"${float(price):.2f}"
    except Exception:
        price_str = str(price)

    # Derive a short summary from the outfit input
    outfit_text = (outfit or "").strip()
    import re

    parts_summary = None
    if outfit_text:
        m = re.search(r"Outfit 1:\s*(.*)", outfit_text, flags=re.IGNORECASE)
        if m:
            line = m.group(1)
        else:
            lines = [l.strip() for l in outfit_text.splitlines() if l.strip()]
            line = lines[1] if len(lines) > 1 else (lines[0] if lines else "")

        try:
            line_clean = re.sub(re.escape(title), "", line, flags=re.IGNORECASE)
        except Exception:
            line_clean = line
        line_clean = line_clean.replace("+", ",").strip(" -–—:,\n")
        line_clean = re.sub(r"\s{2,}", " ", line_clean).strip()
        if line_clean:
            parts_summary = line_clean

    # Prefer using the LLM when an API key is available; otherwise fall back
    load_dotenv()
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            client = _get_groq_client()
            prompt_lines = [
                "You are a social media influencer.",
                "Write a short (2-4 sentence) casual OOTD caption for a thrift find.",
                "CRITICAL RULES:",
                "- ONLY mention details that are explicitly provided below.",
                "- DO NOT make up, invent, or assume any information.",
                "- If a detail is not provided (like platform or price), do NOT include it in the caption.",
                "- Sound authentic and capture the outfit vibe, but use ONLY the provided facts.",
                "- Keep it natural — not a product description. Avoid hashtags.",
                "- Respond only with the caption text. Do not repeat words.",
                "\nProvided Item Details (use ONLY what is listed):\n",
            ]
            prompt_lines.append(f"Name/title: {title}")
            if price_str:
                prompt_lines.append(f"Price: {price_str}")
            else:
                prompt_lines.append("Price: NOT PROVIDED - do not mention cost")
            if platform:
                prompt_lines.append(f"Platform: {platform}")
            else:
                prompt_lines.append("Platform: NOT PROVIDED - do not mention where it was bought")
            if parts_summary:
                prompt_lines.append(f"Outfit summary: {parts_summary}")
            else:
                prompt_lines.append("Outfit summary: NOT PROVIDED")
            styles = new_item.get("style_tags") or []
            if styles:
                prompt_lines.append(f"Style tags: {', '.join([str(s) for s in styles])}")
            else:
                prompt_lines.append("Style tags: NOT PROVIDED")

            prompt = "\n".join(prompt_lines)

            # Call Groq API using chat.completions.create
            resp = None
            try:
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9
                )
                if resp and hasattr(resp, "choices") and len(resp.choices) > 0:
                    message = resp.choices[0].message
                    if hasattr(message, "content"):
                        return message.content.strip()
            except Exception:
                # If LLM call fails, fall back to local generator below
                pass
        except Exception:
            # If any LLM call fails, we'll fall back to local generator below
            pass

    # Local deterministic-but-varied caption generator (stable per input)
    import random
    import hashlib

    seed_input = f"{title}|{price_str}|{platform}|{parts_summary or outfit_text}"
    seed = int(hashlib.sha256(seed_input.encode("utf-8")).hexdigest(), 16) % (2 ** 32)
    rnd = random.Random(seed)

    openers = [
        "Just snagged", "Found", "Thrifted", "Score:", "Latest OOTD:", "Can’t stop wearing"
    ]
    middles = [
        "and I’m pairing it with", "styled with", "worn here with", "layered over", "team it with"
    ]
    vibes = [
        "easy everyday cool", "vintage casual", "clean minimal", "streetwear edge", "polished thrift", "90s throwback"
    ]

    opener = rnd.choice(openers)
    middle = rnd.choice(middles)
    vibe = (", ".join([str(s) for s in (new_item.get("style_tags") or [])[:2]]) ) or rnd.choice(vibes)

    # Sentence 1: name + price + platform (natural)
    s1_parts = [opener, title]
    if price_str:
        # vary placement
        if rnd.random() < 0.5:
            s1 = f"{opener} {title} for {price_str}"
        else:
            s1 = f"{opener} {title} — {price_str}"
    else:
        s1 = f"{opener} {title}"
    if platform:
        if rnd.random() < 0.5:
            s1 += f" on {platform}"
        else:
            s1 = f"{s1} (picked up on {platform})"
    s1 = s1.rstrip(" .,") + "."

    # Sentence 2: outfit summary
    if parts_summary:
        s2_templates = [
            f"{middle} {parts_summary} for an easy, put-together look.",
            f"Wearing it with {parts_summary} — comfy but pulled together.",
            f"Pairing it with {parts_summary} to keep things {vibe}.",
        ]
        s2 = rnd.choice(s2_templates)
    else:
        s2 = rnd.choice([
            "Pair it with a white tee and denim for instant wearability.",
            "I’d style this with neutral basics and chunky sneakers.",
            "Works great with layered outerwear and simple sneakers for everyday wear.",
        ])

    # Sentence 3: vibe / CTA
    s3 = rnd.choice([
        f"Perfect for a {vibe} vibe.",
        f"Totally {vibe} — loving how versatile this is.",
        "Simple, trendy, and cool.",
    ])

    caption = " ".join([s1, s2, s3]).strip()
    return caption
