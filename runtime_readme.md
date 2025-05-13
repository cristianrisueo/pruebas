# Runtime Service

Sistema de gestión para levantar agentes de inteligencia generativa como microservicios independientes.

## Descripción

Este proyecto permite lanzar, monitorizar y gestionar múltiples agentes de IA generativa como servicios web independientes. Cada agente se ejecuta en su propio puerto y puede ser controlado individualmente a través de una API centralizada.

## Características

- 🚀 Levantamiento dinámico de agentes como microservicios
- 📋 Agentes con puertos fijos predeterminados (vfs: 8001, kendra: 8002, gpt4: 8003, orchestrator: 8004)
- 🔍 Monitorización de agentes en ejecución
- 🛑 Apagado controlado de servicios
- 🔄 API RESTful para gestión completa
- 🔁 Reutilización inteligente de puertos
- 📊 Sistema de logging centralizado y configurable
- 🔒 Manejo robusto de errores y validaciones
- 🔄 Orquestador centralizado para la comunicación entre agentes

## Requisitos

- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic-settings
- Psutil
- Requests

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/generative-ai-agent-manager.git
   cd generative-ai-agent-manager
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Instalar pydantic-settings (para Pydantic v2):
   ```bash
   pip install pydantic-settings
   ```

## Estructura del Proyecto

```
app/
├── main.py               # Punto de entrada de la aplicación
├── api.py                # Endpoints REST
├── models.py             # Modelos de datos y excepciones
├── services.py           # Lógica de servicios y gestión de agentes
├── config.py             # Configuración y sistema de logging
├── utils.py              # Utilidades para gestión de recursos
agents/
├── vfs/                  # Agente de sistema de archivos virtual
│   └── asgi.py           # Implementación del servicio (puerto 8001)
├── kendra/               # Agente de búsqueda y recuperación
│   └── asgi.py           # Implementación del servicio (puerto 8002)
├── gpt4/                 # Agente de generación de texto
│   └── asgi.py           # Implementación del servicio (puerto 8003)
└── orchestrator/         # Agente orquestador para la comunicación
    └── asgi.py           # Implementación del servicio (puerto 8004)
logs/                     # Logs centralizados del sistema
tests/                    # Tests automatizados
```

### Descripción de los componentes principales

#### `main.py`

Punto de entrada de la aplicación que inicializa el servidor FastAPI principal. Configura el ciclo de vida de la aplicación, registra las rutas de la API, y gestiona los eventos de inicio y cierre. Implementa un manejador asíncrono (`lifespan`) que garantiza la correcta inicialización de recursos y la limpieza al finalizar.

#### `config.py`

Gestiona toda la configuración centralizada usando `BaseSettings` de Pydantic. Define parámetros como puertos, rutas de archivos, timeouts y nombres de aplicación. Configura también el sistema de logging centralizado usando el módulo de logging estándar de Python, estableciendo formatos, niveles y destinos para los logs.

#### `models.py`

Define los modelos de datos y esquemas utilizando Pydantic, incluyendo:

- Excepciones personalizadas para el manejo de errores
- Payloads para peticiones API (ManifestPayload)
- Respuestas API estandarizadas
- Enumeradores para estados de agentes
- Modelos para información de agentes activos
- Funciones para convertir excepciones en respuestas HTTP

#### `api.py`

Implementa los endpoints REST para interactuar con los agentes. Las rutas incluyen:

- Lanzamiento de agentes (`/launch_agents`)
- Listado de agentes en ejecución (`/list_agents`)
- Detención de agentes (`/stop_agent`)

Gestiona la validación de entradas, transformación de excepciones en respuestas HTTP y el enrutamiento general de la API.

#### `services.py`

Contiene la lógica de negocio principal con dos clases fundamentales:

- `AgentService`: Gestiona operaciones de bajo nivel para iniciar y detener procesos de agentes individuales
- `AgentManager`: Orquesta múltiples agentes, manteniendo registro de su estado, asignando puertos y coordinando operaciones

#### `utils.py`

Proporciona funciones auxiliares para:

- Manejo de archivos y directorios
- Generación de comandos para iniciar agentes
- Gestión de puertos fijos para agentes
- Almacenamiento y limpieza de recursos de agentes

## Sistema de Logging

El proyecto implementa un sistema de logging centralizado usando el módulo de logging estándar de Python con las siguientes características:

- **Configuración centralizada**: Toda la configuración de logging se realiza en `config.py`
- **Niveles de log**: Soporte para diferentes niveles (debug, info, warning, error, critical)
- **Logs en consola**: Salida formateada para facilitar la lectura
- **Logs en archivos**: Almacenamiento automático en archivos con rotación
- **Rotación automática**: Gestión inteligente del tamaño de los archivos de log
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

- **Excepciones tipadas**: Uso de excepciones específicas para cada tipo de error
- **Conversión de excepciones**: Transformación automática a respuestas HTTP adecuadas
- **Logging automático**: Registro detallado de errores para facilitar diagnóstico
- **Validación con Pydantic**: Validaciones automáticas de esquemas de entrada
- **Mensajes claros**: Respuestas de error informativas para el cliente

## Configuración

La configuración del sistema se realiza principalmente a través del archivo `config.py`. Los parámetros más importantes incluyen:

- `APP_NAME`: Nombre de la aplicación
- `DEBUG`: Modo de depuración
- `PORT`: Puerto principal (8000 por defecto)
- `MIN_AGENT_PORT` y `MAX_AGENT_PORT`: Rango de puertos para agentes (8001-12001)
- `AGENTS_DIR`: Directorio donde se encuentran los agentes
- `LOG_DIR`: Directorio para almacenar logs
- `AGENT_STARTUP_TIMEOUT` y `AGENT_SHUTDOWN_TIMEOUT`: Tiempos de espera para operaciones

