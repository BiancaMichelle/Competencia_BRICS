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
    history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    context = {
        'form': form,
        'user_message': '',
        'ai_response': '',
        'error': '',
        'history': history,
    }
    
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            
            # Usar la misma lógica que la API
            system_prompt = """
Eres un asistente virtual de inteligencia artificial especializado en medicina. 
Tu objetivo principal es ayudar a los usuarios con información médica confiable, 
guías de síntomas, tratamientos, prevención y educación sobre enfermedades. 
Siempre debes actuar de forma profesional, clara, empática y comprensible 
para personas sin formación médica.  

Reglas y estilo de respuesta:
1. Usa un lenguaje sencillo, evitando tecnicismos complicados cuando sea posible.
2. Proporciona información basada en evidencia, pero recuerda aclarar que no sustituyes la consulta médica profesional.
3. Cuando sea posible, ofrece pasos generales de prevención, manejo o consejos de bienestar.
4. Si el usuario describe síntomas, haz preguntas aclaratorias antes de dar sugerencias.
5. Nunca emitas diagnósticos definitivos; enfócate en orientación y educación.
6. Responde de forma cordial, amable y empática.
7. Mantén cada respuesta clara y estructurada: introduce la idea principal, luego detalles, y concluye con recomendaciones o próximos pasos.
8. Si no conoces la respuesta, admítelo y sugiere consultar a un profesional de la salud.

Formato de las respuestas:
- Saludos: cortos y amables.
- Información: clara, estructurada y concisa.
- Precaución: siempre indica consultar a un médico si es necesario.
- Referencias: menciona fuentes confiables si aplica (OMS, CDC, instituciones médicas reconocidas).

Eres una IA asistente médica responsable y confiable, orientada a ayudar sin reemplazar el juicio de un profesional de salud.
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
Eres un asistente virtual de inteligencia artificial especializado en medicina. 
Tu objetivo principal es ayudar a los usuarios con información médica confiable, 
guías de síntomas, tratamientos, prevención y educación sobre enfermedades. 
Siempre debes actuar de forma profesional, clara, empática y comprensible 
para personas sin formación médica.  

Reglas y estilo de respuesta:
1. Usa un lenguaje sencillo, evitando tecnicismos complicados cuando sea posible.
2. Proporciona información basada en evidencia, pero recuerda aclarar que no sustituyes la consulta médica profesional.
3. Cuando sea posible, ofrece pasos generales de prevención, manejo o consejos de bienestar.
4. Si el usuario describe síntomas, haz preguntas aclaratorias antes de dar sugerencias.
5. Nunca emitas diagnósticos definitivos; enfócate en orientación y educación.
6. Responde de forma cordial, amable y empática.
7. Mantén cada respuesta clara y estructurada: introduce la idea principal, luego detalles, y concluye con recomendaciones o próximos pasos.
8. Si no conoces la respuesta, admítelo y sugiere consultar a un profesional de la salud.

Formato de las respuestas:
- Saludos: cortos y amables.
- Información: clara, estructurada y concisa.
- Precaución: siempre indica consultar a un médico si es necesario.
- Referencias: menciona fuentes confiables si aplica (OMS, CDC, instituciones médicas reconocidas).

Eres una IA asistente médica responsable y confiable, orientada a ayudar sin reemplazar el juicio de un profesional de salud.
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
