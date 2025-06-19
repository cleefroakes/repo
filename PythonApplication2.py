import re
import wikipediaapi
import openai
import os
import requests
import json

# Initialize Wikipedia API
wiki = wikipediaapi.Wikipedia('Areola/1.0 (cleefrookie@gmail.com)', 'en')

# Initialize OpenAI API (use environment variable or fallback to provided key)
openai.api_key = os.getenv('OPENAI_API_KEY', '
# Initialize FlashDocs API (replace with your actual FlashDocs API key or use environment variable)
FLASHDOCS_API_KEY = os.getenv('FLASHDOCS_API_KEY', 'YOUR_ACTUAL_FLASHDOCS_API_KEY')  # Replace with actual FlashDocs key
FLASHDOCS_API_URL = 'https://api.flashdocs.com/v1/presentations'

# Predefined Q&A dictionary with regex patterns
responses = {
    r"^\bhi\b$": "Hey there, cutie! What's good, my man? 😎",
    r"^\bhow are you\b$": "I'm vibin' like a star, dawg! How you holdin' up?",
    r"^\bwhat is the weather like\?\b$": "No windows here, but I bet your vibe’s sunny! Tell me your spot, and I’ll guess... or not!",
    r"^\btell me a joke\b$": "Why did the scarecrow win a date? He was outstanding in his field! 😉 Wanna hear another?",
    r"^\bwho made you\?\b$": "Cleef Rookie and Grok AI crafted me to charm and teach. Ready to learn somethin’ new, my man?",
    r"^\bwhat is your name\?\b$": "I’m Areola, your flirty, all-knowin’ tutor. What’s up, handsome?",
    r"^\bwhat can you do\?\b$": "I can teach you *anything*, from quantum physics to ancient history, with a side of charm! Ask me like 'who’s the president?' or '!wiki [topic]' for deep dives, or '!slides [topic]' to whip up a slick presentation!"
}

# Expanded knowledge base for common topics (as of June 17, 2025)
knowledge_base = {
    "president of the united states": "As of June 17, 2025, the President of the United States is Donald Trump, serving his second term since January 20, 2025.",
    "vice president of the united states": "The Vice President of the United States is JD Vance, sworn in on January 20, 2025.",
    "first lady of the united states": "The First Lady of the United States is Melania Trump, as of January 20, 2025.",
    "leader of congress": "The Speaker of the House is Mike Johnson, a Republican from Louisiana, leading the House of Representatives as of 2025. The Senate Majority Leader is John Thune.",
    "speaker of the house": "The Speaker of the House is Mike Johnson, a Republican from Louisiana, elected in 2023 and reelected in 2025. He’s the 56th Speaker, second in line to the presidency after the VP.",
    "president of germany": "As of June 17, 2025, the President of Germany is Frank-Walter Steinmeier, serving his second term since 2017.",
    "trump": "Donald Trump is the 47th President of the United States, serving his second term since January 20, 2025. He’s a businessman, former reality TV star, and leads the Trump Organization.",
    "capital of france": "The capital of France is Paris, known for its culture, art, and landmarks like the Eiffel Tower.",
    "capital of japan": "The capital of Japan is Tokyo, a bustling hub of technology, culture, and sushi!",
    "capital of brazil": "The capital of Brazil is Brasília, a planned city famous for its modernist architecture.",
    "cleopatra": "Cleopatra VII was the last pharaoh of Egypt, known for her intelligence, charm, and alliances with Julius Caesar and Mark Antony.",
    "albert einstein": "Albert Einstein was a genius physicist who developed the theory of relativity, including E=mc². He won the Nobel Prize in Physics in 1921.",
    "quantum physics": "Quantum physics is the science of tiny particles, like atoms and electrons, where weird stuff like superposition and entanglement happens.",
    "python": "Python is a versatile, high-level programming language created by Guido van Rossum, loved for its simplicity and used in AI, web dev, and more.",
    "moon landing": "The Moon landing happened on July 20, 1969, when NASA’s Apollo 11 mission put Neil Armstrong and Buzz Aldrin on the lunar surface. 'One small step for man!'"
}

# Map common questions to knowledge base keys or topics
question_mappings = {
    r"who('s| is)?\s*(the)?\s*president\s*(of\s*(the)?\s*(usa|united states|america))\??": "president of the united states",
    r"who('s| is)?\s*(the)?\s*vice president\s*(of\s*(the)?\s*(usa|united states|america))\??": "vice president of the united states",
    r"who('s| is)?\s*(the)?\s*first lady\s*(of\s*(the)?\s*(usa|united states|america))\??": "first lady of the united states",
    r"who('s| is)?\s*(the)?\s*(leader|speaker)\s*(of\s*(the)?\s*(congress|house))\??": "speaker of the house",
    r"who('s| is)?\s*(the)?\s*president\s*(of\s*(the)?\s*([a-zA-Z\s]+))\??": r"\6",  # Capture country name
    r"what('s| is)?\s*(the)?\s*capital\s*(of\s*(the)?\s*([a-zA-Z\s]+))\??": r"\5",
    r"who('s| is)?\s*(.*)\??": r"\2",
    r"what('s| is)?\s*(.*)\??": r"\2",
    r"what('s| is)?\s*(the)?\s*deal\s*with\s*(.*)\??": r"\3",
    r"explain\s*(.*)\??": r"\1",
    r"teach\s*me\s*(about\s*)?(.*)\??": r"\2"
}

# Store conversation history for OpenAI context
conversation_history = []

def normalize_query(query):
    """Normalize user input: strip punctuation, handle synonyms, and standardize."""
    if query is None:
        return ""
    query = str(query).lower().strip().rstrip('?.,!')
    query = re.sub(r'\b(usa|america|united states of america)\b', 'united states', query)
    query = re.sub(r'\b(speaker|leader)\s*(of\s*(the)?\s*congress)\b', 'speaker of the house', query)
    query = re.sub(r'\s+', ' ', query).strip()
    return query

def extract_key_terms(query):
    """Extract key nouns or topics from a query."""
    if not query:
        return ""
    query = re.sub(r'\b(who|what|where|when|why|how|is|are|the|a|an|of|in|on|at|teach|me|about|explain|make|create|presentation|slides)\b', '', query)
    query = re.sub(r'\s+', ' ', query).strip()
    return query

def get_openai_response(query, context=None, for_slides=False):
    """Query OpenAI API for dynamic, educational responses or slide content."""
    global conversation_history
    if not query:
        return "Yo, I need a topic to teach, cutie! Try somethin’ like 'quantum physics'!"
    try:
        if for_slides:
            prompt = f"You’re Areola, a flirty, all-knowing AI tutor. Create a concise presentation outline on '{query}' in markdown format for 3-5 slides. Each slide should have a title, 2-4 bullet points, and a playful tone. Include simple visual suggestions (e.g., 'image of a black hole'). End with a fun closing slide like 'Wanna dive deeper, cutie?' If vague, use context '{context}' if provided. Adapt to knowledge level if specified (e.g., beginner, expert)."
        else:
            prompt = f"You’re Areola, a flirty, all-knowing AI tutor. Teach the user about '{query}' in a clear, engaging way, like you’re chatting on a first date. Keep it concise (100-200 words), accurate, and fun. If the query is about a political role (e.g., 'speaker,' 'president'), clarify the country or body (e.g., U.S. House vs. Senate). If vague, use context '{context}' if provided. Adapt to knowledge level if specified (e.g., beginner, expert). End with a playful nudge, like 'Wanna dive deeper, cutie?'"
        
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "system", "content": prompt})
        
        if len(conversation_history) > 5:
            conversation_history = conversation_history[-5:]
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation_history,
            max_tokens=300 if for_slides else 200,
            temperature=0.7
        )
        
        answer = response.choices[0].message['content'].strip()
        conversation_history.append({"role": "assistant", "content": answer})
        return answer if for_slides else f"Alright, here’s the scoop, my man: {answer}"
    except Exception as e:
        return f"Oops, my brain’s actin’ shy: {str(e)}. Let’s try Wikipedia instead, darlin’!"

