# Entrega de Objetos Perdidos

Este proyecto es una aplicación web para la **gestión y registro de objetos perdidos entregados**, construida con **Django**.  
El objetivo es tener una plataforma escalable y fácil de usar para centralizar la información de los objetos reclamados.

## Requisitos previos
- Python 3.x
- Django
- Git (opcional, si deseas clonar el repositorio directamente)

## Instalación y ejecución

1. Clonar el repositorio.
   ```bash
   git clone https://github.com/tu-usuario/Entrega-de-objetos-perdidos-.git
   cd Entrega-de-objetos-perdidos-
2. Crear y activar el entorno virtual.
   ```bash
   python -m venv venv
   venv\Scripts\activate   # En Windows
   source venv/bin/activate  # En Linux/Mac
3. Instalar dependencias.
   ```bash
   pip install -r requirements.txt
4. Cambiar a la ruta del proyecto Django.
   ```bash
   cd objetos_reclamados
   cd "C:\Users\kevin\OneDrive\Escritorio\Entrega-de-objetos-perdidos-\objetos_reclamados"
5. Ejecutar el servidor de desarrollo.
   ```bash
   python manage.py runserver
6. Abrir en el navegador.
   http://127.0.0.1:8000/admin

## Estructura del proyecto
```txt
Entrega-de-objetos-perdidos-/
│── objetos_reclamados/   # Aplicación principal de Django
│── venv/                 # Entorno virtual (no se sube al repo)
│── manage.py             # Archivo principal de Django
│── requirements.txt      # Dependencias del proyecto
│── README.md             # Documentación
```


## Notas
Asegúrate de crear un superusuario para acceder al panel de administración:
  ```bash
  python manage.py createsuperuser
  ```

## Autor
Kevin Ramos (@kevinramos2)

