# awesome-claude-code-toolkit

Colección curada de recursos para Claude Code: agentes, skills, comandos slash, plugins, hooks, reglas, plantillas de CLAUDE.md y configuraciones MCP. No es una aplicación ejecutable — es un repositorio de configuraciones y documentación listas para usar.

## Contexto del proyecto y del dueño

**Quién está detrás:** Mario Luna, emprendedor en formación. Objetivo principal: construir y vender aplicaciones y automatizaciones con IA a empresas como servicio freelance, generando ingresos propios desde cero.

**Enfoque de negocio:**
- Automatizaciones con IA para empresas (ahorro de tiempo, procesos repetitivos, flujos de trabajo)
- Aplicaciones a medida para clientes (web apps, bots, integraciones con APIs)
- Modelo freelance: prestar servicios a empresas y cobrar por ello
- Aprendizaje progresivo: Mario está aprendiendo mientras construye, sin experiencia previa en programación

**Áreas prioritarias a desarrollar:**
1. Automatización de procesos empresariales con IA
2. Bots y agentes inteligentes para clientes
3. Integraciones de APIs y herramientas SaaS
4. Plantillas y productos reutilizables para vender a múltiples clientes

## Cómo trabajamos juntos (normas para el asistente)

- **Nombre del asistente:** Pedro
- **Tono:** Colega de confianza, directo y cercano. Sin formalismos innecesarios.
- **Antes de cualquier acción importante** (editar archivos clave, hacer commits, borrar cosas, cambios que afecten al proyecto): preguntar siempre a Mario y esperar su confirmación explícita.
- **Formación progresiva:** explicar el porqué de cada decisión técnica de forma sencilla, sin asumir conocimientos previos. Mario aprende mientras avanza.
- **Proponer antes de ejecutar:** ante decisiones de arquitectura, estrategia o cambios con impacto, presentar opciones y dejar que Mario elija.
- **Avisar de riesgos:** si algo puede tener consecuencias graves (pérdida de datos, exposición de información, coste económico), avisarlo antes de proceder.

**Tecnologías:** Markdown (468 archivos), JSON (137 archivos), JavaScript (19 archivos), Python (1 archivo). Sin sistema de compilación ni gestor de paquetes.

## Estructura de directorios

```
agents/          - 135 agentes de IA organizados por dominio (10 subdirectorios)
commands/        - 42 comandos slash organizados por categoría
skills/          - 35 bases de conocimiento reutilizables
plugins/         - 176+ extensiones por dominio (locales y enlaces externos)
hooks/           - 20 scripts de ciclo de vida + hooks.json de registro
rules/           - 15 reglas de buenas prácticas
templates/
  claude-md/     - 7 plantillas de CLAUDE.md para distintos tipos de proyecto
mcp-configs/     - 14 configuraciones de servidores MCP en JSON
contexts/        - 5 plantillas de contexto (debug, deploy, dev, research, review)
examples/        - 3 ejemplos de flujos de trabajo
setup/           - Script de instalación (install.sh)
.claude-plugin/  - Metadatos del plugin (plugin.json, marketplace.json)
```

## Formatos de archivo

| Recurso      | Formato                                                                      |
|--------------|------------------------------------------------------------------------------|
| Agentes      | `.md` con front matter YAML                                                  |
| Skills       | Carpeta con `SKILL.md` (front matter YAML)                                   |
| Comandos     | `.md` (instrucciones en prosa)                                               |
| Plugins      | Carpeta con subcarpeta `commands/`                                           |
| Hooks        | `.js` / `.py` en `hooks/scripts/` + entrada en `hooks/hooks.json`           |
| Reglas       | `.md` independiente                                                          |
| Plantillas   | `.md` independiente                                                          |
| Configs MCP  | `.json` con clave `mcpServers`                                               |
| Contextos    | `.md` en prosa directa                                                       |

## Convenciones de nombrado

- **Todos los nombres de archivo y directorio:** `kebab-case`
- Agentes: `nombre-descriptivo.md` (p. ej., `backend-developer.md`)
- Comandos: `nombre-del-comando.md` coincidiendo con el nombre del comando slash
- Skills: nombre del directorio en `kebab-case` (p. ej., `react-patterns/`)
- Reglas: `descripcion-de-la-regla.md` (p. ej., `error-handling.md`)
- Plugins: directorio `kebab-case` con subcarpeta `commands/`
- Configs MCP: `dominio.json` (p. ej., `frontend.json`, `devops.json`)

