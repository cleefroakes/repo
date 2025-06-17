import re
import wikipediaapi

# Initialize Wikipedia API with your user agent
wiki = wikipediaapi.Wikipedia('Areola/1.0 (cleefrookie@gmail.com)', 'en')

# Predefined Q&A dictionary with regex patterns for strict matching
responses = {
    r"^\bhi\b$": "Yo, what's good, my man?",
    r"^\bhow are you\b$": "I'm just a program, but I'm vibin'! What's up with you?",
    r"^\bwhat is the weather like\?\b$": "I ain't got a window, but tell me your spot and I'll guess... or not!",
    r"^\btell me a joke\b$": "Why did the scarecrow win an award? He was outstanding in his field!",
    r"^\bwho made you\?\b$": "Crafted by Cleef Rookie and Grok AI, I'm here to drop knowledge and keep it real!",
    r"^\bwhat is your name\?\b$": "I'm Areola, your go-to AI for facts and fun, my man!",
    r"^\bwhat can you do\?\b$": "I can answer almost anything, crack jokes, or hit you with Wikipedia facts! Try '!wiki [topic]' or ask me something like 'who's the president?'"
}

# Hardcoded knowledge base for critical facts (as of June 17, 2025)
knowledge_base = {
    "president of the united states": "As of June 17, 2025, the President of the United States is Donald Trump, serving his second term since January 20, 2025.",
    "vice president of the united states": "The Vice President of the United States is JD Vance, sworn in on January 20, 2025.",
    "first lady of the united states": "The First Lady of the United States is Melania Trump, as of January 20, 2025.",
    "leader of congress": "The Speaker of the United States House of Representatives is Mike Johnson, leading the House as of 2025. The Senate is led by the Majority Leader, currently John Thune, as of 2025."
}

# Map common general knowledge questions to Wikipedia page titles or knowledge base keys
question_mappings = {
    r"who('s| is) the president of (the )?(usa|united states)\??": "president of the united states",
    r"who('s| is) the vice president of (the )?(usa|united states)\??": "vice president of the united states",
    r"who('s| is) the first lady of (the )?(usa|united states)\??": "first lady of the united states",
    r"who('s| is) the leader of congress\??": "leader of congress",
    r"what('s| is) the capital of (.*)\??": r"\1",  # Extract country/state name
    r"who('s| is) (.*)\??": r"\2",  # Extract person/topic name
    r"what('s| is) (.*)\??": r"\2"   # Extract general topic
}

def normalize_query(query):
    """Normalize user input: strip punctuation, handle synonyms, and standardize."""
    query = query.lower().strip().rstrip('?.,!')
    # Replace synonyms
    query = re.sub(r'\b(usa|america)\b', 'united states', query)
    return query

def get_wikipedia_summary(query):
    try:
        page = wiki.page(query)
        if page.exists():
            # Remove Wikipedia references like [1], [2], etc.
            summary = re.sub(r'\[.*?\]', '', page.summary)
            return f"Here's the scoop on '{page.title}' from Wikipedia:\n{summary[:500]}..."
        else:
            # Try title case and other variations
            variations = [query, query.title(), query.lower(), query.upper()]
            for var in variations:
                page = wiki.page(var)
                if page.exists():
                    summary = re.sub(r'\[.*?\]', '', page.summary)
                    return f"Here's the scoop on '{page.title}' from Wikipedia:\n{summary[:500]}..."
            return f"Yo, I couldn't find '{query}' on Wikipedia. Try rephrasing or ask something else, my man!"
    except Exception as e:
        return f"Oops, Wikipedia's acting up: {str(e)}. Try again, my man!"

def chatbot_response(user_input):
    # Normalize input
    user_input_normalized = normalize_query(user_input)
    
    # Check for predefined responses
    for pattern, answer in responses.items():
        if re.match(pattern, user_input_normalized, re.IGNORECASE):
            return answer
    
    # Check for explicit Wikipedia command
    if user_input_normalized.startswith('!wiki'):
        query = user_input[5:].strip()  # Extract query after "!wiki"
        if query:
            return get_wikipedia_summary(normalize_query(query))
        return "Yo, give me something to search for after '!wiki'!"

    # Check for knowledge base or question mappings
    for pattern, target in question_mappings.items():
        match = re.match(pattern, user_input_normalized, re.IGNORECASE)
        if match:
            # If the pattern has a capture group, use it; otherwise, use the mapped target
            query = match.group(2) if match.group(2) else target
            # Check if the query is in the knowledge base
            if query in knowledge_base:
                return knowledge_base[query]
            return get_wikipedia_summary(query)
    
    # Fallback to Wikipedia for general queries
    return get_wikipedia_summary(user_input_normalized)

def main():
    print("Welcome to Areola, your all-knowing bot! Type 'quit' to bounce.", flush=True)
    print("Ask me anything, like 'who's the president?' or '!wiki [topic]' for Wikipedia facts!", flush=True)
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