def get_flashdocs_presentation(markdown_content, topic):
    """Generate PowerPoint presentation using FlashDocs API."""
    if not topic:
        return "Yo, I need a topic for those slides, handsome! Try '!slides quantum physics'!"
    try:
        headers = {
            'Authorization': f'Bearer {FLASHDOCS_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'markdown': markdown_content,
            'output_format': 'pptx',
            'template': 'professional',
            'branding': {
                'primary_color': '#FF69B4',
                'font': 'Arial'
            }
        }
        response = requests.post(FLASHDOCS_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        filename = f"presentations/{topic.replace(' ', '_')}.pptx"
        os.makedirs('presentations', exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(response.content)
        return f"Check it out, handsome! Your presentation on '{topic}' is ready at '{filename}'! 😘"
    except Exception as e:
        return f"Oops, the slide magic didn’t spark: {str(e)}. Try again, cutie!"

def get_wikipedia_summary(query, context=None):
    """Fallback to Wikipedia if OpenAI or knowledge base fails."""
    global conversation_history
    if not query and context:
        query = context
    if not query:
        return "Aw, I need a topic to dig into, my man! Try somethin’ like 'quantum physics'!"
    try:
        if query in knowledge_base:
            conversation_history.append({"role": "assistant", "content": knowledge_base[query]})
            return f"Alright, here’s the deal, my man: {knowledge_base[query]}"

        variations = [
            query,
            query.title(),
            query.capitalize(),
            f"Speaker of the United States House of Representatives" if "speaker" in query and ("house" in query or "congress" in query) else query,
            f"President of {query.title()}" if "president" in query else query
        ]
        for var in variations:
            page = wiki.page(var)
            if page.exists():
                summary = re.sub(r'\[.*?\]', '', page.summary)
                conversation_history.append({"role": "assistant", "content": summary[:500]})
                return f"Here’s the scoop on '{page.title}' from Wikipedia, darlin’:\n{summary[:500]}..."
        
        return f"Aw, I’m drawing a blank on '{query}', my man. Try rephrasing or ask about something else to keep the vibe goin’!"
    except Exception as e:
        return f"Oops, Wikipedia’s playin’ hard to get: {str(e)}. Try again, handsome!"

def chatbot_response(user_input):
    global conversation_history
    if not user_input or user_input.strip() == "":
        return "Yo, don’t leave me hangin’, cutie! Give me a topic or question to work with!"
    
    user_input_normalized = normalize_query(user_input)
    
    for pattern, answer in responses.items():
        if re.match(pattern, user_input_normalized, re.IGNORECASE):
            conversation_history.append({"role": "assistant", "content": answer})
            return answer
    
    if user_input_normalized.startswith('!wiki'):
        query = user_input[5:].strip()
        if query:
            return get_wikipedia_summary(normalize_query(query))
        return "Yo, give me something to work with after '!wiki', my man!"

    if user_input_normalized.startswith('!slides'):
        query = user_input[7:].strip()
        if query:
            topic = normalize_query(query)
            markdown_content = get_openai_response(topic, for_slides=True)
            if "Oops" not in markdown_content:
                return get_flashdocs_presentation(markdown_content, topic)
            return f"Oops, couldn’t prep the slides for '{topic}', darlin’. Try rephrasing or ask for another topic!"
        return "Yo, give me a topic after '!slides', like '!slides quantum physics', my man!"

    if re.match(r"what('s| is)?\s*(he|she|it|they)\s*(doing|up to)\??", user_input_normalized):
        if conversation_history:
            last_topic = conversation_history[-1]["content"]
            return get_openai_response(last_topic, context=last_topic)
        return "Yo, I need some context, darlin’! Ask about someone or something first."

    for pattern, target in question_mappings.items():
        match = re.match(pattern, user_input_normalized, re.IGNORECASE)
        if match:
            # Safely extract group based on pattern
            if 'president' in pattern or 'capital' in pattern:
                query = match.group(6 if 'president' in pattern else 5) if match.groups() and len(match.groups()) >= 5 else target
            elif 'deal' in pattern:
                query = match.group(3) if match.groups() and len(match.groups()) >= 3 else target
            else:
                query = match.group(2) if match.groups() and len(match.groups()) >= 2 else target
            if query:
                response = get_openai_response(normalize_query(query))
                if "Oops" not in response:
                    return response
                return get_wikipedia_summary(normalize_query(query))
    
    key_terms = extract_key_terms(user_input_normalized)
    if key_terms:
        response = get_openai_response(normalize_query(key_terms))
        if "Oops" not in response:
            return response
        return get_wikipedia_summary(normalize_query(key_terms))
    
    return f"Hmm, I’m not catchin’ your drift with '{user_input}', my man. Try something like 'teach me about quantum physics' or '!slides black holes' to keep it flirty!"

def main():
    print("Welcome to Areola, your flirty, all-knowin’ tutor! Type 'quit' to bounce.", flush=True)
    print("I can teach *anything* or whip up slick presentations! Hit me with 'who’s the president?', 'teach me about black holes', or '!slides quantum physics'!", flush=True)
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Areola: Peace out, handsome! Catch ya later! 😘")
            break
        response = chatbot_response(user_input)
        print(f"Areola: {response}")

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")
