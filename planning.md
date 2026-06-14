# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

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

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
First asks the user for what they want to shop for including the item, size, and maximum price. Then, it parses this information and sends it to the search_listings tool. If this tool returns empty, the agent stops here. Otherwise, the top listing is returned to the user and the user is prompted whether they would like to get a suggested outfit, or shop for more outfits. If the user chooses suggested outfit, suggest_outfit is called and the user is prompted whether they would like to create an Instagram caption for this outfit. If they reply yes, the create_fit_card is called and the user is prompted whether they would like to continue shopping (which loops back to the start) or stop.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
InteractionState class is used to keep track of the current session. search_listings() stores search_results and sets the top result to be selected_item. selected_item is passed to suggest_outfit() along with the user's wardrobe, the output is stored in outfit_suggestion. Finally, create_fit_card() is called with the selected_item and outfit_suggestion, the output is stored in fit_card. Each of the stored variables and placed into the session dict and passed to the UI.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Remind the user to include the item name, maximum price, and size or try a new item. |
| suggest_outfit | Wardrobe is empty | Gives the user a suggestion for what the outfit could go well with and states that there is currently nothing matching in the wardrobe. |
| create_fit_card | Outfit input is missing or incomplete | Uses information provided to generate a caption. |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->
User query
    │
    ▼
Planning Loop ───────────────────────────────────────────┐
    │                                                    │
    ├─► search_listings(description, size, max_price)    │
    │       │ results=[]                                 │
    │       ├──► [ERROR] "No listings found. Try including the item 
                         description, size, and max price or try a
                         different item!" → return
    │       │                                            ^
    │       │ results=[item, ...]                        │
    │       ▼                                            │
    │   Session: selected_item = results[0]              |
    |   Session: "Would you like to get a suggested outfit or 
                 continue shopping?"
    │       │                                            │
    ├─► suggest_outfit(selected_item, wardrobe)          │
    │       │                                            │
    │   Session: outfit_suggestion = "..." 
        Session: "Would you like an Instagram caption for your outfit?"
            |"no"
            ├──► return
    │       │                                            │
    └─► create_fit_card(outfit_suggestion, selected_item)│
            │                                            │
        Session: fit_card = "..."
        Session: "Would you like to continue shopping?"
            |"no"
            ├──► return       
            │                                            └─ error path returns here
            ▼
        Prompt User Query Again
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
I'll give Claude my Tool 1 spec (Tool 1: search_listings) and ask it to implement search_listings()
using load_listings() from data_loader.py. I will then test this with 3 queries, at least one that
will work and one that won't.

I'll give Claude my Tool 2 spec (Tool 2: suggest_outfit) and ask it to implement suggest_outfit()
using load_wardrove_schema() from data_loader.py. I will then test this with 2 queries, one using
get_example_wardrobe() and get_empty_wardrobe() to error test.

I'll give Claude my Tool 3 spec (Tool 3: create_fit_card) and ask it to implement create_fit_card().
I will test this will  queries, one including both parameters, one only including the new_item parameter,
and one more different query to check if it generates original captions.

**Milestone 4 — Planning loop and state management:**
I'll give Claude my Planning Loop, State Management, and Architecture descriptions in the spec and ask
it to follow these guidelines to generate effective state management and prompting.
---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
First, the agent creates a new session and parses the user query. From the example query, it would extract vintage graphic tee, max price of $30, and an empty size field. It would call search_listings ("vintage graphic tee", max_price=30.0).

**Step 2:**
Step 1 returns the top result that was found or nothing. In the latter case, FitFindr will stop running and suggest a different option to the user. Otherwise, it will call suggest_outfit(new_item=<output of step 1>, wardrobe=<user's wardrobe>). The new_item parameter is the dictionary of the top result that was returned in Step 1 and the wardrobe parameter is called via a load wardrobe function.

**Step 3:**
Calls create_fit_card(outfit=<suggest_outfit output>, new_item=<output of step1>). This will return an Instagram caption style description of the outfit that was created using the return values of the previous two steps.

**Final output to user:**
If the queried piece of clothing is found in the listings, the user sees a full output of a String from Step 2 suggesting how to style their outfit and an Instagram caption from Step 3. If not, the user sees an error message that details what they can do to get a result.