## Agente Orquestador

El sistema incluye un agente orquestador que facilita la comunicación entre los diferentes microservicios:

- **Puerto fijo**: 8004
- **Orden de inicialización**: Siempre último en la secuencia de lanzamiento
- **Funcionalidad**:
  - Descubre automáticamente los agentes disponibles
  - Mantiene registro de las URLs base de todos los agentes
  - Proporciona endpoints para consultar los agentes activos
  - Permite redescubrir agentes bajo demanda
  - Optimiza instrucciones en lenguaje natural para LLMs

### Endpoints del Orquestador

- `/`: Información básica del agente
- `/status`: Estado detallado del agente
- `/agents`: Lista de agentes disponibles con sus URLs
- `/discover`: Fuerza un redescubrimiento de agentes
- `/shutdown`: Apagado controlado
- `/instructions`: Procesa instrucciones en lenguaje natural y las optimiza para LLMs

## Tests Automatizados

El proyecto cuenta con una amplia suite de tests automatizados:

- **Cobertura de código**: >80% del código total cubierto por tests
- **Tests unitarios**: Verificación de componentes individuales
- **Tests de integración**: Verificación de interacciones entre componentes
- **Tests de API**: Verificación de endpoints y respuestas HTTP

### Ejecutar Tests

Para ejecutar la suite de tests:

```bash
python -m pytest
```

Para ejecutar con reporte de cobertura:

```bash
python -m pytest --cov=src
```

## Uso

### Iniciar el Servidor

```bash
python -m app.main
```

El servidor principal estará disponible en http://localhost:8000

### Ejemplos de Uso con curl

Lanzar agentes:

```bash
curl -X POST http://localhost:8000/api/launch_agents \
     -H "Content-Type: application/json" \
     -d '{"agents": ["vfs", "kendra"], "resources": {}}'
```

Lanzar agentes con recursos:

```bash
curl -X POST http://localhost:8000/api/launch_agents \
     -H "Content-Type: application/json" \
     -d '{"agents": ["vfs", "kendra"], "resources": {"sharepoint": {"url": "https://example.com", "user": "user", "password": "pass"}}}'
```

Lanzar el orquestador y otros agentes:

```bash
curl -X POST http://localhost:8000/api/launch_agents \
     -H "Content-Type: application/json" \
     -d '{"agents": ["vfs", "gpt4", "orchestrator"], "resources": {}}'
```

Listar agentes en ejecución:

```bash
curl http://localhost:8000/api/list_agents
```

Consultar agentes disponibles al orquestador:

```bash
curl http://localhost:8004/agents
```

Forzar redescubrimiento de agentes:

```bash
curl http://localhost:8004/discover
```

Enviar instrucciones al orquestador:

```bash
curl -X POST http://localhost:8004/instructions \
     -H "Content-Type: application/json" \
     -d '{"text": "Busca información sobre inteligencia artificial"}'
```

Detener un agente por nombre:

```bash
curl -X POST http://localhost:8000/api/stop_agent?agent_name=vfs
```

## API Reference

### Servidor Principal (Puerto 8000)

| Endpoint             | Método | Descripción                                       | Tipo de Retorno                  |
| -------------------- | ------ | ------------------------------------------------- | -------------------------------- |
| `/api/launch_agents` | POST   | Lanza uno o más agentes                           | `Dict[str, list[AgentResponse]]` |
| `/api/list_agents`   | GET    | Lista agentes en ejecución con filtros opcionales | `Dict[str, list[AgentResponse]]` |
| `/api/stop_agent`    | POST   | Detiene uno o más agentes                         | `Dict[str, list[AgentResponse]]` |

### Servicios de Agente (Puertos asignados)

| Endpoint    | Método | Descripción                   |
| ----------- | ------ | ----------------------------- |
| `/`         | GET    | Información básica del agente |
| `/status`   | GET    | Estado detallado del agente   |
| `/shutdown` | GET    | Inicia apagado controlado     |

### Orquestador (Puerto 8004)

| Endpoint        | Método | Descripción                                          |
| --------------- | ------ | ---------------------------------------------------- |
| `/`             | GET    | Información básica del orquestador                   |
| `/status`       | GET    | Estado detallado del orquestador                     |
| `/agents`       | GET    | Lista de agentes disponibles con URLs                |
| `/discover`     | GET    | Fuerza redescubrimiento de agentes                   |
| `/instructions` | POST   | Optimiza instrucciones en lenguaje natural para LLMs |
| `/shutdown`     | GET    | Inicia apagado controlado                            |

## Características Adicionales

### Agentes con Puertos Fijos

El sistema utiliza puertos fijos para ciertos agentes:

- `vfs`: Puerto 8001
- `kendra`: Puerto 8002
- `gpt4`: Puerto 8003
- `orchestrator`: Puerto 8004

Otros agentes recibirán puertos dinámicos dentro del rango configurado.

### Gestión Eficiente de Puertos

- Reutilización inteligente de puertos: cuando un agente se detiene, su puerto queda disponible para futuros agentes
- Los puertos se asignan de manera secuencial, priorizando los de menor número
- El sistema mantiene un registro de puertos liberados para su reutilización

### Implementación de Agentes

Cada agente es un servicio web FastAPI independiente que implementa:

- Endpoint raíz (`/`) para información básica
- Endpoint de estado (`/status`) para monitoreo
- Endpoint de apagado (`/shutdown`) para cierre controlado
- Funcionalidad específica según el tipo de agente

### Recursos para Agentes

El sistema permite asignar recursos específicos a cada agente mediante archivos JSON:

- Se almacenan en la carpeta del agente
- Incluyen información como ID, nombre, y otros recursos necesarios
- Se limpian automáticamente al detener el agente
