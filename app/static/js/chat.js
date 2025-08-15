// JavaScript para el chat ArQa
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const streamBtn = document.getElementById('stream-btn');
    const chatMessages = document.getElementById('chat-messages');
    const streamingMessage = document.getElementById('streaming-message');
    const streamingContent = document.getElementById('streaming-content');

    // Auto-scroll to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Crear mensaje en el DOM
    function createMessage(content, isUser = false) {
        const chatDiv = document.createElement('div');
        chatDiv.className = `chat ${isUser ? 'chat-end' : 'chat-start'} mb-4`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'chat-image avatar';
        avatarDiv.innerHTML = `
            <div class="w-10 rounded-full">
                <svg class="w-full h-full p-2 ${isUser ? 'bg-blue-500' : 'bg-green-500'} text-white rounded-full" fill="currentColor" viewBox="0 0 20 20">
                    ${isUser ? 
                        '<path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>' :
                        '<path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"></path><path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"></path>'
                    }
                </svg>
            </div>
        `;
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'chat-header';
        headerDiv.textContent = isUser ? 'Tú' : 'ArQa Chat-IA';
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `chat-bubble ${isUser ? 'chat-bubble-primary' : 'chat-bubble-accent'}`;
        bubbleDiv.textContent = content;
        
        chatDiv.appendChild(avatarDiv);
        chatDiv.appendChild(headerDiv);
        chatDiv.appendChild(bubbleDiv);
        
        return chatDiv;
    }

    // Limpiar mensajes de bienvenida
    function clearWelcomeMessages() {
        const welcomeMessage = document.querySelector('.text-center.mt-12');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
    }

    // Enviar mensaje normal
    async function sendMessage(message) {
        try {
            const response = await fetch('/chat/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            return data.response;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }

    // Enviar mensaje con streaming
    async function sendStreamingMessage(message) {
        try {
            const response = await fetch('/chat/api/chat/stream/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            // Mostrar mensaje de streaming
            streamingMessage.style.display = 'block';
            streamingContent.textContent = '';
            scrollToBottom();

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Mantener la línea incompleta
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const jsonData = JSON.parse(line.slice(6));
                            
                            if (jsonData.chunk) {
                                streamingContent.textContent += jsonData.chunk;
                                scrollToBottom();
                            }
                            
                            if (jsonData.done) {
                                // Finalizar streaming
                                const finalContent = streamingContent.textContent;
                                streamingMessage.style.display = 'none';
                                
                                // Crear mensaje permanente
                                const aiMessage = createMessage(finalContent, false);
                                chatMessages.appendChild(aiMessage);
                                scrollToBottom();
                                return;
                            }
                            
                            if (jsonData.error) {
                                throw new Error(jsonData.error);
                            }
                        } catch (e) {
                            console.warn('Error parsing JSON:', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error en streaming:', error);
            streamingMessage.style.display = 'none';
            
            // Mostrar error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-error mb-4';
            errorDiv.innerHTML = `
                <svg class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>Error: ${error.message}</span>
            `;
            chatMessages.appendChild(errorDiv);
            scrollToBottom();
        }
    }

    // Obtener cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Manejar envío normal
    sendBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;

        // Limpiar mensajes de bienvenida
        clearWelcomeMessages();

        // Mostrar mensaje del usuario
        const userMessage = createMessage(message, true);
        chatMessages.appendChild(userMessage);
        scrollToBottom();

        // Limpiar input y deshabilitar botones
        messageInput.value = '';
        sendBtn.disabled = true;
        streamBtn.disabled = true;
        sendBtn.classList.add('loading');

        try {
            const response = await sendMessage(message);
            
            // Mostrar respuesta de la IA
            const aiMessage = createMessage(response, false);
            chatMessages.appendChild(aiMessage);
            scrollToBottom();
            
        } catch (error) {
            // Mostrar error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-error mb-4';
            errorDiv.innerHTML = `
                <svg class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>Error: ${error.message}</span>
            `;
            chatMessages.appendChild(errorDiv);
            scrollToBottom();
        } finally {
            // Rehabilitar botones
            sendBtn.disabled = false;
            streamBtn.disabled = false;
            sendBtn.classList.remove('loading');
        }
    });

    // Manejar envío con streaming
    streamBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;

        // Limpiar mensajes de bienvenida
        clearWelcomeMessages();

        // Mostrar mensaje del usuario
        const userMessage = createMessage(message, true);
        chatMessages.appendChild(userMessage);
        scrollToBottom();

        // Limpiar input y deshabilitar botones
        messageInput.value = '';
        sendBtn.disabled = true;
        streamBtn.disabled = true;
        streamBtn.classList.add('loading');

        try {
            await sendStreamingMessage(message);
        } catch (error) {
            console.error('Error en streaming:', error);
        } finally {
            // Rehabilitar botones
            sendBtn.disabled = false;
            streamBtn.disabled = false;
            streamBtn.classList.remove('loading');
        }
    });

    // Enviar con Enter
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendBtn.click();
        }
    });

    // Focus automático en el input
    messageInput.focus();

    // Auto-scroll si ya hay mensajes
    if (chatMessages.children.length > 0) {
        scrollToBottom();
    }
});
