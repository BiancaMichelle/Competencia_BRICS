import traceback
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.users.models import Paciente, Alergia, CondicionMedica, Tratamiento, Antecedente, PruebaLaboratorio, Cirugia
import json
import requests
from .models import ChatMessage
from .forms import ChatForm


def build_medical_history(paciente):
    """Return a string with the patient's medical history (safe if paciente is None)."""
    if not paciente:
        return ""
    parts = []
    for a in paciente.alergias.all():
        parts.append(f"Alergia: {a.sustancia}, Severidad: {a.severidad}, Diagnóstico: {a.fecha_diagnostico}")
    for c in paciente.condiciones.all():
        parts.append(f"Condición: {c.codigo}, Estado: {c.estado}, Diagnóstico: {c.fecha_diagnostico}")
    for t in paciente.tratamientos.all():
        med = t.medicamento.nombre if getattr(t, "medicamento", None) else "Sin medicamento"
        parts.append(f"Tratamiento: {t.descripcion}, Medicamento: {med}, Desde: {t.fecha_inicio}, Hasta: {t.fecha_fin}")
    for ant in paciente.antecedentes.all():
        parts.append(f"Antecedente: {ant.tipo}, Descripción: {ant.descripcion}")
    for cir in paciente.cirugias.all():
        parts.append(f"Cirugía: {cir.nombre_cirugia}, Fecha: {cir.fecha_cirugia}, Estado: {cir.estado}")
    for p in paciente.pruebas.all():
        parts.append(f"Prueba: {p.nombre_prueba}, Fecha: {p.fecha_realizacion}, Resultados: {p.resultados}")
    return "\n".join(parts)

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

            try:
                paciente = Paciente.objects.get(user=request.user)
            except Paciente.DoesNotExist:
                paciente = None
            except Exception:
                tb = traceback.format_exc()
                context.update({'form': form, 'error': f'Error leyendo Paciente: {tb[:1000]}'})
                return render(request, 'chat/chat.html', context)

            medical_history = build_medical_history(paciente)

            system_prompt = f"""
            Eres un asistente virtual de inteligencia artificial especializado en medicina.

            Historial clínico del usuario:
            {medical_history if medical_history else "No hay datos clínicos registrados."}

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
    """Enviar mensaje al chat - DEBUG robusto: siempre devuelve JsonResponse."""
    try:
        print("=== CHAT API DEBUG ===")
        print(f"Method: {request.method}")
        print(f"User: {request.user!r}")
        print(f"Body raw: {request.body}")

        # Parseo seguro del body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            tb = traceback.format_exc()
            print("JSONDecodeError:\n", tb)
            return JsonResponse({'error': 'JSON inválido', 'traceback': tb[:2000]}, status=400)

        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)
        if len(message) > 1000:
            return JsonResponse({'error': 'Mensaje demasiado largo'}, status=400)

        # Obtener paciente
        try:
            paciente = Paciente.objects.get(user=request.user)
        except Paciente.DoesNotExist:
            paciente = None
        except Exception:
            tb = traceback.format_exc()
            print("Error al obtener Paciente:\n", tb)
            return JsonResponse({'error': 'Error leyendo Paciente', 'traceback': tb[:2000]}, status=500)

        # Construir historial
        try:
            medical_history = build_medical_history(paciente)
        except Exception:
            tb = traceback.format_exc()
            print("Error construyendo medical_history:\n", tb)
            return JsonResponse({'error': 'Error construyendo medical_history', 'traceback': tb[:2000]}, status=500)

        print("Medical history preview:", medical_history[:500])

        # Preparar prompt
        # instrucción clara
        system_instruction = (
            "Eres un asistente virtual médico. En tus respuestas debes usar la información del 'Historial clínico del usuario' "
            "que se proporciona abajo para responder las preguntas. "
            "No digas que no tienes acceso a los datos; en cambio usa y cita el historial entregado. "
            "Responde con claridad, cita los datos relevantes y recomienda consultar un profesional si es necesario."
        )

        # pon el historial COMO mensaje separado (evita ambigüedades)
        medical_history_msg = f"Historial clínico del usuario:\n{medical_history if medical_history else 'No hay datos clínicos registrados.'}"

        payload = {
            "model": "llama3.2:1b",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "system", "content": medical_history_msg},   # si Ollama acepta varios system; si no, usar role "user"
                {"role": "user", "content": message}
            ],
            "stream": False
        }

        system_prompt = f"""
        Eres un asistente virtual de inteligencia artificial especializado en medicina.

        Historial clínico del usuario:
        {medical_history}

        (Coloca aquí el resto de tu prompt y reglas de estilo...)
        """

        payload = {
            "model": "llama3.2:1b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "stream": False
        }

        # Llamada a Ollama (requests.post)
        try:
            response = requests.post(
                'http://localhost:11434/api/chat',
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
        except Exception:
            tb = traceback.format_exc()
            print("Error llamando a Ollama (requests.post):\n", tb)
            return JsonResponse({'error': 'Error conectando con servicio IA', 'traceback': tb[:2000]}, status=500)

        print(f"Ollama status: {getattr(response, 'status_code', 'no-response')}")

        # Manejo de respuesta de Ollama
        if response is None:
            return JsonResponse({'error': 'Sin respuesta de servicio IA'}, status=500)

        if response.status_code != 200:
            body_text = getattr(response, 'text', '<no body>')
            print("Ollama returned non-200:", response.status_code, body_text[:1000])
            return JsonResponse({'error': f'Error del servicio IA: {response.status_code}', 'body': body_text[:2000]}, status=500)

        # después de response = requests.post(...)
        print("Ollama status:", getattr(response, "status_code", None))
        print("Ollama raw body preview:", getattr(response, "text", "")[:2000])

        # ahora parsear a JSON con manejo
        try:
            response_data = response.json()
        except Exception:
            tb = traceback.format_exc()
            print("Error parseando JSON de Ollama:\n", tb)
            return JsonResponse({'error': 'Respuesta IA no JSON', 'body_preview': response.text[:2000], 'traceback': tb[:2000]}, status=500)

        ai_response = response_data.get('message', {}).get('content', '')
        print("AI response (preview):", ai_response[:1000])

        # Intentar parsear JSON
        try:
            response_data = response.json()
        except Exception:
            tb = traceback.format_exc()
            body_text = getattr(response, 'text', '<no body>')
            print("Error parseando JSON de la respuesta de Ollama:\n", tb)
            return JsonResponse({'error': 'Respuesta IA no JSON', 'traceback': tb[:2000], 'body': body_text[:2000]}, status=500)

        ai_response = response_data.get('message', {}).get('content', '')

        # Guardar el chat
        try:
            chat_message = ChatMessage.objects.create(
                user=request.user,
                user_message=message,
                ai_response=ai_response
            )
        except Exception:
            tb = traceback.format_exc()
            print("Error guardando ChatMessage:\n", tb)
            return JsonResponse({'error': 'Error guardando mensaje', 'traceback': tb[:2000]}, status=500)

        # DEV: devolvemos medical_history para verificar (quitar en prod)
        return JsonResponse({
            'user_message': message,
            'bot_response': ai_response,
            'message_id': chat_message.id,
            'medical_history_debug': medical_history
        }, status=200)

    except Exception:
        tb = traceback.format_exc()
        print("UNHANDLED EXCEPTION:\n", tb)
        return JsonResponse({'error': 'Excepción en servidor', 'traceback': tb[:3000]}, status=500)
    
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
