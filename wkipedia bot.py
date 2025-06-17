import re
import wikipediaapi
import wikipediaapi  # Added for search functionality

# Initialize Wikipedia API with your user agent
wiki = wikipediaapi.Wikipedia('Areola/1.0 (cleefrookie@gmail.com)', 'en')

# Predefined Q&A dictionary
responses = {
    r"^\bhi\b$": "Hello! What's good, my man?",
    r"^\bhow are you\b$": "I'm just a program, but thanks for asking! How can I assist you today?",
    r"^\bwhat is the weather like\?\b$": "I ain't got a window, but tell me your location and I'll guess... or not!",
    r"^\btell me a joke\b$": "Why did the scarecrow win an award? Because he was outstanding in his field!",
    r"^\bwho made you\?\b$": "I was brought to life by Cleef Rookie and Grok AI, a team of developers and AI enthusiasts. They created me to assist and entertain users like you!",
    r"^\bwhat is your name\?\b$": "I am Areola, your friendly neighborhood AI assistant!",
    r"^\bwhat can you do\?\b$": "I can answer questions, tell jokes, provide info from Wikipedia, and assist with various tasks. Try '!wiki [topic]' for Wikipedia info or just ask away!"
}

def get_wikipedia_summary(query):
    try:
        # First, try to search for the query to get a valid page
        search_results = wikipedia.search(query, results=1)
        if not search_results:
            return f"Sorry, I couldn't find anything on Wikipedia about '{query}'."
        
        page_title = search_results[0]
        page = wiki.page(page_title)
        
        if page.exists():
            # Remove Wikipedia references like [1], [2], etc.
            summary = re.sub(r'\[.*?\]', '', page.summary)
            return f"Here's what I found on Wikipedia about '{page_title}':\n{summary[:500]}..."
        else:
            return f"Sorry, I couldn't find a Wikipedia page for '{query}'."
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
    
    # If no predefined match, try Wikipedia
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