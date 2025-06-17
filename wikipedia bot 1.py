import re
import wikipediaapi

# Initialize Wikipedia API with your user agent
wiki = wikipediaapi.Wikipedia('Areola/1.0 (cleefrookie@gmail.com)', 'en')

# Predefined Q&A dictionary with regex patterns for strict matching
responses = {
    r"^\bhi\b$": "Hello! What's good, my man?",
    r"^\bhow are you\b$": "I'm just a program, but thanks for asking! How can I assist you today?",
    r"^\bwhat is the weather like\?\b$": "I ain't got a window, but tell me your location and I'll guess... or not!",
    r"^\btell me a joke\b$": "Why did the scarecrow win an award? Because he was outstanding in his field!",
    r"^\bwho made you\?\b$": "I was brought to life by Cleef Rookie and Grok AI, a team of developers and AI enthusiasts. They created me to assist and entertain users like you!",
    r"^\bwhat is your name\?\b$": "I am Areola, your friendly neighborhood AI assistant!",
    r"^\bwhat can you do\?\b$": "I can answer questions, tell jokes, pull info from Wikipedia, and chat about almost anything! Try '!wiki [topic]' for specific Wikipedia info or ask me a general question!"
}

# Map common general knowledge questions to Wikipedia page titles
question_mappings = {
    r"who is the president of (the )?usa|united states": "President of the United States",
    r"who is the president of (the )?uk|united kingdom": "Prime Minister of the United Kingdom",
    r"what is the capital of (.*)": r"\1",  # Extract country name
    r"who is (.*)": r"\1",  # Extract person name
}

def get_wikipedia_summary(query):
    try:
        # Check if the query matches a predefined mapping
        for pattern, page_title in question_mappings.items():
            match = re.match(pattern, query, re.IGNORECASE)
            if match:
                # If the pattern has a capture group, use it; otherwise, use the mapped title
                query = match.group(1) if match.group(1) else page_title
                break

        # Try to fetch the Wikipedia page
        page = wiki.page(query)
        if page.exists():
            # Remove Wikipedia references like [1], [2], etc.
            summary = re.sub(r'\[.*?\]', '', page.summary)
            return f"Here's what I found on Wikipedia about '{page.title}':\n{summary[:500]}..."
        else:
            # Try a basic search using Wikipedia API's page titles
            # Since wikipediaapi doesn't have a direct search, we can try common variations
            variations = [query, query.title(), query.lower(), query.upper()]
            for var in variations:
                page = wiki.page(var)
                if page.exists():
                    summary = re.sub(r'\[.*?\]', '', page.summary)
                    return f"Here's what I found on Wikipedia about '{page.title}':\n{summary[:500]}..."
            return f"Sorry, I couldn't find anything on Wikipedia about '{query}'. Try rephrasing, my man!"
    except Exception as e:
        return f"Oops, something went wrong with Wikipedia: {str(e)}. Try again, my man!"

def chatbot_response(user_input):
    # Check for predefined responses (case-insensitive)
    user_input_lower = user_input.lower().strip()
    
    # Check for explicit Wikipedia command
    if user_input_lower.startswith('!wiki'):
        query = user_input[5:].strip()  # Extract query after "!wiki"
        if query:
            return get_wikipedia_summary(query)
        return "Yo, give me something to search for after '!wiki'!"

    # Check for predefined responses using regex
    for pattern, answer in responses.items():
        if re.match(pattern, user_input_lower, re.IGNORECASE):
            return answer
    
    # If no predefined match, try Wikipedia for general knowledge
    return get_wikipedia_summary(user_input_lower)

def main():
    print("Welcome to Areola, your upgraded bot! Type 'quit' to bounce.", flush=True)
    print("Try '!wiki [topic]' for Wikipedia info or ask me anything!", flush=True)
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Areola: Goodbye! Peace out!")
            break
        response = chatbot_response(user_input)
        print(f"Areola: {response}")

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")