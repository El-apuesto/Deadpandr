import os
import time
from typing import List

def save_output(jokes: List[str], fmt='txt'):
    """Save generated jokes to file"""
    try:
        # Create exports directory
        exports_dir = 'exports'
        os.makedirs(exports_dir, exist_ok=True)
        
        # Generate timestamped filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if fmt == 'txt':
            filename = f"dark_comedy_jokes_{timestamp}.txt"
            filepath = os.path.join(exports_dir, filename)
            
            # Write jokes to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("🎭 Dark Comedy Jokes 🎭\n")
                f.write("=" * 50 + "\n\n")
                f.write("\n\n".join(jokes))
                f.write(f"\n\n\nGenerated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return filepath
        
        elif fmt == 'pdf':
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                
                filename = f"dark_comedy_jokes_{timestamp}.pdf"
                filepath = os.path.join(exports_dir, filename)
                
                # Create PDF
                c = canvas.Canvas(filepath, pagesize=letter)
                width, height = letter
                
                # Set up fonts and spacing
                c.setFont("Helvetica-Bold", 16)
                y_position = height - 50
                c.drawString(50, y_position, "🎭 Dark Comedy Jokes 🎭")
                
                c.setFont("Helvetica", 11)
                y_position -= 40
                
                # Add jokes to PDF
                for i, joke in enumerate(jokes, 1):
                    # Check if we need a new page
                    if y_position < 100:
                        c.showPage()
                        c.setFont("Helvetica", 11)
                        y_position = height - 50
                    
                    # Add joke number
                    c.setFont("Helvetica-Bold", 11)
                    c.drawString(50, y_position, f"Joke {i}:")
                    y_position -= 20
                    
                    # Add joke text (handle line wrapping)
                    c.setFont("Helvetica", 11)
                    lines = joke.split('\n')
                    for line in lines:
                        # Simple line wrapping
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            test_line = current_line + word + " "
                            if len(test_line) > 80:  # Approximate character limit
                                if current_line:
                                    c.drawString(70, y_position, current_line.strip())
                                    y_position -= 15
                                    if y_position < 100:
                                        c.showPage()
                                        c.setFont("Helvetica", 11)
                                        y_position = height - 50
                                current_line = word + " "
                            else:
                                current_line = test_line
                        
                        if current_line:
                            c.drawString(70, y_position, current_line.strip())
                            y_position -= 15
                            if y_position < 100:
                                c.showPage()
                                c.setFont("Helvetica", 11)
                                y_position = height - 50
                    
                    y_position -= 20  # Extra space between jokes
                
                # Add timestamp
                if y_position < 150:
                    c.showPage()
                    y_position = height - 50
                
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(50, 50, f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                c.save()
                return filepath
                
            except ImportError:
                return "Error: Install reportlab for PDF support (pip install reportlab)"
        
        else:
            return f"Error: Unsupported format '{fmt}'"
    
    except Exception as e:
        return f"Error: {str(e)}"