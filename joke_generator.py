import os
import json
import random
from typing import Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

_generator = None

def _get_generator(token):
    """Lazily import and initialize text generation pipeline"""
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
    except Exception as e:
        return None, f"Error initializing model: {e}"

def _load_jokes_data():
    """Load jokes.json with all style data"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        jokes_path = os.path.join(script_dir, 'jokes.json')
        with open(jokes_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading jokes.json: {e}")
        return {}

def _blend_style_pools(style_weights: Dict[str, float]) -> Tuple[List[str], str]:
    """Blend multiple joke styles based on weights"""
    jokes_data = _load_jokes_data()
    all_examples = []
    descriptions = []
    
    for style, weight in style_weights.items():
        if weight <= 0:
            continue
            
        style_data = jokes_data.get(style, {})
        examples = style_data.get('jokes', [])
        description = style_data.get('name', style)
        
        if examples:
            # Sample proportionally based on weight
            num_samples = max(1, int(6 * weight))
            sampled = random.sample(examples, min(num_samples, len(examples)))
            all_examples.extend(sampled)
            
            if weight > 0.2:  # Only include significant influences
                descriptions.append(f"{description} ({int(weight*100)}%)")
    
    blended_desc = " blended with ".join(descriptions) if descriptions else "Default style"
    return all_examples, blended_desc

def _build_prompt(topic: str, style_weights: Dict[str, float], output_type: str, 
                  transition_type: str, madness: float, darkness: int, 
                  examples: List[str]) -> str:
    """Build prompt for joke generation with style blending"""
    
    examples_pool, style_description = _blend_style_pools(style_weights)
    
    prompt = f"Generate {output_type.lower()} about '{topic}' using {style_description}. "
    
    # Add output type instructions
    if output_type == 'Routines':
        prompt += f"Create a comedy routine with {transition_type.lower()} transitions. "
    elif output_type == 'One-liners':
        prompt += "Create short, punchy one-liners. "
    elif output_type == 'Punchlines':
        prompt += "Focus on strong, memorable punchlines. "
    
    # Add parameter guidance
    creativity_level = "very creative and unpredictable" if madness > 0.8 else \
                      "creative and surprising" if madness > 0.6 else \
                      "moderately creative" if madness > 0.4 else \
                      "straightforward"
    
    darkness_level = "extremely dark" if darkness > 8 else \
                    "very dark" if darkness > 6 else \
                    "moderately dark" if darkness > 4 else \
                    "mildly dark" if darkness > 2 else \
                    "lightly humorous"
    
    prompt += f"Make it {creativity_level} and {darkness_level}. "
    
    # Add examples
    if examples_pool:
        sample_examples = random.sample(examples_pool, min(6, len(examples_pool)))
        prompt += "\n\nStyle examples:\n"
        for i, example in enumerate(sample_examples, 1):
            prompt += f"{i}. {example}\n"
    
    prompt += f"\nNow create a new joke about '{topic}':\n"
    return prompt

def generate_jokes(topic: str, style_weights: Dict[str, float], output_type: str, 
                   transition_type: str, madness: float, darkness: int, 
                   num_jokes: int) -> List[str]:
    """Generate jokes using blended styles"""
    
    # Get blended examples
    examples, _ = _blend_style_pools(style_weights)
    
    # Try HF model
    token = os.getenv('HF_TOKEN')
    generator, error = _get_generator(token)
    
    jokes = []
    
    if generator and not error:
        try:
            prompt = _build_prompt(topic, style_weights, output_type, 
                                  transition_type, madness, darkness, examples)
            
            outputs = generator(
                prompt,
                max_new_tokens=150,
                temperature=madness,
                num_return_sequences=min(num_jokes, 3),
                do_sample=True,
                pad_token_id=generator.tokenizer.eos_token_id
            )
            
            for output in outputs:
                generated_text = output['generated_text']
                joke_start = generated_text.find("Now create a new joke")
                if joke_start != -1:
                    joke_part = generated_text[joke_start:].split('\n', 1)
                    if len(joke_part) > 1:
                        joke = joke_part[1].strip()
                        if joke and len(joke) > 10:
                            jokes.append(joke)
        except Exception as e:
            print(f"Model generation failed: {e}")
    
    # Fallback to template-based generation
    while len(jokes) < num_jokes:
        if examples:
            base_joke = random.choice(examples)
            modified_joke = base_joke.replace("life", topic).replace("work", topic)
            
            if darkness > 7:
                dark_prefixes = ["In the darkest timeline, ", "When hope dies, "]
                modified_joke = random.choice(dark_prefixes) + modified_joke.lower()
            
            if madness > 0.8:
                weird_suffixes = [" ...or does it?", " in an alternate reality"]
                modified_joke += random.choice(weird_suffixes)
            
            jokes.append(modified_joke)
        else:
            jokes.append(f"I told my therapist about {topic}. Now we both need therapy.")
    
    return jokes[:num_jokes]

def get_styles_config():
    """Return styles configuration for UI"""
    return _load_jokes_data()