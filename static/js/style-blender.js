class StyleBlender {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.radius = 200;
        this.centerX = 250;
        this.centerY = 250;
        this.cursorX = 250;
        this.cursorY = 250;
        this.dragging = false;
        this.styles = [];
        
        this.loadStyles();
        this.setupEventListeners();
    }
    
    async loadStyles() {
        try {
            const response = await fetch('/api/styles');
            const stylesData = await response.json();
            
            this.styles = Object.entries(stylesData)
                .filter(([name, data]) => !data.is_default)
                .map(([name, data]) => ({
                    name: name,
                    angle: data.angle || 0,
                    color: data.color || '#888'
                }));
            
            this.draw();
        } catch (error) {
            console.error('Failed to load styles:', error);
        }
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const dist = Math.sqrt(
                Math.pow(x - this.cursorX, 2) + 
                Math.pow(y - this.cursorY, 2)
            );
            
            if (dist < 15) {
                this.dragging = true;
            }
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            if (!this.dragging) return;
            
            const rect = this.canvas.getBoundingClientRect();
            let x = e.clientX - rect.left;
            let y = e.clientY - rect.top;
            
            const dx = x - this.centerX;
            const dy = y - this.centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            if (dist > this.radius) {
                x = this.centerX + (dx / dist) * this.radius;
                y = this.centerY + (dy / dist) * this.radius;
            }
            
            this.cursorX = x;
            this.cursorY = y;
            this.draw();
            this.updateWeights();
        });
        
        this.canvas.addEventListener('mouseup', () => {
            this.dragging = false;
        });
        
        this.canvas.addEventListener('mouseleave', () => {
            this.dragging = false;
        });
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw outer circle
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, this.radius, 0, 2 * Math.PI);
        this.ctx.strokeStyle = '#444';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // Draw style points
        this.styles.forEach(style => {
            const angle = (style.angle * Math.PI) / 180;
            const x = this.centerX + this.radius * Math.cos(angle);
            const y = this.centerY + this.radius * Math.sin(angle);
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, 10, 0, 2 * Math.PI);
            this.ctx.fillStyle = style.color;
            this.ctx.fill();
            
            // Label
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '12px Arial';
            this.ctx.fillText(style.name, x + 15, y + 5);
        });
        
        // Draw center (Default)
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, 8, 0, 2 * Math.PI);
        this.ctx.fillStyle = '#FF1B6D';
        this.ctx.fill();
        this.ctx.fillStyle = '#fff';
        this.ctx.fillText('Default', this.centerX + 10, this.centerY);
        
        // Draw cursor
        this.ctx.beginPath();
        this.ctx.arc(this.cursorX, this.cursorY, 12, 0, 2 * Math.PI);
        this.ctx.fillStyle = 'rgba(255, 27, 109, 0.5)';
        this.ctx.fill();
        this.ctx.strokeStyle = '#FF1B6D';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
    }
    
    calculateWeights() {
        const weights = { 'Default': 1.0 };
        
        const dx = this.cursorX - this.centerX;
        const dy = this.cursorY - this.centerY;
        const distFromCenter = Math.sqrt(dx * dx + dy * dy);
        
        if (distFromCenter < 5) {
            return weights;
        }
        
        const cursorAngle = Math.atan2(dy, dx) * (180 / Math.PI);
        
        const defaultWeight = 1 - (distFromCenter / this.radius);
        weights['Default'] = Math.max(0, defaultWeight);
        
        this.styles.forEach(style => {
            let angleDiff = Math.abs(cursorAngle - style.angle);
            if (angleDiff > 180) angleDiff = 360 - angleDiff;
            
            const angleProximity = Math.max(0, 1 - (angleDiff / 60));
            const distanceInfluence = distFromCenter / this.radius;
            
            const weight = angleProximity * distanceInfluence;
            if (weight > 0.1) {
                weights[style.name] = weight;
            }
        });
        
        const total = Object.values(weights).reduce((a, b) => a + b, 0);
        Object.keys(weights).forEach(key => {
            weights[key] = weights[key] / total;
        });
        
        return weights;
    }
    
    updateWeights() {
        const weights = this.calculateWeights();
        
        const display = document.getElementById('weights-display');
        display.innerHTML = Object.entries(weights)
            .filter(([_, w]) => w > 0.05)
            .map(([style, weight]) => 
                `${style}: ${(weight * 100).toFixed(0)}%`
            )
            .join('<br>');
        
        this.onWeightsChange(weights);
    }
    
    onWeightsChange(weights) {
        // Override this method
        console.log('Weights updated:', weights);
    }

    getWeights() {
        return this.calculateWeights();
    }
}