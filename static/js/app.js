let blender;
let currentWeights = { 'Default': 1.0 };

document.addEventListener('DOMContentLoaded', () => {
    blender = new StyleBlender('style-canvas');
    
    blender.onWeightsChange = (weights) => {
        currentWeights = weights;
    };
    
    document.getElementById('generate-btn').addEventListener('click', generateJokes);
    
    document.getElementById('topic-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            generateJokes();
        }
    });
});

async function generateJokes() {
    const topic = document.getElementById('topic-input').value || 'life';
    const numJokes = parseInt(document.getElementById('num-jokes').value);
    const outputDiv = document.getElementById('joke-output');
    
    outputDiv.innerHTML = '<p>Generating jokes...</p>';
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                style_weights: currentWeights,
                output_type: 'Jokes',
                transition_type: 'smooth',
                madness: 0.7,
                darkness: 5,
                num_jokes: numJokes
            })
        });
        
        const data = await response.json();
        
        if (data.jokes && data.jokes.length > 0) {
            outputDiv.innerHTML = '<h3>Generated Jokes:</h3>' +
                data.jokes.map((joke, i) => `<p><strong>${i+1}.</strong> ${joke}</p>`).join('');
        } else {
            outputDiv.innerHTML = '<p>No jokes generated. Try a different topic or style blend.</p>';
        }
    } catch (error) {
        console.error('Error generating jokes:', error);
        outputDiv.innerHTML = '<p>Error generating jokes. Please try again.</p>';
    }
}