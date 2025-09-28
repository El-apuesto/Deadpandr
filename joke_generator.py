import os
import json
import time
import random
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variable to hold the generator
_generator = None

def _get_generator(token):
    """Lazily import and initialize the text generation pipeline"""
    global _generator
    
    if _generator is not None:
        return _generator, None
    
    try:
        from transformers import pipeline
        
        model_name = os.getenv('HF_MODEL', 'microsoft/DialoGPT-medium')
        
        _generator = pipeline(
            'text-generation',
            model=model_name,
            use_auth_token=token if token else None,
            device_map='auto',
            trust_remote_code=True
        )
        
        return _generator, None
    
    except ImportError as e:
        return None, f"Error: transformers library not installed: {e}"
    except Exception as e:
        return None, f"Error initializing model: {e}"

def _get_pool_for_style(tone):
    """Get example jokes from jokes.json for the specified tone"""
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        jokes_path = os.path.join(script_dir, 'jokes.json')
        
        with open(jokes_path, 'r', encoding='utf-8') as f:
            jokes_data = json.load(f)
        
        # Get jokes for the tone, fallback to 'Default'
        tone_data = jokes_data.get(tone, jokes_data.get('Default', {}))
        return tone_data.get('jokes', []), tone_data.get('description', '')
    
    except Exception as e:
        print(f"Error loading jokes.json: {e}")
        return [], "Generate dark humor with wit and edge"

def _build_prompt(topic, tone, output_type, transition_type, madness, darkness, examples):
    """Build the prompt for joke generation"""
    
    # Get tone description
    _, tone_description = _get_pool_for_style(tone)
    
    # Build base prompt
    prompt = f"Generate {output_type.lower()} about '{topic}' in a {tone} style. "
    prompt += f"{tone_description} "
    
    # Add output type specific instructions
    if output_type == 'Routines':
        prompt += f"Create a comedy routine with {transition_type.lower()} transitions between jokes. "
    elif output_type == 'One-liners':
        prompt += "Create short, punchy one-liner jokes. "
    elif output_type == 'Punchlines':
        prompt += "Focus on strong, memorable punchlines. "
    else:
        prompt += "Create varied joke formats. "
    
    # Add parameter guidance
    creativity_level = "very creative and unpredictable" if madness > 0.8 else \
                     "creative and surprising" if madness > 0.6 else \
                     "moderately creative" if madness > 0.4 else \
                     "straightforward and conventional"
    
    darkness_level = "extremely dark" if darkness > 8 else \
                    "very dark" if darkness > 6 else \
                    "moderately dark" if darkness > 4 else \
                    "mildly dark" if darkness > 2 else \
                    "lightly humorous"
    
    prompt += f"Make the humor {creativity_level} and {darkness_level}. "
    
    # Add examples if available
    if examples:
        sample_examples = random.sample(examples, min(6, len(examples)))
        prompt += "Here are some examples of the style:\n"
        for i, example in enumerate(sample_examples, 1):
            prompt += f"{i}. {example}\n"
    
    prompt += f"\nNow create a new joke about '{topic}':\n"
    
    return prompt

def generate_jokes(topic, tone, output_type, transition_type, madness, darkness, num_jokes):
    """Generate jokes using the Hugging Face model with fallback to template-based jokes"""
    
    # Get example jokes for the tone
    examples, _ = _get_pool_for_style(tone)
    
    # Try to use the HF model first
    token = os.getenv('HF_TOKEN')
    generator, error = _get_generator(token)
    
    jokes = []
    
    if generator and not error:
        try:
            # Build prompt
            prompt = _build_prompt(topic, tone, output_type, transition_type, madness, darkness, examples)
            
            # Generate jokes
            outputs = generator(
                prompt,
                max_new_tokens=150,
                temperature=madness,
                num_return_sequences=min(num_jokes, 3),  # Limit to avoid memory issues
                do_sample=True,
                pad_token_id=generator.tokenizer.eos_token_id
            )
            
            for output in outputs:
                generated_text = output['generated_text']
                # Extract the joke part (after the prompt)
                joke_start = generated_text.find("Now create a new joke")
                if joke_start != -1:
                    joke_part = generated_text[joke_start:].split('\n', 1)
                    if len(joke_part) > 1:
                        joke = joke_part[1].strip()
                        if joke and len(joke) > 10:  # Basic quality filter
                            jokes.append(joke)
            
        except Exception as e:
            print(f"Model generation failed: {e}")
    
    # Fallback to template-based jokes if model failed or didn't generate enough
    while len(jokes) < num_jokes:
        if examples:
            # Use template-based approach with examples
            base_joke = random.choice(examples)
            
            # Simple template replacement
            modified_joke = base_joke.replace("life", topic).replace("work", topic).replace("people", topic)
            
            # Add some variation based on parameters
            if darkness > 7:
                dark_prefixes = ["In the darkest timeline, ", "When all hope dies, ", "At rock bottom, "]
                modified_joke = random.choice(dark_prefixes) + modified_joke.lower()
            
            if madness > 0.8:
                weird_suffixes = [" ...or does it?", " in a parallel universe where logic died", " according to my therapist"]
                modified_joke += random.choice(weird_suffixes)
            
            jokes.append(modified_joke)
        else:
            # Last resort: generic joke templates
            templates = [
                f"Why did the {topic} cross the road? To get to the {tone.lower()} side.",
                f"I told my therapist about {topic}. Now we both need therapy.",
                f"{topic} is like {tone.lower()} humor - not everyone gets it, but those who do are probably damaged.",
                f"They say {topic} builds character. I'd rather be shallow and happy.",
            ]
            jokes.append(random.choice(templates))
    
    return jokes[:num_jokes]