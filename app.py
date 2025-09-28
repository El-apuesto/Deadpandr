import os
import gradio as gr
from joke_generator import generate_jokes
from utils import save_output
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_creativity_label(value):
    """Convert creativity value to custom label"""
    labels = [
        "homeowners association", "golf", "Steven Seagal Movies", 
        "meh", "the News", "acid trip", "schizophrenic"
    ]
    # Map 0.1-1.0 range to 0-6 index
    index = min(6, max(0, int((value - 0.1) / 0.15)))
    return labels[index]

def get_creativity_value(label):
    """Convert custom label to creativity value"""
    labels = {
        "homeowners association": 0.1, "golf": 0.25, "Steven Seagal Movies": 0.4,
        "meh": 0.55, "the News": 0.7, "acid trip": 0.85, "schizophrenic": 1.0
    }
    return labels.get(label, 0.7)

def generate_jokes_wrapper(topic, tone, output_type, transition_type, madness_label, darkness, num_jokes):
    """Wrapper function for generating jokes with validation"""
    try:
        # Validate topic
        if not topic or not topic.strip():
            return "Error: Please enter a topic for joke generation."
        
        # Convert creativity label to value
        madness = get_creativity_value(madness_label)
        
        # Handle transition type
        if output_type != 'Routines':
            transition_type = 'None'
        
        # Generate jokes
        jokes = generate_jokes(
            topic=topic.strip(),
            tone=tone,
            output_type=output_type,
            transition_type=transition_type,
            madness=madness,
            darkness=darkness,
            num_jokes=num_jokes
        )
        
        # Format output
        if isinstance(jokes, list):
            return "\n\n".join(f"Joke {i+1}:\n{joke}" for i, joke in enumerate(jokes))
        else:
            return str(jokes)
    
    except Exception as e:
        return f"Error generating jokes: {str(e)}"

def save_txt_wrapper(output_text):
    """Save output as TXT file"""
    try:
        if not output_text or output_text.strip() == "":
            return "Error: No content to save."
        
        jokes_list = output_text.split('\n\n')
        result = save_output(jokes_list, 'txt')
        
        if result.startswith('Error'):
            return result
        else:
            return f"Successfully saved to: {result}"
    
    except Exception as e:
        return f"Error saving TXT: {str(e)}"

def save_pdf_wrapper(output_text):
    """Save output as PDF file"""
    try:
        if not output_text or output_text.strip() == "":
            return "Error: No content to save."
        
        jokes_list = output_text.split('\n\n')
        result = save_output(jokes_list, 'pdf')
        
        if result.startswith('Error'):
            return result
        else:
            return f"Successfully saved to: {result}"
    
    except Exception as e:
        return f"Error saving PDF: {str(e)}"

def update_transition_visibility(output_type):
    """Show/hide transition type dropdown based on output type"""
    if output_type == 'Routines':
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)

# Create Gradio interface
with gr.Blocks(title="Dark Comedy Joke Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎭 Dark Comedy Joke Generator")
    gr.Markdown("Generate darkly humorous content with customizable parameters.")
    
    with gr.Row():
        with gr.Column(scale=2):
            # Input components
            topic_input = gr.Textbox(
                label="Topic",
                placeholder="Enter a topic for jokes (e.g., 'office life', 'relationships', 'technology')",
                lines=2
            )
            
            tone_dropdown = gr.Dropdown(
                choices=['Dark Deadpan', 'Sarcastic', 'Nihilist', 'Cynical', 'Absurdist', 'Dark', 'Default'],
                value='Default',
                label="Tone"
            )
            
            output_type_dropdown = gr.Dropdown(
                choices=['Routines', 'One-liners', 'Punchlines', 'Random Jokes'],
                value='One-liners',
                label="Output Type"
            )
            
            transition_type_dropdown = gr.Dropdown(
                choices=['False Segue', 'Thematic', 'Absurd Thematic', 'Self-aware', 'Random', 'None'],
                value='Random',
                label="Transition Type (for Routines)",
                visible=False
            )
            
            with gr.Row():
                madness_slider = gr.Dropdown(
                    choices=["homeowners association", "golf", "Steven Seagal Movies", "meh", "the News", "acid trip", "schizophrenic"],
                    value="the News",
                    label="Creativity Level"
                )
                
                darkness_slider = gr.Slider(
                    minimum=0,
                    maximum=10,
                    step=1,
                    value=5,
                    label="Darkness Level"
                )
            
            num_jokes_slider = gr.Slider(
                minimum=1,
                maximum=10,
                step=1,
                value=5,
                label="Number of Jokes"
            )
            
            generate_btn = gr.Button("🎪 Generate Jokes", variant="primary")
        
        with gr.Column(scale=3):
            # Output components
            output_textbox = gr.Textbox(
                label="Generated Jokes",
                lines=8,
                max_lines=15,
                show_copy_button=True,
                placeholder="Generated jokes will appear here..."
            )
            
            with gr.Row():
                save_txt_btn = gr.Button("💾 Save as TXT", variant="secondary")
                save_pdf_btn = gr.Button("📄 Save as PDF", variant="secondary")
            
            status_textbox = gr.Textbox(
                label="Status",
                lines=2,
                interactive=False,
                placeholder="Save status will appear here..."
            )
    
    # Event handlers
    output_type_dropdown.change(
        fn=update_transition_visibility,
        inputs=[output_type_dropdown],
        outputs=[transition_type_dropdown]
    )
    
    generate_btn.click(
        fn=generate_jokes_wrapper,
        inputs=[topic_input, tone_dropdown, output_type_dropdown, transition_type_dropdown, 
                madness_slider, darkness_slider, num_jokes_slider],
        outputs=[output_textbox]
    )
    
    save_txt_btn.click(
        fn=save_txt_wrapper,
        inputs=[output_textbox],
        outputs=[status_textbox]
    )
    
    save_pdf_btn.click(
        fn=save_pdf_wrapper,
        inputs=[output_textbox],
        outputs=[status_textbox]
    )

if __name__ == "__main__":
    try:
        port = int(os.getenv('PORT', 7860))
        demo.launch(
            server_name='127.0.0.1',
            server_port=port
        )
    except Exception as e:
        print(f"Error launching app: {e}")