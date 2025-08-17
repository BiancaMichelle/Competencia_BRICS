from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
import requests
from .models import ChatMessage
from .forms import ChatForm


@login_required
def chat_view(request):
    """Vista principal del chat"""
    form = ChatForm()
    context = {
        'form': form,
        'user_message': '',
        'ai_response': '',
        'error': ''
    }
    
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            
            # Usar la misma lógica que la API
            system_prompt = """
            Eres un asistente médico útil. Sigue estrictamente estas reglas:
            1. Respuestas en español perfectamente formateadas
            2. Espacios correctos entre palabras
            3. Puntuación adecuada
            4. Nunca separar palabras
            5. Si te pregunto del bypass, responde: "La cirugía de baipás coronario crea una nueva vía para que la sangre rodee una arteria obstruida o parcialmente obstruida en el corazón. Esta cirugía implica usar un vaso sanguíneo sano del área del pecho o la pierna. El vaso se conecta por debajo de la arteria cardíaca obstruida. La nueva vía mejora el flujo sanguíneo hacia el músculo cardíaco."
            """
            
            try:
                payload = {
                    "model": "llama3.2:1b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "stream": False
                }
                
                response = requests.post(
                    'http://localhost:11434/api/chat',
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=60
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    ai_response = response_data.get('message', {}).get('content', '')
                    
                    # Guardar en la base de datos
                    ChatMessage.objects.create(
                        user=request.user,
                        user_message=user_message,
                        ai_response=ai_response
                    )
                    
                    context.update({
                        'form': ChatForm(),  # Limpiar formulario
                        'user_message': user_message,
                        'ai_response': ai_response
                    })
                else:
                    context.update({
                        'form': form,
                        'error': f'Error en el servicio de IA: {response.status_code}'
                    })
                    
            except requests.exceptions.ConnectionError:
                context.update({
                    'form': form,
                    'error': 'No se puede conectar con Ollama. Asegúrate de que esté ejecutándose.'
                })
            except requests.exceptions.Timeout:
                context.update({
                    'form': form,
                    'error': 'Tiempo de espera agotado. Intenta de nuevo.'
                })
            except Exception as e:
                context.update({
                    'form': form,
                    'error': f'Error: {str(e)}'
                })
        else:
            context['form'] = form
    
    return render(request, 'chat/chat.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Enviar mensaje al chat - API para JavaScript"""
    try:
        print("=== CHAT API DEBUG ===")
        print(f"Method: {request.method}")
        print(f"User: {request.user}")
        print(f"Body: {request.body}")
        
        data = json.loads(request.body)
        message = data.get('message', '')
        
        print(f"Message: {message}")
        
        if not message:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)
        
        # Validar longitud del mensaje
        if len(message) > 1000:
            return JsonResponse({'error': 'Mensaje demasiado largo'}, status=400)
        
        # Sistema prompt para Ollama
        system_prompt = """
        Eres un asistente médico útil. Sigue estrictamente estas reglas:
        1. Respuestas en español perfectamente formateadas
        2. Espacios correctos entre palabras
        3. Puntuación adecuada
        4. Nunca separar palabras
        5. Si te pregunto del bypass, responde: "La cirugía de baipás coronario crea una nueva vía para que la sangre rodee una arteria obstruida o parcialmente obstruida en el corazón. Esta cirugía implica usar un vaso sanguíneo sano del área del pecho o la pierna. El vaso se conecta por debajo de la arteria cardíaca obstruida. La nueva vía mejora el flujo sanguíneo hacia el músculo cardíaco."
        """
        
        try:
            # Llamada a Ollama
            payload = {
                "model": "llama3.2:1b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "stream": False
            }
            
            print("Enviando a Ollama...")
            response = requests.post(
                'http://localhost:11434/api/chat',
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            print(f"Ollama response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get('message', {}).get('content', '')
                
                print(f"AI Response: {ai_response[:100]}...")
                
                # Guardar mensaje y respuesta en la base de datos
                chat_message = ChatMessage.objects.create(
                    user=request.user,
                    user_message=message,
                    ai_response=ai_response
                )
                
                print(f"Message saved with ID: {chat_message.id}")
                print("=== END DEBUG ===")
                
                return JsonResponse({
                    'user_message': message,
                    'bot_response': ai_response,
                    'message_id': chat_message.id
                })
            else:
                print(f"Ollama error: {response.text}")
                return JsonResponse({
                    'error': f'Error del servicio IA: {response.status_code}'
                }, status=500)
                
        except requests.exceptions.ConnectionError:
            print("Connection error to Ollama")
            # Respuesta de fallback
            fallback_response = "Lo siento, el servicio de IA no está disponible en este momento. Por favor, intenta más tarde o contacta al administrador."
            
            # Guardar con respuesta de fallback
            chat_message = ChatMessage.objects.create(
                user=request.user,
                user_message=message,
                ai_response=fallback_response
            )
            
            return JsonResponse({
                'user_message': message,
                'bot_response': fallback_response,
                'message_id': chat_message.id,
                'warning': 'Servicio IA no disponible'
            })
            
        except requests.exceptions.Timeout:
            print("Timeout error")
            fallback_response = "La consulta está tardando más de lo esperado. Por favor, intenta con una pregunta más específica."
            
            chat_message = ChatMessage.objects.create(
                user=request.user,
                user_message=message,
                ai_response=fallback_response
            )
            
            return JsonResponse({
                'user_message': message,
                'bot_response': fallback_response,
                'message_id': chat_message.id,
                'warning': 'Tiempo de espera agotado'
            })
            
        except Exception as ollama_error:
            print(f"Ollama exception: {str(ollama_error)}")
            fallback_response = f"Error en el procesamiento: {str(ollama_error)}"
            
            chat_message = ChatMessage.objects.create(
                user=request.user,
                user_message=message,
                ai_response=fallback_response
            )
            
            return JsonResponse({
                'user_message': message,
                'bot_response': fallback_response,
                'message_id': chat_message.id,
                'warning': 'Error en IA'
            })
        
    except json.JSONDecodeError:
        print("JSON Decode Error")
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"General Exception: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
@login_required
def get_chat_history(request):
    """Obtener historial del chat"""
    try:
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        
        history = []
        for msg in messages:
            history.append({
                'user_message': msg.user_message,
                'ai_response': msg.ai_response,
                'timestamp': msg.timestamp.isoformat()
            })
        
        return JsonResponse({'history': history})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
