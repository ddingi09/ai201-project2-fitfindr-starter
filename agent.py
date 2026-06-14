"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import re
from tools import search_listings, suggest_outfit, create_fit_card


# ── parsing ───────────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    """
    Parse a natural language query to extract description, size, and max_price.

    Uses regex to find:
    - max_price: "under $30", "$30", "30", etc.
    - size: "size M", "size XL", "M/L", etc.
    - description: everything else

    Returns a dict with keys: description, size, max_price
    (values may be None if not found).
    """
    parsed = {
        "description": None,
        "size": None,
        "max_price": None,
    }

    # Remove common filler words
    q = query.lower()

    # Extract max_price (patterns: "under $30", "$30", "max $30", etc.)
    price_match = re.search(r'(?:under|up to|max|price.{0,5})?\$?(\d+(?:\.\d{2})?)', q)
    if price_match:
        try:
            parsed["max_price"] = float(price_match.group(1))
        except Exception:
            pass

    # Extract size (patterns: "size M", "size XL", "M/L", "small", "medium", etc.)
    size_match = re.search(r'size\s+([xXsSmMlL]{1,3}(?:/[xXsSmMlL]{1,3})?)', q, re.IGNORECASE)
    if not size_match:
        # Fall back to full size words (small, medium, large, extra large, etc.)
        size_match = re.search(r'\b(small|medium|large|extra\s+large|xs|xl|xxl)\b', q, re.IGNORECASE)
    if size_match:
        parsed["size"] = size_match.group(1).upper()

    # Extract description: remove size and price info, keep the rest
    # Remove "size XX" patterns
    desc = re.sub(r'size\s+[xXsSmMlL]{1,3}(?:/[xXsSmMlL]{1,3})?', '', q, flags=re.IGNORECASE)
    # Remove price indicator words and numbers (e.g., "under $30", "max $50", "$40")
    desc = re.sub(r'\b(?:under|up\s+to|max|price|paid)\s*\$?\d+(?:\.\d{2})?', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'\$\d+(?:\.\d{2})?', '', desc)
    # Remove standalone price indicator words
    desc = re.sub(r'\b(?:under|up\s+to|max|price)\b', '', desc, flags=re.IGNORECASE)
    # Remove size words
    desc = re.sub(r'\b(small|medium|large|extra\s+large)\b', '', desc, flags=re.IGNORECASE)
    # Remove common filler words
    desc = re.sub(r'\b(?:looking for|i\'m looking|search|find|want|need|looking|for|a|an|the)\b', '', desc, flags=re.IGNORECASE)
    # Clean up extra spaces
    desc = re.sub(r'\s+', ' ', desc).strip()
    # Remove punctuation cruft
    desc = desc.strip(',.!?;:-')

    if desc:
        parsed["description"] = desc

    return parsed


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.

    Planning loop (from planning.md):
        Step 1: Initialize session.
        Step 2: Parse query to extract description, size, max_price.
        Step 3: Call search_listings() with parsed params.
                If no results → set error and return early.
        Step 4: Select top result as selected_item.
        Step 5: Call suggest_outfit() with selected_item and wardrobe.
        Step 6: Call create_fit_card() with outfit_suggestion and selected_item.
        Step 7: Return session.
    """
    # Step 1: Initialize session
    session = _new_session(query, wardrobe)

    # Step 2: Parse the query
    session["parsed"] = _parse_query(query)

    # Step 3: Search for listings
    try:
        session["search_results"] = search_listings(
            description=session["parsed"]["description"],
            size=session["parsed"]["size"],
            max_price=session["parsed"]["max_price"],
        )
    except Exception as e:
        # search_listings raises ValueError if no results match
        session["error"] = str(e)
        return session

    # Step 4: Select the top result
    if not session["search_results"]:
        session["error"] = "No listings found. Try including the item name, maximum price, and size or try a different item."
        return session

    session["selected_item"] = session["search_results"][0]

    # Step 5: Get outfit suggestion
    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=wardrobe,
    )

    # Step 6: Generate fit card caption
    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"],
    )

    # Step 7: Return the completed session
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
