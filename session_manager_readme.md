# Session Manager

Microservicio para gestión de sesiones de usuario y autenticación en el sistema Generative AI Agent Manager.

## Descripción

Este microservicio actúa como una capa de autenticación y comunicación unificada para el sistema Generative AI Agent Manager. Permite a los usuarios autenticarse y enviar mensajes que serán procesados por el orquestador de agentes, simplificando la interacción con múltiples agentes de IA.

## Características

- 🔐 Autenticación de usuarios mediante base de datos SQLite
- 🚀 Lanzamiento automático de agentes necesarios
- 📨 Comunicación simplificada con el orquestador
- 📊 Sistema de logging centralizado y configurable
- 🔒 Manejo robusto de errores y validaciones
- 🔄 Validación de datos con Pydantic
- 🔍 Verificación de credenciales

## Requisitos

- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic-settings
- SQLite3
- PyJWT
- Requests

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/session-manager.git
   cd session-manager
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Estructura del Proyecto

```
session_manager/
├── main.py               # Punto de entrada de la aplicación
├── api.py                # Endpoints REST
├── models.py             # Modelos de datos y validaciones
├── services.py           # Lógica de servicios y autenticación
├── config.py             # Configuración y sistema de logging
├── utils.py              # Utilidades auxiliares
data/
└── session_manager.db    # Base de datos SQLite para usuarios
```

### Descripción de los componentes principales

#### `main.py`

Punto de entrada de la aplicación que inicializa el servidor FastAPI. Configura el ciclo de vida de la aplicación, inicializa la base de datos y registra las rutas de la API.

#### `config.py`

Gestiona toda la configuración centralizada usando `BaseSettings` de Pydantic. Define parámetros como puerto, ruta de la base de datos, timeouts y configuración del sistema de logging.

#### `models.py`

Define los modelos de datos y esquemas utilizando Pydantic, incluyendo:
- Modelo de usuario para la base de datos
- Esquemas de solicitud y respuesta para la comunicación
- Modelos para solicitudes a los servicios externos (API principal y orquestador)

#### `api.py`

Implementa los endpoints REST del microservicio:
- Endpoint `/communicate` para iniciar el flujo completo (autenticación, lanzamiento de agentes y envío de instrucciones)
- Endpoint `/send_instruction` para enviar instrucciones al orquestador cuando los agentes ya están levantados

#### `services.py`

Contiene la lógica de negocio principal con tres clases fundamentales:
- `DatabaseService`: Gestiona la conexión e interacción con la base de datos SQLite
- `AgentRuntimeService`: Maneja la comunicación con la API principal y el orquestador
- `CommunicationService`: Integra autenticación y comunicación con los agentes

## Base de Datos

El Session Manager utiliza una base de datos SQLite para almacenar usuarios registrados:

- **Tabla `users`**: Almacena información de usuarios incluyendo:
  - `id`: Identificador único (UUID)
  - `username`: Nombre de usuario (único)
  - `password`: Contraseña almacenada con hash SHA-256
  - `created_at`: Timestamp de creación

Por defecto, la base de datos viene precargada con dos usuarios:
- **Usuario 1**: username: `user_1`, password: `1234`
- **Usuario 2**: username: `user_2`, password: `5678`

## Sistema de Logging

El proyecto implementa un sistema de logging centralizado usando el módulo de logging estándar de Python con las siguientes características:

- **Configuración centralizada**: Toda la configuración de logging se realiza en `config.py`
- **Niveles de log**: Soporte para diferentes niveles (debug, info, warning, error, critical)
- **Logs en consola**: Salida formateada para facilitar la lectura
- **Contexto incluido**: Inclusión automática de información como timestamps, niveles y código fuente

### Configuración de Logging

El nivel de log puede configurarse mediante la variable de entorno `LOG_LEVEL`. Los valores posibles son:

- `DEBUG`: Información detallada para desarrollo
- `INFO`: Información operativa general (predeterminado)
- `WARNING`: Situaciones problemáticas pero no críticas
- `ERROR`: Errores que impiden funcionalidad
- `CRITICAL`: Errores críticos que requieren atención inmediata

