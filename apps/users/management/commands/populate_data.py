from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.users.models import Paciente, Profesional
from datetime import date

class Command(BaseCommand):
    help = 'Populate database with sample patients and professionals'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample professionals
        professionals_data = [
            {
                'username': 'dr_garcia',
                'first_name': 'Carlos',
                'last_name': 'García',
                'email': 'carlos.garcia@hospital.com',
                'especialidad': 'medicina_general',
                'matricula': 'MG12345',
                'telefono': '+54911234567',
            },
            {
                'username': 'dr_martinez',
                'first_name': 'Ana',
                'last_name': 'Martínez',
                'email': 'ana.martinez@hospital.com',
                'especialidad': 'cardiologia',
                'matricula': 'CAR67890',
                'telefono': '+54911234568',
            },
            {
                'username': 'dr_lopez',
                'first_name': 'Miguel',
                'last_name': 'López',
                'email': 'miguel.lopez@hospital.com',
                'especialidad': 'neurologia',
                'matricula': 'NEU54321',
                'telefono': '+54911234569',
            },
        ]

        for prof_data in professionals_data:
            if not User.objects.filter(username=prof_data['username']).exists():
                user = User.objects.create_user(
                    username=prof_data['username'],
                    first_name=prof_data['first_name'],
                    last_name=prof_data['last_name'],
                    email=prof_data['email'],
                    password='password123'  # In production, use proper password hashing
                )
                profesional = Profesional.objects.create(
                    user=user,
                    especialidad=prof_data['especialidad'],
                    matricula=prof_data['matricula'],
                    telefono=prof_data['telefono'],
                )
                self.stdout.write(f'Created professional: {profesional}')

        # Create sample patients
        patients_data = [
            {
                'username': 'paciente1',
                'first_name': 'María',
                'last_name': 'Rodríguez',
                'email': 'maria.rodriguez@email.com',
                'cedula': '12345678',
                'genero': 'female',
                'fecha_nacimiento': date(1985, 5, 15),
                'tipo_sangre': 'O+',
                'telefono': '+54911234570',
                'direccion': 'Calle Ficticia 123',
                'ciudad': 'Buenos Aires',
            },
            {
                'username': 'paciente2',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'email': 'juan.perez@email.com',
                'cedula': '87654321',
                'genero': 'male',
                'fecha_nacimiento': date(1990, 8, 22),
                'tipo_sangre': 'A+',
                'telefono': '+54911234571',
                'direccion': 'Avenida Imaginaria 456',
                'ciudad': 'Córdoba',
            },
            {
                'username': 'paciente3',
                'first_name': 'Laura',
                'last_name': 'Fernández',
                'email': 'laura.fernandez@email.com',
                'cedula': '11223344',
                'genero': 'female',
                'fecha_nacimiento': date(1975, 12, 3),
                'tipo_sangre': 'B-',
                'telefono': '+54911234572',
                'direccion': 'Plaza Central 789',
                'ciudad': 'Rosario',
            },
        ]

        for pat_data in patients_data:
            if not User.objects.filter(username=pat_data['username']).exists():
                user = User.objects.create_user(
                    username=pat_data['username'],
                    first_name=pat_data['first_name'],
                    last_name=pat_data['last_name'],
                    email=pat_data['email'],
                    password='password123'  # In production, use proper password hashing
                )
                paciente = Paciente.objects.create(
                    user=user,
                    cedula=pat_data['cedula'],
                    genero=pat_data['genero'],
                    fecha_nacimiento=pat_data['fecha_nacimiento'],
                    tipo_sangre=pat_data['tipo_sangre'],
                    telefono=pat_data['telefono'],
                    direccion=pat_data['direccion'],
                    ciudad=pat_data['ciudad'],
                )
                self.stdout.write(f'Created patient: {paciente}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('Default password for all users: password123')
        self.stdout.write('Remember to change passwords in production!')
