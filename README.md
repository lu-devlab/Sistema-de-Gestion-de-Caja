# CajaPulso

Sistema web para el control diario de caja, desarrollado con Django y PostgreSQL. Permite registrar apertura de caja, ingresos, egresos, cierre diario, historial, reportes, configuración general y notificaciones operativas.

## Descripción

CajaPulso centraliza el control de caja de una jornada en un solo lugar. Su objetivo es reemplazar registros manuales o dispersos por un flujo simple y ordenado:

- apertura de caja
- registro de ingresos y egresos
- cálculo automático del saldo esperado
- cierre diario con diferencia, faltante o sobrante
- historial por fecha
- reportes por período
- configuración del sistema
- notificaciones internas


## Instalación

1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd CajaPulso
```

2. Crear y activar entorno virtual

En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. Crear el archivo `.env` a partir de `.env.example`

En Windows:

```bash
copy .env.example .env
```

Contenido base:

```env
SECRET_KEY=tu_clave_secreta
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.postgresql
DB_NAME=cajapulso_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

5. Aplicar migraciones

```bash
python manage.py migrate
```

6. Ejecutar el servidor

```bash
python manage.py runserver
```

## Comandos útiles

Chequeo general:

```bash
python manage.py check
```

Pruebas:

```bash
python manage.py test --keepdb
```

Crear superusuario:

```bash
python manage.py createsuperuser
```

## Notas de desarrollo

- El proyecto usa `usuarios.Usuario` como modelo de usuario personalizado.
- La moneda visible se obtiene desde configuración y se refleja en todo el sistema.
- Las notificaciones se sincronizan automáticamente según apertura, cierre y diferencias de caja.
- Las migraciones sí deben versionarse en Git.

## Estado actual

El sistema se encuentra funcional para uso local o de presentación. Los flujos principales, configuración general, notificaciones y recuperación de contraseña ya están integrados.

## Mejoras futuras sugeridas

- envío real de correo para recuperación de contraseña
- endurecimiento de seguridad para producción
- más pruebas automatizadas en módulos operativos
- exportación o impresión más avanzada de reportes

## Autor

Proyecto CajaPulso
