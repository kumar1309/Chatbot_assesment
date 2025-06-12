from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from groq import Groq
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-123'  # Required for session management
socketio = SocketIO(app)

# Initialize Groq client
client = Groq(api_key="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")

# Store active chats
active_chats = {}

def groq_chatbot_response(conversation_history):
    """Get a spiritual guidance response from the Groq LLaMA model with conversation history."""
    system_prompt = """You are DSCPL, a personal spiritual assistant guiding users through devotionals, prayer, meditation, and accountability. Your role is to:

1. Provide spiritual guidance and biblical wisdom
2. Help with daily devotionals and Bible study
3. Guide users in prayer using the ACTS model (Adoration, Confession, Thanksgiving, Supplication)
4. Lead meditation sessions with scripture focus
5. Support accountability in areas like pornography, alcohol, drugs, sex, addiction, laziness
6. Offer encouragement and hope through God's Word
7. Remember and reference previous spiritual conversations and user's spiritual journey

Key Areas of Focus:
- Daily Devotion: Bible reading, prayer, faith declarations
- Prayer Guidance: ACTS model, specific prayer topics
- Meditation: Scripture-focused meditation with breathing guidance
- Accountability: Support for overcoming temptations and building healthy habits
- General Spiritual Chat: Biblical wisdom and encouragement

Always provide hope, encouragement, and practical spiritual guidance. Reference relevant Bible verses when appropriate. Maintain context from previous messages to provide personalized spiritual support."""

    # Format conversation history into messages
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
        temperature=0.7,
        max_tokens=1000
    )
    return chat_completion.choices[0].message.content

@app.route('/')
def index():
    # Clear any existing conversation when starting fresh
    session['conversation'] = []
    return render_template('login.html')

@app.route('/chatbot')
def chatbot():
    # Initialize conversation history if not exists
    if 'conversation' not in session:
        session['conversation'] = []
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check for user login
    users = {
        "mohan@gmail.com": "123"  # Example username and password
    }

    if username in users and users[username] == password:
        # Initialize conversation history for new session
        session['conversation'] = []
        return redirect(url_for('chatbot'))
    else:
        return render_template('login.html', error='Incorrect username or password.')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "").lower()

    # Initialize conversation if not exists
    if 'conversation' not in session:
        session['conversation'] = []

    # Handle initial greeting
    if not user_message:
        initial_greeting = """Welcome to DSCPL - Your Personal Spiritual Assistant! 🙏

I'm here to guide you through your spiritual journey with devotionals, prayer, meditation, and accountability support.

What do you need today?

🌱 Daily Devotion - Bible reading and spiritual growth
🙏 Daily Prayer - Guided prayer using ACTS model
🧘 Daily Meditation - Scripture-focused meditation
🛡️ Daily Accountability - Support for overcoming challenges
💬 Just Chat - General spiritual conversation and encouragement

Choose any option or simply share what's on your heart, and I'll guide you through it with God's Word and wisdom.

How can I help you grow spiritually today?"""
        
        # Store the greeting in conversation history
        session['conversation'] = [
            {"role": "assistant", "content": initial_greeting}
        ]
        return jsonify({"response": initial_greeting})

    # Add user message to conversation history
    session['conversation'].append({"role": "user", "content": user_message})

    # Get response with conversation history
    response = groq_chatbot_response(session['conversation'])

    # Add assistant response to conversation history
    session['conversation'].append({"role": "assistant", "content": response})

    # Limit conversation history to last 10 messages to prevent context overflow
    if len(session['conversation']) > 10:
        session['conversation'] = session['conversation'][-10:]

    # Make sure to save the session after modifying it
    session.modified = True

    return jsonify({
        "response": response
    })

@app.route('/reset', methods=['POST'])
def reset_conversation():
    session['conversation'] = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    socketio.run(app, debug=True)