```bash
# Ejemplo: establecer nivel de log a DEBUG
export LOG_LEVEL=DEBUG
```

## Manejo de Errores y Validaciones

El sistema implementa un manejo robusto de errores y validaciones:

- **Validación de credenciales**: Verificación segura de usuarios y contraseñas
- **Logging automático**: Registro detallado de errores para facilitar diagnóstico
- **Validación con Pydantic**: Validaciones automáticas de esquemas de entrada
- **Mensajes claros**: Respuestas de error informativas para el cliente

## Configuración

La configuración del sistema se realiza principalmente a través del archivo `config.py`. Los parámetros más importantes incluyen:

- `APP_NAME`: Nombre de la aplicación
- `DEBUG`: Modo de depuración
- `PORT`: Puerto del servicio (8005 por defecto)
- `RUNTIME_API_URL`: URL de la API principal del sistema
- `DB_PATH`: Ruta a la base de datos SQLite
- `DB_CONN_TIMEOUT`: Timeout para conexiones a la base de datos

## Flujos de Comunicación

El Session Manager implementa dos flujos principales para procesar mensajes:

### 1. Flujo Completo (Endpoint `/communicate`)

1. El usuario envía sus credenciales y un mensaje
2. El sistema verifica las credenciales contra la base de datos SQLite
3. Si la autenticación es exitosa, crea un objeto de recursos con las credenciales
4. Envía una solicitud a la API principal para lanzar los agentes necesarios (vfs, gpt4, orchestrator)
5. Envía el mensaje original al orquestador para su procesamiento
6. Devuelve una respuesta unificada con el resultado

### 2. Solo Instrucción (Endpoint `/send_instruction`)

1. El usuario envía solo un mensaje (asumiendo que los agentes ya están levantados)
2. El sistema envía el mensaje directamente al orquestador para su procesamiento
3. Devuelve la respuesta del orquestador

## Uso

### Iniciar el Servidor

```bash
python -m session_manager.main
```

El servidor estará disponible en http://localhost:8005

### Ejemplos de Uso con curl

#### Flujo completo (autenticación, lanzamiento de agentes y envío de instrucciones):

```bash
curl -X POST http://localhost:8005/communicate \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Necesito información sobre inteligencia artificial",
       "credentials": {
         "username": "user_1",
         "password": "1234"
       }
     }'
```

#### Solo envío de instrucciones (cuando los agentes ya están levantados):

```bash
curl -X POST http://localhost:8005/send_instruction \
     -H "Content-Type: application/json" \
     -d '{
       "message": "¿Qué tipos de algoritmos de machine learning existen?"
     }'
```

#### Verificar el estado del servicio:

```bash
curl http://localhost:8005/
```

## API Reference

### Session Manager (Puerto 8005)

| Endpoint           | Método | Descripción                                    | Tipo de Solicitud       | Tipo de Respuesta     |
| ------------------ | ------ | ---------------------------------------------- | ----------------------- | --------------------- |
| `/`                | GET    | Información básica del microservicio           | -                       | JSON con estado       |
| `/communicate`     | POST   | Flujo completo (autenticación y comunicación)  | `CommunicateRequest`    | `CommunicateResponse` |
| `/send_instruction`| POST   | Solo envío de instrucción al orquestador       | `SendInstructionRequest`| `CommunicateResponse` |

#### Modelo de Solicitud `/communicate`

```json
{
  "message": "Texto del mensaje a procesar",
  "credentials": {
    "username": "nombre_de_usuario",
    "password": "contraseña"
  }
}
```

#### Modelo de Solicitud `/send_instruction`

```json
{
  "message": "Texto del mensaje a procesar"
}
```

#### Modelo de Respuesta (ambos endpoints)

```json
{
  "success": true,
  "message": "Comunicación procesada correctamente",
  "data": {
    "launched_agents": [...],  // Solo en /communicate
    "instruction": {
      "original": "Texto original",
      "optimized": "Texto optimizado para LLM"
    }
  }
}
```