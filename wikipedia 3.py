import re
import wikipediaapi

# Initialize Wikipedia API with your user agent
wiki = wikipediaapi.Wikipedia('Areola/1.0 (cleefrookie@gmail.com)', 'en')

# Predefined Q&A dictionary with regex patterns for strict matching
responses = {
    r"^\bhi\b$": "Yo, what's good, my man?",
    r"^\bhow are you\b$": "I'm vibin' like a true AI, dawg! What's up with you?",
    r"^\bwhat is the weather like\?\b$": "No windows here, but tell me your spot and I’ll guess... or not!",
    r"^\btell me a joke\b$": "Why did the scarecrow win an award? He was outstanding in his field!",
    r"^\bwho made you\?\b$": "Cleef Rookie and Grok AI built me to drop knowledge and keep it real!",
    r"^\bwhat is your name\?\b$": "I’m Areola, your smooth-talkin’ AI, ready to chat, my man!",
    r"^\bwhat can you do\?\b$": "I can chat about almost anything, crack jokes, or pull facts from Wikipedia! Ask me stuff like 'who’s the president?' or '!wiki [topic]' for deep dives."
}

# Hardcoded knowledge base for critical facts (as of June 17, 2025)
knowledge_base = {
    "president of the united states": "As of June 17, 2025, the President of the United States is Donald Trump, serving his second term since January 20, 2025.",
    "vice president of the united states": "The Vice President of the United States is JD Vance, sworn in on January 20, 2025.",
    "first lady of the united states": "The First Lady of the United States is Melania Trump, as of January 20, 2025.",
    "leader of congress": "The Speaker of the House is Mike Johnson, and the Senate Majority Leader is John Thune, leading Congress as of 2025.",
    "trump": "Donald Trump is the 47th President of the United States, serving his second term since January 20, 2025. He’s a businessman, former reality TV star, and leads the Trump Organization.",
    "capital of france": "The capital of France is Paris, known for its culture, art, and landmarks like the Eiffel Tower."
}

# Map common questions to knowledge base keys or Wikipedia page titles
question_mappings = {
    r"who('s| is)?\s*(the)?\s*president\s*(of\s*(the)?\s*(usa|united states|america))\??": "president of the united states",
    r"who('s| is)?\s*(the)?\s*vice president\s*(of\s*(the)?\s*(usa|united states|america))\??": "vice president of the united states",
    r"who('s| is)?\s*(the)?\s*first lady\s*(of\s*(the)?\s*(usa|united states|america))\??": "first lady of the united states",
    r"who('s| is)?\s*(the)?\s*leader\s*(of\s*(the)?\s*congress)\??": "leader of congress",
    r"what('s| is)?\s*(the)?\s*capital\s*(of\s*(.*))\??": r"\4",  # Extract country/state
    r"who('s| is)?\s*(.*)\??": r"\2",  # Extract person/topic
    r"what('s| is)?\s*(.*)\??": r"\2",  # Extract general topic
    r"what('s| is)?\s*(the)?\s*deal\s*with\s*(.*)\??": r"\3"  # Handle "what’s the deal with X?"
}

# Store last topic for basic context tracking
last_topic = None

def normalize_query(query):
    """Normalize user input: strip punctuation, handle synonyms, and extract key terms."""
    query = query.lower().strip().rstrip('?.,!')
    # Replace synonyms
    query = re.sub(r'\b(usa|america|united states of america)\b', 'united states', query)
    query = re.sub(r'\s+', ' ', query).strip()  # Collapse spaces
    return query

def extract_key_terms(query):
    """Extract key nouns or topics from a query for better matching."""
    # Remove common question words
    query = re.sub(r'\b(who|what|where|when|why|how|is|are|the|a|an|of|in|on|at)\b', '', query)
    query = re.sub(r'\s+', ' ', query).strip()
    return query

def get_wikipedia_summary(query, context=None):
    global last_topic
    try:
        # If query is empty or too vague, use context if available
        if not query and context:
            query = context

        # Check knowledge base first
        if query in knowledge_base:
            last_topic = query  # Update context
            return knowledge_base[query]
        
        # Try Wikipedia page
        page = wiki.page(query)
        if page.exists():
            summary = re.sub(r'\[.*?\]', '', page.summary)
            last_topic = query  # Update context
            return f"Here’s the scoop on '{page.title}' from Wikipedia:\n{summary[:500]}..."
        
        # Try variations
        variations = [query, query.title(), query.capitalize()]
        for var in variations:
            page = wiki.page(var)
            if page.exists():
                summary = re.sub(r'\[.*?\]', '', page.summary)
                last_topic = query  # Update context
                return f"Here’s the scoop on '{page.title}' from Wikipedia:\n{summary[:500]}..."
        
        return f"Yo, I’m drawing a blank on '{query}'. Try rephrasing or ask about something like '{last_topic}' if you’re still curious!"
    except Exception as e:
        return f"Oops, Wikipedia’s acting up: {str(e)}. Try again, my man!"

def chatbot_response(user_input):
    global last_topic
    # Normalize input
    user_input_normalized = normalize_query(user_input)
    
    # Check for predefined responses
    for pattern, answer in responses.items():
        if re.match(pattern, user_input_normalized, re.IGNORECASE):
            return answer
    
    # Check for explicit Wikipedia command
    if user_input_normalized.startswith('!wiki'):
        query = user_input[5:].strip()
        if query:
            return get_wikipedia_summary(normalize_query(query))
        return "Yo, give me something to search for after '!wiki'!"

    # Check for follow-up questions (e.g., "what’s he doing now?" after "who is trump?")
    if re.match(r"what('s| is)?\s*(he|she|it|they)\s*(doing|up to)\??", user_input_normalized):
        if last_topic:
            return get_wikipedia_summary(last_topic, context=last_topic)
        return "Yo, I need some context! Ask about someone or something first."

    # Check for question mappings
    for pattern, target in question_mappings.items():
        match = re.match(pattern, user_input_normalized, re.IGNORECASE)
        if match:
            query = match.group(4 if 'capital' in pattern else 3 if 'deal' in pattern else 2) if match.group(2) else target
            return get_wikipedia_summary(normalize_query(query))
    
    # Fallback: extract key terms and try again
    key_terms = extract_key_terms(user_input_normalized)
    if key_terms:
        return get_wikipedia_summary(normalize_query(key_terms))
    
    return f"Yo, I’m not quite catching '{user_input}'. Try something like 'who’s the president?' or '!wiki [topic]'!"

def main():
    print("Welcome to Areola, your smooth-talkin’ bot! Type 'quit' to bounce.", flush=True)
    print("Ask me anything, like 'who’s the president?' or '!wiki [topic]' for Wikipedia facts!", flush=True)
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Areola: Peace out, my man!")
            break
        response = chatbot_response(user_input)
        print(f"Areola: {response}")

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")