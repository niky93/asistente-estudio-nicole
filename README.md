# Jarvis — Asistente de estudio de Nicole

Jarvis es un bot de Telegram que ayuda a estudiar distintas materias:
explica conceptos, propone ejercicios y organiza sesiones de estudio.
Personalicé la plantilla del curso con un planificador, búsqueda web
con fuentes, memoria persistente por chat y recordatorios automáticos.

## Acceder al bot

[Abre Jarvis en Telegram](https://t.me/sistente_nicole_curso_bot)

El acceso está limitado a los usuarios autorizados.

## Ejemplos para probar

### Organizar una sesión y buscar material

«Tengo una hora para estudiar historia de China. Organiza una sesión
con descansos y busca páginas educativas para repasar».

### Practicar con retroalimentación

«Dame un ejercicio sencillo de funciones de Python.
Espera mi respuesta y luego explícame qué puedo corregir».

Después, envía tu solución para que Jarvis la revise.

### Retomar una conversación

Tras estudiar un tema, escribe:

«Retomemos lo que estábamos estudiando y hazme una pregunta de repaso».

El historial se conserva por chat, incluso después de reiniciar Render.
Las materias comparten una conversación; no son sesiones independientes.

## Recordatorios

Los recordatorios se crean mediante comandos y utilizan la hora de Bolivia
(UTC−4), en formato de 24 horas.

| Comando | Función |
|---|---|
| `/start` | Iniciar y comprobar el acceso. |
| `/recordar AAAA-MM-DD HH:MM texto` | Crear un recordatorio para una fecha futura. |
| `/recordatorios` | Consultar hasta 20 recordatorios pendientes. |
| `/cancelar NUMERO` | Cancelar un recordatorio pendiente por su número. |

Para crear uno, reemplaza la fecha, hora y texto:

`/recordar AAAA-MM-DD HH:MM Repasar para el examen`

Jarvis devuelve el número del recordatorio. Puedes usarlo para cancelarlo.

Una petición como «recuérdame mañana» no programa un aviso automáticamente:
debes usar `/recordar`.

## Tecnologías y funcionamiento

- Python y Pydantic AI: agente y herramientas.
- Gemini: generación de respuestas.
- Tavily: búsqueda en internet.
- PostgreSQL en Neon: historial y recordatorios.
- Render: alojamiento del bot y del servicio de envíos.
- cron-job.org: revisión de recordatorios pendientes cada minuto.

Se conservan las herramientas de la plantilla para APIs públicas,
gastos y consultas a documentos. Los gastos y documentos de ejemplo
son ficticios y no son apuntes de estudio.

## Límites

- Las respuestas pueden contener errores; verifica la información
  importante y las fuentes.
- Render Free puede suspender el servicio por inactividad:
  la primera respuesta puede tardar alrededor de un minuto.
- Los recordatorios pueden retrasarse por el intervalo de revisión
  o la disponibilidad de los servicios.
- Cada llamada al servicio de envíos procesa hasta cinco pendientes.
- El funcionamiento depende de las cuotas de los servicios utilizados.

## Créditos

Proyecto basado en la plantilla del curso «Más allá de los chatbots»,
de Alex Ojeda Copa:

https://github.com/alex-roc/mi-asistente

Se conserva la licencia original del repositorio.