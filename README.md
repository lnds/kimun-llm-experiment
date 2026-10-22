# ¿Le importa a un agente la salud del código?

Datos y scripts del post *¿Tu código es amistoso para un LLM?*, del blog de [kimun.tools](https://kimun.tools/blog/) <!-- TODO: enlace al post -->.

Dos partes:

1. **El mapa.** `km map --color-by llm` de [kimun](https://kimun.tools) sobre nueve proyectos conocidos. Cada archivo se pinta según su nota de `km score`: verde desde 95 ("amistoso para un LLM"), gris entre 70 y 95, rojo bajo 70. El umbral de 95 es la contraparte, en la escala de kimun, del 9,5 de Code Health que CodeScene propone para trabajar con agentes. No es una equivalencia calibrada.
2. **El experimento.** 25 bugs de un token inyectados en click, flask y black: 13 en archivos verdes (nota ≥ 85) y 12 en rojos (< 65). Un agente por bug intenta arreglarlo, y luego se vuelve a correr la suite completa.

## Resultados

| | Verdes (n=13) | Rojos (n=12) |
|---|---|---|
| Diagnóstico correcto | 13/13 | 12/12 |
| La suite pasa | 11/13 | 12/12 |
| Herramientas usadas (mediana) | 6 | 7 |
| Tokens de entrada acumulados (mediana) | 355 mil | 389 mil |
| Código que el agente sumó al contexto (mediana) | 10 mil tokens | 10 mil tokens |
| Tamaño del archivo (mediana) | 385 líneas | 1.145 líneas |

La correlación de Spearman entre la nota del archivo y las herramientas que usó el agente es −0,26: con 25 casos, ruido. Medida en tokens de entrada acumulados, la correlación es −0,18. Cada sesión parte con unos 52 mil tokens fijos (instrucciones y herramientas), que se reenvían en cada turno; lo que el agente suma al contexto leyendo código es `context_growth` en `data/results.json`. Los tokens de salida que registran los transcripts no son confiables y no se usan. El único caso caro fue `black/linegen.py` (nota 32,3): 36 herramientas, 5,5 minutos y 2,8 millones de tokens de entrada, contra 4 a 12 herramientas y una mediana de 370 mil tokens en el resto. Los dos casos en que la suite no pasa (t08, t13) son archivos verdes: el agente encontró el bug, aplicó el arreglo con un `sed -i` de sintaxis GNU que falla en macOS y reportó éxito sin ver el resultado.

```bash
python3 scripts/summary.py    # la tabla por intento y los agregados, desde data/results.json
```

## Contenido

| Ruta | Qué es |
|---|---|
| `repos.txt` | Los repos medidos, con el commit exacto |
| `prompt.md` | El prompt de cada agente, idéntico para todos |
| `capturas/` | Los mapas de cada repo |
| `data/maps/` | `km score` de cada repo y el resumen de su mapa (líneas en cada franja, directorios destacados) |
| `data/mutations/` | Las mutaciones: archivo, línea, columna, token original y mutado, tests que fallan |
| `data/trials.json` | Las 25 copias: qué mutación lleva cada una y la nota de su archivo |
| `data/results.json` | Cada intento: herramientas, tokens de entrada acumulados, contexto inicial y su crecimiento, segundos, si la suite pasa, si el arreglo deshace la mutación exacta y el reporte final del agente |

## Reproducir

Requiere `git`, `python3`, [`uv`](https://docs.astral.sh/uv/), [`km`](https://kimun.tools) 0.44 y, para el experimento, [Claude Code](https://claude.com/claude-code).

```bash
scripts/fetch.sh            # clona los repos en work/repos y crea los entornos de click, flask y black
scripts/maps.sh             # mapas y notas en work/maps
scripts/find_mutations.sh   # opcional: busca mutaciones nuevas en work/mutations
python3 scripts/setup_trials.py              # copias aisladas en work/trials, con las mutaciones de data/mutations
scripts/run_trials.sh                        # un agente por copia; sesiones en work/runs
python3 scripts/analyze.py                   # work/results.json
python3 scripts/summary.py work/results.json
```

`find_mutations.sh` prueba, en cada archivo, mutaciones de un token en orden aleatorio (semilla 7) y se queda con la primera que hace fallar entre 1 y 15 tests: `==`/`!=`, `<`/`>=`, `is`/`is not`, `in`/`not in`, `and`/`or`, quitar un `not`, `+`/`-`, `True`/`False` en un `return`, un entero pequeño más uno. Para usar las mutaciones nuevas, pasa su directorio a `setup_trials.py work/mutations`.

Cada copia de `setup_trials.py` lleva un historial de git nuevo, para que `git diff` no delate la mutación, y su propio entorno, porque uno editable compartido importaría el código sin mutar.

`run_trials.sh` corre los agentes sin pedir permisos (`--dangerously-skip-permissions`). Hazlo en una máquina o un contenedor desechable. `MODEL` y `JOBS` eligen el modelo (por omisión `sonnet`) y cuántos corren a la vez (4).

## Cómo se corrió

- **Con quién:** el experimento se diseñó, se corrió y se analizó con Claude (Opus) en Claude Code. Claude escribió los scripts de este repositorio.
- **Modelo de los agentes:** Claude Sonnet, como subagentes de Claude Code (no con `claude -p`), con 20 agentes a la vez. `analyze.py` lee los dos formatos de sesión.
- **Fecha:** 22 de octubre de 2026, en macOS con Python 3.13.
- **Mapas:** kimun 0.44. En black se excluyó `profiling/` (datos de prueba) y en redis `deps/` (código de terceros).

## Límites

- Son 25 casos, con una corrida por bug y un solo modelo.
- Un bug de un token que un test señala es la tarea más fácil posible: el agente lee el traceback, hace grep y lee unas 40 líneas, sin importar el tamaño del archivo. Features, refactors y bugs sin un test que los señale pueden dar otro resultado.
- El tiempo no sirve para comparar: la suite de black es la más lenta, la mayoría de los archivos rojos son de black y los agentes corrían en paralelo.

## Licencia

MIT. Los repos medidos conservan sus propias licencias y no se incluyen aquí.
