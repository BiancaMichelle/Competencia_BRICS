# formulario para el chat
from django import forms


class ChatForm(forms.Form):
    """Formulario para el chat"""
    
    message = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={
            'class': 'form-control chat-input',
            'placeholder': 'Type your message...',
            'autocomplete': 'off',
            'id': 'messageInput'
        }),
        label='',
        required=True
    )
    
    def clean_message(self):
        """Validación del mensaje"""
        message = self.cleaned_data['message']
        
        if not message.strip():
            raise forms.ValidationError('Message cannot be empty.')

        if len(message.strip()) < 1:
            raise forms.ValidationError('Message is too short.')

        return message.strip()