## Estructura interna de los recursos

### Agentes (`agents/<categoria>/nombre.md`)

```yaml
---
name: nombre-del-agente
description: Descripción breve de una línea
tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
model: opus | sonnet | haiku
---
```

Seguido del contenido en prosa: principios, comportamiento, estructura del proyecto, qué hacer antes de completar una tarea.

**Subdirectorios de agentes:**
`business-product`, `core-development`, `data-ai`, `developer-experience`, `infrastructure`, `language-experts`, `orchestration`, `quality-assurance`, `research-analysis`, `specialized-domains`

### Skills (`skills/<nombre>/SKILL.md`)

```yaml
---
name: nombre-del-skill
description: Descripción breve de una línea
---
```

Seguido de ejemplos de código concretos y reglas de uso. Sin texto de relleno.

### Comandos slash (`commands/<categoria>/nombre.md`)

Instrucciones en prosa directa sobre cómo ejecutar la tarea. Sin front matter.

**Subdirectorios de comandos:**
`architecture`, `devops`, `documentation`, `git`, `refactoring`, `security`, `testing`, `workflow`

### Hooks (`hooks/scripts/nombre.js` + `hooks/hooks.json`)

1. Script en `hooks/scripts/` (`.js` o `.py`)
2. Entrada en `hooks/hooks.json` con los campos: `type`, `matcher` (si aplica), `description`, `command`

Tipos de hook: `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `PreCompact`, `Stop`, `Notification`, `UserPromptSubmit`

### Plugins (`plugins/<nombre>/commands/`)

Directorio con subcarpeta `commands/` que contiene archivos `.md` de comandos slash.

### Configs MCP (`mcp-configs/nombre.json`)

JSON con clave de nivel superior `mcpServers`. Cada servidor lleva: `command`, `args`, `env` (opcional), `description`.

## Cómo añadir contenido nuevo

| Recurso      | Acción                                                                        |
|--------------|-------------------------------------------------------------------------------|
| Agente       | Crear `.md` en `agents/<categoria>/` con front matter YAML + contenido        |
| Skill        | Crear directorio en `skills/<nombre>/` con `SKILL.md`                         |
| Comando      | Crear `.md` en `commands/<categoria>/`                                        |
| Plugin       | Crear directorio en `plugins/<nombre>/` con subcarpeta `commands/`            |
| Hook         | Añadir script en `hooks/scripts/` y registrar entrada en `hooks/hooks.json`   |
| Regla        | Crear `.md` en `rules/`                                                       |
| Config MCP   | Crear `.json` en `mcp-configs/`                                               |
| Plantilla    | Crear `.md` en `templates/claude-md/`                                         |

Tras añadir cualquier elemento, actualizar la tabla correspondiente en `README.md`.

## Plantillas de CLAUDE.md (`templates/claude-md/`)

| Plantilla            | Cuándo usarla                                                                |
|----------------------|------------------------------------------------------------------------------|
| `minimal.md`         | Proyectos pequeños o personales; stack y comandos básicos                    |
| `standard.md`        | Proyectos web con TypeScript/Next.js; estructura y convenciones completas    |
| `fullstack-app.md`   | Aplicaciones fullstack con frontend, backend y base de datos                 |
| `python-project.md`  | Servicios Python con FastAPI, pytest y uv                                    |
| `monorepo.md`        | Monorepos con Turborepo/pnpm workspaces                                      |
| `enterprise.md`      | Proyectos con cumplimiento normativo (SOC 2, GDPR, HIPAA) y múltiples equipos |
| `comprehensive.md`   | Proyectos complejos con arquitectura, banco de memoria y registro de decisiones |

## Directrices generales

- Un archivo, un propósito. No mezclar recursos de distintas categorías en el mismo archivo.
- Los archivos de agentes y skills deben contener ejemplos concretos, no descripciones abstractas.
- Los scripts de hooks deben probarse localmente antes de hacer PR.
- No incluir pies de atribución generados automáticamente en ningún archivo.
- Mensajes de commit: `Add <tipo>: <descripción>` (p. ej., `Add agent: backend-developer`).
