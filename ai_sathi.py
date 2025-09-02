#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, request
import subprocess
import os
import google.generativeai as genai
import time
import json

app = Flask(__name__)

# Configure Gemini AI
API_KEY = "AIzaSyBOukE7ak1vmIFR7zaiOvmCBVXDc0xf7ZE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Sathi - Your Digital Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .container {
            text-align: center;
            max-width: 800px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo {
            width: 120px;
            height: 120px;
            margin: 0 auto 30px;
            border-radius: 50%;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 50px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        h1 { font-size: 3em; margin-bottom: 10px; }
        .subtitle { font-size: 1.2em; margin-bottom: 30px; opacity: 0.8; }
        
        .controls {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 15px 30px;
            font-size: 1.1em;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .language-toggle {
            background: linear-gradient(45deg, #4ecdc4, #44a08d);
        }
        
        .response {
            margin-top: 20px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            text-align: left;
            min-height: 100px;
            border-left: 4px solid #ff6b6b;
        }
        
        .device-controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .device-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖</div>
        <h1>AI Sathi</h1>
        <p class="subtitle">Your Multilingual Digital Assistant</p>
        
        <div class="controls">
            <button onclick="startListening()">🎤 Listen</button>
            <button onclick="stopListening()">⏹️ Stop</button>
            <button class="language-toggle" onclick="toggleLanguage()">🌐 <span id="langText">English</span></button>
        </div>
        
        <div class="device-controls">
            <div class="device-card">
                <h3>🖥️ Mac Control</h3>
                <button onclick="sendCommand('mac volume up')">Volume Up</button>
                <button onclick="sendCommand('mac screenshot')">Screenshot</button>
            </div>
            <div class="device-card">
                <h3>📱 Mobile Control</h3>
                <button onclick="sendCommand('phone find')">Find Phone</button>
                <button onclick="sendCommand('phone battery')">Battery Status</button>
            </div>
        </div>
        
        <div class="response" id="response">
            <strong>AI Sathi:</strong> Namaste! I can help you in English and Nepali. Click Listen to start.
        </div>
    </div>

    <script>
        let recognition;
        let currentLang = 'en-US';
        let isListening = false;
        
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
        }
        
        function speak(text, lang = 'en') {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.8;
            utterance.pitch = 1.1;
            
            if (lang === 'ne') {
                // Try different voices for better Nepali pronunciation
                const voices = speechSynthesis.getVoices();
                const nepaliVoice = voices.find(voice => 
                    voice.lang.includes('ne') || 
                    voice.lang.includes('hi') || 
                    voice.name.includes('Hindi') ||
                    voice.name.includes('Indian')
                );
                
                if (nepaliVoice) {
                    utterance.voice = nepaliVoice;
                    utterance.lang = nepaliVoice.lang;
                } else {
                    // Fallback to Hindi for better Devanagari pronunciation
                    utterance.lang = 'hi-IN';
                }
            } else {
                utterance.lang = 'en-US';
                const voices = speechSynthesis.getVoices();
                const femaleVoice = voices.find(voice => 
                    voice.name.includes('Samantha') || 
                    voice.name.includes('Female')
                );
                if (femaleVoice) utterance.voice = femaleVoice;
            }
            
            // For Nepali, try phonetic pronunciation if native doesn't work well
            if (lang === 'ne' && !utterance.voice) {
                const phoneticText = improveNepaliPronunciation(text);
                utterance.text = phoneticText;
                utterance.lang = 'en-US';
            }
            
            speechSynthesis.speak(utterance);
        }
        
        function toggleLanguage() {
            if (currentLang === 'en-US') {
                currentLang = 'ne-NP';
                document.getElementById('langText').textContent = 'नेपाली';
            } else {
                currentLang = 'en-US';
                document.getElementById('langText').textContent = 'English';
            }
        }
        
        function startListening() {
            if (!recognition) return;
            
            recognition.lang = currentLang;
            document.getElementById('response').innerHTML = '<strong>Status:</strong> Listening...';
            
            recognition.start();
            
            recognition.onresult = function(event) {
                let command = event.results[0][0].transcript;
                
                // Clean up unwanted words and translations
                command = command.replace(/translation:/gi, '');
                command = command.replace(/\([^)]*\)/g, ''); // Remove text in parentheses
                command = command.replace(/ma sanchai chu.*$/gi, ''); // Remove this specific phrase
                command = command.replace(/hajurlai kasto chha.*$/gi, ''); // Remove this phrase
                command = command.replace(/i am well.*$/gi, ''); // Remove English translations
                command = command.replace(/how are you.*$/gi, ''); // Remove English translations
                command = command.trim();
                
                if (command.length < 3) {
                    document.getElementById('response').innerHTML = '<strong>Status:</strong> Command too short, try again';
                    return;
                }
                
                document.getElementById('response').innerHTML = '<strong>You:</strong> ' + command;
                sendCommand(command);
            };
            
            recognition.onerror = function() {
                document.getElementById('response').innerHTML = '<strong>Error:</strong> Could not hear you.';
            };
        }
        
        function stopListening() {
            if (recognition) recognition.stop();
            speechSynthesis.cancel();
        }
        
        function sendCommand(command) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    command: command,
                    language: currentLang.includes('ne') ? 'ne' : 'en'
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').innerHTML = '<strong>AI Sathi:</strong> ' + data.response;
                speak(data.response, data.language || 'en');
            });
        }
        // Load voices when available
        speechSynthesis.onvoiceschanged = function() {
            console.log('Available voices:', speechSynthesis.getVoices().map(v => v.name + ' - ' + v.lang));
        };
        
        // Add phonetic pronunciation helper for Nepali
        function improveNepaliPronunciation(text) {
            const replacements = {
                'नमस्ते': 'namaste',
                'धन्यवाद': 'dhanyabad', 
                'समय': 'samaya',
                'मिति': 'miti',
                'आज': 'aaja',
                'अहिले': 'ahile',
                'हो': 'ho',
                'छ': 'cha'
            };
            
            let improvedText = text;
            for (const [nepali, phonetic] of Object.entries(replacements)) {
                improvedText = improvedText.replace(new RegExp(nepali, 'g'), phonetic);
            }
            return improvedText;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/command', methods=['POST'])
def process_command():
    data = request.json
    command = data.get('command', '').lower().strip()
    language = data.get('language', 'en')
    
    # Additional server-side cleaning
    command = command.replace('translation:', '')
    command = command.replace('ma sanchai chu', '')
    command = command.replace('hajurlai kasto chha', '')
    command = command.strip()
    
    try:
        # Mac Controls
        if 'mac' in command or 'volume' in command or 'screenshot' in command:
            if 'volume up' in command:
                subprocess.run(['osascript', '-e', 'set volume output volume (output volume of (get volume settings) + 10)'])
                response = "Volume increased" if language == 'en' else "आवाज बढाइयो"
            elif 'volume down' in command:
                subprocess.run(['osascript', '-e', 'set volume output volume (output volume of (get volume settings) - 10)'])
                response = "Volume decreased" if language == 'en' else "आवाज घटाइयो"
            elif 'screenshot' in command:
                subprocess.run(['screencapture', '-x', f'{os.path.expanduser("~/Desktop")}/screenshot_{int(time.time())}.png'])
                response = "Screenshot taken" if language == 'en' else "स्क्रिनसट लिइयो"
            elif 'open' in command:
                if 'spotify' in command:
                    subprocess.run(['open', '-a', 'Spotify'])
                    response = "Opening Spotify" if language == 'en' else "Spotify खोल्दै"
                elif 'safari' in command:
                    subprocess.run(['open', '-a', 'Safari'])
                    response = "Opening Safari" if language == 'en' else "Safari खोल्दै"
        
        # Mobile Controls (simulated)
        elif 'phone' in command or 'mobile' in command:
            if 'find' in command:
                response = "Phone location sent to your email" if language == 'en' else "फोनको स्थान इमेलमा पठाइयो"
            elif 'battery' in command:
                response = "Phone battery: 85%" if language == 'en' else "फोनको ब्याट्री: ८५%"
        
        # Time and Date
        elif 'time' in command or 'समय' in command:
            current_time = time.strftime("%I:%M %p")
            if language == 'en':
                response = f"Current time is {current_time}"
            else:
                # Convert to Nepali numerals and format
                nepali_time = current_time.replace('AM', 'बिहान').replace('PM', 'बेलुका')
                response = f"अहिलेको समय {nepali_time} हो"
        
        elif 'date' in command or 'मिति' in command:
            current_date = time.strftime("%B %d, %Y")
            if language == 'en':
                response = f"Today is {current_date}"
            else:
                response = f"आजको मिति {current_date} हो"
        
        # Developer info
        elif any(word in command for word in ['develop', 'developer', 'create', 'made', 'who', 'विकास', 'बनाउने', 'को']):
            if language == 'ne':
                response = "म एक बृहत् भाषा मोडेल हुँ जुन नेपालका समीर पुरीले विकास गरेका हुन्।"
            else:
                response = "I am a large language model developed by Samir Puri from Nepal."
        
        # AI Conversations
        else:
            if language == 'ne':
                prompt = f"You are AI Sathi, a helpful Nepali assistant. Respond in simple, clear Nepali (Devanagari script) to: '{command}'. Use common Nepali words that are easy to pronounce. Keep it brief and natural."
            else:
                prompt = f"You are AI Sathi, a helpful assistant. Respond in English to: '{command}'. Keep it brief and natural."
            
            ai_response = model.generate_content(prompt)
            response = ai_response.text.strip()
            
            # Improve Nepali pronunciation by adding phonetic hints
            if language == 'ne' and any(char in response for char in 'अआइईउऊएऐओऔकखगघचछजझटठडढतथदधनपफबभमयरलवशषसह'):
                # Add SSML-like pauses for better pronunciation
                response = response.replace('।', '। ')
                response = response.replace('?', '? ')
                response = response.replace('!', '! ')
        
        return jsonify({
            'response': response,
            'language': language
        })
    
    except Exception as e:
        error_msg = f"Error: {str(e)}" if language == 'en' else f"त्रुटि: {str(e)}"
        return jsonify({'response': error_msg, 'language': language})

if __name__ == '__main__':
    print("🚀 Starting AI Sathi...")
    print("🌐 Open http://localhost:5002 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5002)