### Bienvenidos al proyecto ARQA


### Pasos de instalación

1. Clonar el repositorio (saltear este paso si tenes el ):

```bash
git clone https://github.com/BiancaMichelle/Competencia_BRICS
cd Competencia_BRICS
// O hacemos un git pull en el caso de tener una version vieja
```
2. Instalar las dependencias 

```bash
pip3 install -r requirements.txt
npm install
```
3. Creamos las migraciones

```bash
python manage.py makemigrations
python manage.py migrate
// Ejecutar y probar si se encuentra el superusuario creado, en el caso de no ser asi, hacer:
python manage.py createsuperuser
```

4. Ejecutamos el proyecto

```bash
// Ejecutar y dejar abierto en una terminal:
npm run build-css

// En otra terminal ejecutamos el proyecto asi:
python manage.py runserver
```