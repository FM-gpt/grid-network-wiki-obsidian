// Chatbot Interface
class Chatbox {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.api = new API();
        this.init();
    }

    init() {
        this.createUI();
        this.setupEventListeners();
    }

    createUI() {
        const chatbox = document.createElement('div');
        chatbox.id = 'chatbox';
        chatbox.className = 'chatbox';
        chatbox.innerHTML = `
            <div class="chatbox-header">
                <h3>AI Assistant</h3>
                <button class="chatbox-close" onclick="chatbox.toggle()">✕</button>
            </div>
            <div class="chatbox-messages" id="chatbox-messages">
                <div class="message bot">
                    <div class="message-content">
                        Hello! I'm your GRID Wiki assistant. How can I help you today?
                    </div>
                </div>
            </div>
            <div class="chatbox-input">
                <input type="text" id="chatbox-input" placeholder="Ask about GRID Wiki..." 
                       onkeypress="if(event.key==='Enter')chatbox.sendMessage()">
                <button onclick="chatbox.sendMessage()">Send</button>
            </div>
        `;
        document.body.appendChild(chatbox);
    }

    setupEventListeners() {
        // Open chatbox button
        const openBtn = document.createElement('button');
        openBtn.id = 'chatbox-open';
        openBtn.className = 'chatbox-open';
        openBtn.innerHTML = '💬';
        openBtn.onclick = () => this.toggle();
        document.body.appendChild(openBtn);
    }

    toggle() {
        this.isOpen = !this.isOpen;
        const chatbox = document.getElementById('chatbox');
        if (chatbox) {
            chatbox.classList.toggle('open', this.isOpen);
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbox-input');
        const message = input.value.trim();
        if (!message) return;

        // Add user message
        this.addMessage('user', message);
        input.value = '';

        // Show loading
        this.addMessage('bot', 'Thinking...', true);

        try {
            const response = await this.api.post('/api/chat', { message });
            // Remove loading message
            const loadingMessages = document.querySelectorAll('.message.loading');
            loadingMessages.forEach(msg => msg.remove());
            
            // Add bot response
            this.addMessage('bot', response.reply || response.message || 'No response received');
        } catch (error) {
            // Remove loading message
            const loadingMessages = document.querySelectorAll('.message.loading');
            loadingMessages.forEach(msg => msg.remove());
            
            // Add error message
            this.addMessage('bot', `Error: ${error.message}`);
        }
    }

    addMessage(role, content, isLoading = false) {
        const messagesContainer = document.getElementById('chatbox-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}${isLoading ? ' loading' : ''}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                ${content}
                ${isLoading ? '<span class="typing-indicator">...</span>' : ''}
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Initialize chatbox
document.addEventListener('DOMContentLoaded', () => {
    window.chatbox = new Chatbox();
});
