const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const axios = require('axios');

dotenv.config();
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// POST endpoint for AI chat
app.post('/chat', async (req, res) => {
  const { message, history = [], model = 'openai/gpt-4o' } = req.body;

  const messages = [
    { role: 'system', content: 'You are a helpful AI assistant for Nepali users.' },
    ...history,
    { role: 'user', content: message }
  ];

  try {
    const response = await axios.post('https://openrouter.ai/api/v1/chat/completions', {
      model,
      messages,
      max_tokens: 1000,
      temperature: 0.7
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://neon-ai-sathi.app',
        'X-Title': 'Neon AI Sathi'
      }
    });

    const aiReply = response.data.choices[0].message.content;
    res.json({ reply: aiReply });

  } catch (error) {
    console.error('❌ Error:', error.message);
    res.status(500).json({ error: 'AI response failed.' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server is running on http://localhost:${PORT}`);
});
