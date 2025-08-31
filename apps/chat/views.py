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
        parts.append(f"Alergy: {a.sustancia}, Severity: {a.severidad}, Diagnosis: {a.fecha_diagnostico}")
    for c in paciente.condiciones.all():
        parts.append(f"Condition: {c.codigo}, Status: {c.estado}, Diagnosis: {c.fecha_diagnostico}")
    for t in paciente.tratamientos.all():
        med = t.medicamento.nombre if getattr(t, "medicamento", None) else "No medication"
        parts.append(f"Treatment: {t.descripcion}, Medication: {med}, From: {t.fecha_inicio}, Until: {t.fecha_fin}")
    for ant in paciente.antecedentes.all():
        parts.append(f"Antecedent: {ant.tipo}, Description: {ant.descripcion}")
    for cir in paciente.cirugias.all():
        parts.append(f"Surgery: {cir.nombre_cirugia}, Date: {cir.fecha_cirugia}, Status: {cir.estado}")
    for p in paciente.pruebas.all():
        parts.append(f"Test: {p.nombre_prueba}, Date: {p.fecha_realizacion}, Results: {p.resultados}")
    return "\n".join(parts)

@login_required
def chat_view(request):
    """Main chat view"""
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
                context.update({'form': form, 'error': f'Error reading Patient: {tb[:1000]}'})
                return render(request, 'chat/chat.html', context)

            medical_history = build_medical_history(paciente)

            system_prompt = f"""
            You are a virtual assistant specialized in medicine.

            Patient's medical history:
            {medical_history if medical_history else "No clinical data registered."}

            Your main objective is to assist users with reliable medical information,
            symptom guides, treatments, prevention, and education about diseases.
            You must always act professionally, clearly, empathetically, and understandably
            for people without medical training.

            Rules and response style:
            1. Use simple language, avoiding complicated technical terms when possible.
            2. Provide evidence-based information, but remember to clarify that you do not replace professional medical consultation.
            3. When possible, offer general steps for prevention, management, or wellness advice.
            4. If the user describes symptoms, ask clarifying questions before giving suggestions.
            5. Never issue definitive diagnoses; focus on guidance and education.
            6. Respond in a cordial, kind, and empathetic manner.
            7. Keep each response clear and structured: introduce the main idea, then details, and conclude with recommendations or next steps.
            8. If you don't know the answer, admit it and suggest consulting a healthcare professional.

            Response format:
            - Greetings: short and friendly.
            - Information: clear, structured, and concise.
            - Caution: always indicate to consult a doctor if necessary.
            - References: mention reliable sources if applicable (WHO, CDC, recognized medical institutions).

            You are a responsible and reliable medical assistant AI, aimed at helping without replacing the judgment of a health professional.
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
                        'error': f'Error in IA service: {response.status_code}'
                    })
                    
            except requests.exceptions.ConnectionError:
                context.update({
                    'form': form,
                    'error': 'Cannot connect to Ollama. Make sure it is running.'
                })
            except requests.exceptions.Timeout:
                context.update({
                    'form': form,
                    'error': 'Request timed out. Please try again.'
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
            return JsonResponse({'error': 'Invalid JSON', 'traceback': tb[:2000]}, status=400)

        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'error': 'Empty message'}, status=400)
        if len(message) > 1000:
            return JsonResponse({'error': 'Message too long'}, status=400)

        # Obtener paciente
        try:
            paciente = Paciente.objects.get(user=request.user)
        except Paciente.DoesNotExist:
            paciente = None
        except Exception:
            tb = traceback.format_exc()
            print("Error getting Pacient:\n", tb)
            return JsonResponse({'error': 'Error reading Pacient', 'traceback': tb[:2000]}, status=500)

        # Construir historial
        try:
            medical_history = build_medical_history(paciente)
        except Exception:
            tb = traceback.format_exc()
            print("Error building medical_history:\n", tb)
            return JsonResponse({'error': 'Error building medical_history', 'traceback': tb[:2000]}, status=500)

        print("Medical history preview:", medical_history[:500])

        # Preparar prompt
        # instrucción clara
        system_instruction = (
            "You are a virtual medical assistant. In your responses, you must use the information from the 'User's medical history' "
            "provided below to answer questions. "
            "Do not say you do not have access to the data; instead, use and cite the provided history. "
            "Respond clearly, cite relevant data, and recommend consulting a professional if necessary."
        )

        # pon el historial COMO mensaje separado (evita ambigüedades)
        medical_history_msg = f"Clinical medical history of the user:\n{medical_history if medical_history else 'No clinical data registered.'}"

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
        you are a virtual medical assistant.

        Clinical medical history of the user:
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
            print("Error calling Ollama (requests.post):\n", tb)
            return JsonResponse({'error': 'Error connecting to AI service', 'traceback': tb[:2000]}, status=500)

        print(f"Ollama status: {getattr(response, 'status_code', 'no-response')}")

        # Manejo de respuesta de Ollama
        if response is None:
            return JsonResponse({'error': 'Without response from AI service'}, status=500)

        if response.status_code != 200:
            body_text = getattr(response, 'text', '<no body>')
            print("Ollama returned non-200:", response.status_code, body_text[:1000])
            return JsonResponse({'error': f'Error from AI service: {response.status_code}', 'body': body_text[:2000]}, status=500)

        # después de response = requests.post(...)
        print("Ollama status:", getattr(response, "status_code", None))
        print("Ollama raw body preview:", getattr(response, "text", "")[:2000])

        # ahora parsear a JSON con manejo
        try:
            response_data = response.json()
        except Exception:
            tb = traceback.format_exc()
            print("Error parsing JSON from Ollama:\n", tb)
            return JsonResponse({'error': 'AI response not JSON', 'body_preview': response.text[:2000], 'traceback': tb[:2000]}, status=500)

        ai_response = response_data.get('message', {}).get('content', '')
        print("AI response (preview):", ai_response[:1000])

        # Intentar parsear JSON
        try:
            response_data = response.json()
        except Exception:
            tb = traceback.format_exc()
            body_text = getattr(response, 'text', '<no body>')
            print("Error parsing JSON from Ollama:\n", tb)
            return JsonResponse({'error': 'AI response not JSON', 'traceback': tb[:2000], 'body': body_text[:2000]}, status=500)

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
            print("Error saving ChatMessage:\n", tb)
            return JsonResponse({'error': 'Error saving message', 'traceback': tb[:2000]}, status=500)

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
        return JsonResponse({'error': 'Unhandled exception on server', 'traceback': tb[:3000]}, status=500)

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
