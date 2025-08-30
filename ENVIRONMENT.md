# Guía de Variables de Entorno

Este documento explica todas las variables de entorno disponibles para configurar el proyecto Sistema Médico Blockchain.

## Variables Obligatorias

### Django Configuration
```env
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-aqui
DEBUG=False  # Siempre False en producción
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

### Polygon Blockchain (Obligatorio para funcionalidad blockchain)
```env
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/TU_PROJECT_ID
POLYGON_CHAIN_ID=137  # 137 para mainnet, 80001 para testnet
```

## Variables Opcionales

### Filecoin Storage (Opcional)
```env
FILECOIN_API_URL=https://api.filecoin.io
FILECOIN_API_KEY=tu_api_key_de_filecoin
```

### Base de Datos
```env
# SQLite (por defecto)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (recomendado para producción)
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_db
```

### Email Configuration
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
```

### Configuración de Seguridad (Importante para producción)
```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

## Cómo Obtener las API Keys

### Polygon/Infura
1. Ve a https://infura.io/
2. Crea una cuenta gratuita
3. Crea un nuevo proyecto
4. Selecciona "Polygon Mainnet" como red
5. Copia el endpoint URL

### Filecoin
1. Ve a https://filecoin.io/ o servicios como Web3.Storage
2. Regístrate para obtener una API key
3. Configura la variable FILECOIN_API_KEY

## Configuración por Entorno

### Desarrollo
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
POLYGON_RPC_URL=https://polygon-mumbai.infura.io/v3/TU_PROJECT_ID
POLYGON_CHAIN_ID=80001
```

### Producción
```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/TU_PROJECT_ID
POLYGON_CHAIN_ID=137
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Verificación de Configuración

Para verificar que las variables de entorno están cargadas correctamente:

```python
# En una shell de Django
python manage.py shell
>>> import os
>>> print(os.getenv('POLYGON_RPC_URL'))
>>> print(os.getenv('DEBUG'))
```

O visita la página de estado de blockchain en `/users/blockchain-status/` para verificar la conexión con Polygon.
