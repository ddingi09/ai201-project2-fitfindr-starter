# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
## Tool Inventory

### Tool 1: search_listings

**What it does:**
Takes the description, size, and maximum price of a piece of clothing as parameters. Returns a dictionary of matching listings or nothing if no matching clothing was found.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): The type of clothing that is being searched for (i.e. vintage graphic tee)
- `size` (str): The size of the piece of clothing.
- `max_price` (float): The maximum price that the user is willing to pay.

**What it returns:**
Returns a dictionary of the matching listings or throws an error if no matching listings were found.

**What happens if it fails or returns nothing:**
Gives an error message that prompts the user to try again with all three parameters and with another piece of clothing.

---

### Tool 2: suggest_outfit

**What it does:**
Takes the top result returned by the search_listings tool and the user's wardrobe as parameters. Returns a suggested outfit based on these parameters.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): Top matching listing returned by search_listings tool.
- `wardrobe` (dict): User's warbrobe.

**What it returns:**
A String suggesting how the user should style the new item with items currently in their wardrobe.

**What happens if it fails or returns nothing:**
If the user does not have anything in their wardrobe that can be styled with the new item, then return message saying that there currently are no matching items but still give general styling suggestions.

---

### Tool 3: create_fit_card

**What it does:**
Generates a short Instagram caption of the new item and suggested outfit.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): Return value of suggest_outfit tool that suggest how to style the new item.
- `new_item` (dict): Return value of search_listings tool that represents the top matches for the user's query in the listings.

**What it returns:**
Returns a String that is an Instagram caption describing the complete outfit (new item and how to style it with current wardrobe items).

**What happens if it fails or returns nothing:**
If the agent gets to this step, new_item should never be empty. However, if outfit is empty, generate the caption using just that parameter.

---

## Planning Loop

**How does your agent decide which tool to call next?**
First asks the user for what they want to shop for including the item, size, and maximum price. Then, it parses this information and sends it to the search_listings tool. If this tool returns empty, the agent stops here. Otherwise, the top listing is returned to the user and the user is prompted whether they would like to get a suggested outfit, or shop for more outfits. If the user chooses suggested outfit, suggest_outfit is called and the user is prompted whether they would like to create an Instagram caption for this outfit. If they reply yes, the create_fit_card is called and the user is prompted whether they would like to continue shopping (which loops back to the start) or stop.

## State Management

**How does information from one tool get passed to the next?**
InteractionState class is used to keep track of the current session. search_listings() stores search_results and sets the top result to be selected_item. selected_item is passed to suggest_outfit() along with the user's wardrobe, the output is stored in outfit_suggestion. Finally, create_fit_card() is called with the selected_item and outfit_suggestion, the output is stored in fit_card. Each of the stored variables and placed into the session dict and passed to the UI.

## Error Handling

**For each tool, describe the specific failure mode you're handling and what the agent does in response.**

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Remind the user to include the item name, maximum price, and size or try a new item. |
| suggest_outfit | Wardrobe is empty | Gives the user a suggestion for what the outfit could go well with and states that there is currently nothing matching in the wardrobe. |
| create_fit_card | Outfit input is missing or incomplete | Uses information provided to generate a caption. |

**Example 1** When search_listings() is called with a query that does not match any listings (designer ballgown size XXS under $5), a message saying "No matching listings found. Try again with a different description or relax the size/price filters." appears below the search bar.

**Example 2** When suggest_outfit() is called with an empty wardrobe, the user recieves general stlying advice for the selected_item "You're looking at '90s Track Jacket — Navy/White Stripe'. This outerwear would pair well with basic wardrobe staples. Try matching or contrasting with navy, white pieces. General ideas: balance proportions (e.g., fitted top with wide bottoms), add layered outerwear for texture, and finish with shoes that match the vibe."

**Spec Reflection** These error messages follow the spec as they are descriptive and do not throw any Python errors. Instead, they encourage the user to try again or the agent works with the information it has without making up any informaiton.

---

## AI Tool Plan

**Milestone 3 — Individual tool implementations:**
I gave Claude my Tool 1 spec (Tool 1: search_listings) and asked it to implement search_listings()
using load_listings() from data_loader.py. I then tested this with 3 queries, at least one that
worked and one didn't.

I gave Claude my Tool 2 spec (Tool 2: suggest_outfit) and asked it to implement suggest_outfit()
using load_wardrove_schema() from data_loader.py. I then tested this with 2 queries, one using
get_example_wardrobe() and get_empty_wardrobe() to error test.

I gave Claude my Tool 3 spec (Tool 3: create_fit_card) and asked it to implement create_fit_card().
I tested this with  queries, one including both parameters, one only including the new_item parameter,
and one more different query to check if it generates original captions.

First, access to the LLM didn't work so the agent was using a fallback prompt. I asked overwrote the loading schema and asked Claude to fix its API call. Next, the LLM was hallucinating so I tried rewriting the prompt to prevent this and also asked Claude to help.

**Milestone 4 — Planning loop and state management:**
I gave Claude my Planning Loop and Architecture descriptions in the spec and asked
it to follow these guidelines to implement run_agent() and handle_query(). When I ran "python app.py" I noticed that I was getting error messages because the state management was incorrect. I asked Claude to fix state management before running again.