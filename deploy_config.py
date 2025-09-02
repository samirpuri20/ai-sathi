#!/usr/bin/env python3
# Production deployment configuration for AI Sathi

import os
from ai_sathi import app

# Production settings
app.config['DEBUG'] = False
app.config['ENV'] = 'production'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)