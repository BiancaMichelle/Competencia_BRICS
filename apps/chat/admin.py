from django.contrib import admin
from django.utils.html import format_html
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message_short', 'ai_response_short', 'timestamp', 'conversation_length')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user_message', 'ai_response')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    def user_message_short(self, obj):
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
    user_message_short.short_description = 'User Message'

    def ai_response_short(self, obj):
        return obj.ai_response[:50] + '...' if len(obj.ai_response) > 50 else obj.ai_response
    ai_response_short.short_description = 'AI Response'

    def conversation_length(self, obj):
        user_length = len(obj.user_message)
        ai_length = len(obj.ai_response)
        total = user_length + ai_length
        
        if total > 500:
            color = 'red'
        elif total > 200:
            color = 'orange'
        else:
            color = 'green'
            
        return format_html(
            '<span style="color: {};">{} caracteres</span>',
            color,
            total
        )
    conversation_length.short_description = 'Total Length'

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'timestamp')
        }),
        ('Conversation', {
            'fields': ('user_message', 'ai_response'),
            'description': 'Full conversation between the user and the AI'
        }),
        ('Metadata', {
            'fields': ('session_key',),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    # Acciones personalizadas
    actions = ['delete_old_messages']
    
    def delete_old_messages(self, request, queryset):
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=30)
        old_messages = ChatMessage.objects.filter(timestamp__lt=cutoff_date)
        count = old_messages.count()
        old_messages.delete()
        self.message_user(request, f'{count} old messages deleted (older than 30 days).')
    delete_old_messages.short_description = 'Delete old messages (>30 days)'
