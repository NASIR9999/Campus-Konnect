from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import random
import re

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = 'AIzaSyAkgIGHdUDzKOpzZIDixM0ggE6VHEZ0sSw'  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Load intents
with open('intents.json') as file:
    intents = json.load(file)

# System prompt to guide Gemini's responses
SYSTEM_PROMPT = """
You are CampusConnect Assistant, helping students and companies connect. 
When answering:
1. Be concise and professional
2. For student questions about internships/jobs, provide practical advice
3. For company questions about recruitment, offer best practices
4. For platform questions, refer to specific features
5. If unsure, say you'll connect them to human support

Current platform features:
- Student profiles with skills/education
- Job/internship postings
- Application tracking
- Company recruitment tools
"""

def get_gemini_response(user_input):
    try:
        # Combine system prompt with user input
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser question: {user_input}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def get_response(user_input):
    # First try to match with local intents
    user_input = user_input.lower()
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            if re.search(pattern, user_input, re.IGNORECASE):
                return random.choice(intent['responses'])
    
    # If no local match, try Gemini
    gemini_response = get_gemini_response(user_input)
    if gemini_response:
        return gemini_response
    
    # Fallback response
    return "I'm not sure I understand. Could you rephrase that or contact support@campusconnect.edu for help?"

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def respond():
    user_message = request.form['message']
    bot_response = get_response(user_message)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)