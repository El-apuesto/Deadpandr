from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from joke_generator import generate_jokes, get_styles_config
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/robots.txt')
def robots():
    """Serve robots.txt for SEO"""
    return send_from_directory('.', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml for SEO"""
    return send_from_directory('.', 'sitemap.xml')

@app.route('/api/styles', methods=['GET'])
def get_styles():
    """Return available styles with UI positioning"""
    return jsonify(get_styles_config())

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate jokes with style blending"""
    data = request.json
    
    # Accept style_weights instead of single tone
    style_weights = data.get('style_weights', {'Default': 1.0})
    topic = data.get('topic', 'life')
    output_type = data.get('output_type', 'Jokes')
    transition_type = data.get('transition_type', 'smooth')
    madness = float(data.get('madness', 0.7))
    darkness = int(data.get('darkness', 5))
    num_jokes = int(data.get('num_jokes', 5))
    
    try:
        jokes = generate_jokes(topic, style_weights, output_type, 
                              transition_type, madness, darkness, num_jokes)
        
        return jsonify({
            'jokes': jokes,
            'style_blend': style_weights,
            'topic': topic
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'jokes': []
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)