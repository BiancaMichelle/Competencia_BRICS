// JavaScript para el Chat Médico IA
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const messagesContainer = document.getElementById('messagesContainer');
    const typingIndicator = document.getElementById('typingIndicator');
    const charCount = document.getElementById('charCount');
    
    // Variables de estado
    let isTyping = false;

    // Verificar que todos los elementos existen
    if (!messageInput || !sendBtn || !messagesContainer) {
        console.error('Error: No se pudieron encontrar los elementos del chat');
        return;
    }

    // Auto-scroll al fondo del chat
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
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

    // Crear mensaje del usuario
    function createUserMessage(content) {
        const timestamp = new Date().toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat chat-end mb-4';
        messageDiv.innerHTML = `
            <div class="chat-image avatar">
                <div class="w-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                    </svg>
                </div>
            </div>
            <div class="chat-header text-sm text-gray-600 mb-1">
                Tú
                <time class="text-xs opacity-50 ml-2">${timestamp}</time>
            </div>
            <div class="chat-bubble chat-bubble-primary">${escapeHtml(content)}</div>
        `;
        
        return messageDiv;
    }

    // Crear mensaje de la IA
    function createAIMessage(content) {
        const timestamp = new Date().toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat chat-start mb-4';
        messageDiv.innerHTML = `
            <div class="chat-image avatar">
                <div class="w-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </div>
            </div>
            <div class="chat-header text-sm text-gray-600 mb-1">
                IA Médica
                <time class="text-xs opacity-50 ml-2">${timestamp}</time>
            </div>
            <div class="chat-bubble chat-bubble-accent">${escapeHtml(content)}</div>
        `;
        
        return messageDiv;
    }

    // Mostrar indicador de escritura
    function showTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.classList.remove('hidden');
            scrollToBottom();
        }
    }

    // Ocultar indicador de escritura
    function hideTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.classList.add('hidden');
        }
    }

    // Crear mensaje de error
    function createErrorMessage(errorText) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'alert alert-error mb-4';
        messageDiv.innerHTML = `
            <svg class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>Error: ${escapeHtml(errorText)}</span>
        `;
        return messageDiv;
    }

    // Enviar mensaje a la API
    async function sendMessage(message) {
        try {
            const response = await fetch('/chat/api/message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            return data.bot_response || data.response || data.message || 'Respuesta recibida';
            
        } catch (error) {
            console.error('Error al enviar mensaje:', error);
            throw error;
        }
    }

    // Manejar envío de mensaje
    async function handleSendMessage() {
        const message = messageInput.value.trim();
        
        if (!message || isTyping) {
            return;
        }

        // Validar longitud del mensaje
        if (message.length > 1000) {
            alert('El mensaje es demasiado largo (máximo 1000 caracteres)');
            return;
        }

        // Cambiar estado
        setTypingState(true);

        try {
            // Crear y mostrar mensaje del usuario
            const userMessage = createUserMessage(message);
            messagesContainer.appendChild(userMessage);
            
            // Limpiar input
            messageInput.value = '';
            updateCharCount();
            
            // Scroll al fondo
            scrollToBottom();
            
            // Mostrar indicador de escritura
            showTypingIndicator();

            // Simular delay para mejor UX
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Enviar mensaje a la API
            const response = await sendMessage(message);
            
            // Ocultar indicador de escritura
            hideTypingIndicator();
            
            // Crear y mostrar respuesta de la IA
            const aiMessage = createAIMessage(response);
            messagesContainer.appendChild(aiMessage);
            
            // Scroll al fondo
            scrollToBottom();
            
        } catch (error) {
            // Ocultar indicador de escritura
            hideTypingIndicator();
            
            // Mostrar mensaje de error
            const errorMessage = createErrorMessage(
                error.message || 'Error de conexión. Por favor, intenta de nuevo.'
            );
            messagesContainer.appendChild(errorMessage);
            scrollToBottom();
            
        } finally {
            // Cambiar estado
            setTypingState(false);
        }
    }

    // Cambiar estado de escritura
    function setTypingState(typing) {
        isTyping = typing;
        messageInput.disabled = typing;
        sendBtn.disabled = typing;
        
        if (typing) {
            sendBtn.innerHTML = `<div class="medical-loading"></div>`;
        } else {
            sendBtn.innerHTML = `
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/>
                </svg>
            `;
            messageInput.focus();
        }
    }

    // Actualizar contador de caracteres
    function updateCharCount() {
        if (charCount) {
            const count = messageInput.value.length;
            charCount.textContent = `${count}/1000`;
            
            // Cambiar color según proximidad al límite
            if (count > 900) {
                charCount.className = 'text-red-500 font-medium';
            } else if (count > 800) {
                charCount.className = 'text-yellow-500 font-medium';
            } else {
                charCount.className = 'text-gray-500';
            }
        }
    }

    // Escapar HTML para prevenir XSS
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }

    // Event listeners
    // Interceptar envío del formulario
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevenir envío normal del formulario
            handleSendMessage(); // Usar JavaScript instead
        });
    }

    sendBtn.addEventListener('click', function(e) {
        e.preventDefault();
        handleSendMessage();
    });

    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    if (charCount) {
        messageInput.addEventListener('input', updateCharCount);
    }

    // Configuración inicial
    messageInput.focus();
    updateCharCount();
    scrollToBottom();

    console.log('Chat médico inicializado correctamente');
});
