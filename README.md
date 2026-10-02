# Aplicación de películas con CI

[![CI](https://github.com/cabamarcos/DevOps/actions/workflows/cicd.yml/badge.svg)](https://github.com/cabamarcos/DevOps/actions/workflows/cicd.yml)

<!-- academic-catalog:start -->
**UC3M · 4.º curso · Desarrollo y operación de sistemas software**

API de gestión de películas con operaciones de creación, consulta, edición y borrado, persistencia SQLite, validación de datos y comprobaciones automáticas en GitHub Actions.

**Tecnologías:** Python, Flask, Pydantic, SQLite, pytest, Ruff, GitHub Actions.

[Ver todos mis proyectos académicos](https://github.com/cabamarcos/academic-projects)
<!-- academic-catalog:end -->

## Qué hace

Mantiene un catálogo de películas con título, duración en minutos y categoría. Los
registros reciben un UUID. Repetir una creación con los mismos datos devuelve la
película existente; reutilizar su título con datos distintos produce un conflicto.
SQLite evita duplicados incluso con peticiones simultáneas.

La aplicación inicial se ha completado con edición y borrado, respuestas de error
JSON, inicialización automática de la base de datos y pruebas independientes. El
historial conserva las entregas de la asignatura. Autor: **Marcos Caballero Cortés**.

## Ejecutar desde cero

Requiere **Python 3.10–3.13**. Desde la raíz del repositorio:

```sh
python -m venv .venv
```

Activa el entorno con `.venv\Scripts\Activate.ps1` en PowerShell o
`source .venv/bin/activate` en Linux/macOS. Después:

```sh
python -m pip install -r requirements-dev.txt
python -m flask --app web_app seed
python -m flask --app web_app run
```

La API queda disponible en **http://127.0.0.1:5000**. La base de datos se crea en
`instance/movies.db`; `seed` importa el CSV incluido sin duplicar sus películas.
Puedes elegir otra ruta mediante la variable de entorno `DATABASE_NAME`.

En una segunda terminal, con el mismo entorno activado:

```sh
python scripts/demo.py
```

La demostración crea una película, la consulta, la edita y la borra al terminar.
La lista completa se puede consultar en `/movies` desde el navegador.

## Contrato de la API

| Método | Ruta | Resultado |
|---|---|---|
| GET | `/health/` | Estado de la aplicación |
| GET | `/movies` | Lista ordenada por título |
| POST | `/movies` | Crea una película: 201; repetición: 200 |
| GET | `/movies/{id}` | Consulta una película: 200 o 404 |
| PUT | `/movies/{id}` | Sustituye título, duración y categoría: 200 o 404 |
| DELETE | `/movies/{id}` | Elimina una película: 204 o 404 |

El cuerpo de POST y PUT es un objeto JSON como este:

```json
{"title": "Arrival", "duration": 116, "category": "Science fiction"}
```

`title` y `category` son textos no vacíos de hasta 200 y 100 caracteres. `duration`
debe ser un entero positivo; se rechazan campos adicionales. Los espacios exteriores
se eliminan. Los títulos usan la comparación `NOCASE` de SQLite, que ignora la caja
de las letras ASCII. Un conflicto de título devuelve **409**, datos inválidos **422**,
JSON mal formado **400** y un tipo de contenido distinto de JSON **415**.

Las rutas originales `/create-movie/`, `/movie-list/` y `/movie/{id}/` siguen
disponibles. PUT y DELETE también funcionan en esta última.

## Pruebas e integración

```sh
python -m pytest --cov --cov-report=term-missing
python -m ruff check .
python -m ruff format --check .
python -m bandit -q -r movies web_app.py
```

**33 pruebas · 98,9 % de cobertura** en la ejecución local de Python 3.12. Se prueban
el ciclo completo de la API, validación, conflictos, persistencia, aislamiento entre
aplicaciones, consultas parametrizadas y creaciones concurrentes. Cada prueba utiliza
una base temporal propia. La integración exige al menos un 90 % de cobertura y
ejecuta las comprobaciones en Python 3.10, 3.12 y 3.13.

En Bash, `bash scripts/all.sh` ejecuta la misma batería y se detiene en el primer
fallo. Los antiguos accesos de Black, Flake8 y Pylint delegan ahora en Ruff; Radon
sigue disponible como informe opcional mediante `scripts/check_quality_radon.sh`.

## Organización

```text
movies/          Modelos validados, comandos y persistencia
web_app.py       Factoría Flask, rutas y comando de importación
tests/           Pruebas de dominio y de la API
scripts/         Comprobaciones y demostración del servicio
.github/         Integración automática
```

Es un servicio académico para ejecución local. No incluye autenticación ni despliegue
en producción; el antiguo paso de Heroku solo imprimía un mensaje y se ha retirado.

