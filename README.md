# ¿Le importa a un agente la salud del código?

Datos y scripts de dos artículos del blog de Kimün: [*¿Tu código es amistoso para un LLM?*](https://kimun.tools/blog/is-your-code-llm-friendly/) ([en inglés](https://kimun.tools/en/blog/is-your-code-llm-friendly/)) y [*Cuando ninguna prueba avisa*](https://kimun.tools/blog/when-no-test-helps/) ([en inglés](https://kimun.tools/en/blog/when-no-test-helps/)).

Cuatro partes:

1. **El mapa.** `km map --color-by llm` de [kimun](https://kimun.tools) sobre nueve proyectos conocidos. Cada archivo se pinta según su nota de `km score`: azul desde 95 ("amistoso para un LLM"), gris entre 70 y 95, naranja bajo 70. El umbral de 95 es la contraparte, en la escala de kimun, del 9,5 de Code Health que CodeScene propone para trabajar con agentes. No es una equivalencia calibrada.
2. **Primera ronda.** 25 bugs de un token inyectados en click, flask y black: 13 en archivos azules (nota ≥ 85) y 12 en naranjas (< 65). Un agente por bug intenta arreglarlo, y luego se vuelve a correr la suite completa.
3. **Segunda ronda.** 22 bugs en [sc-cli](https://github.com/lnds/sc-cli) (Rust, nota F- 40,0), un proyecto que casi seguro no está en los datos de entrenamiento del modelo. Las mutaciones las generó [kalku](https://kalku.tools).
4. **Tercera ronda, sin pruebas.** 20 mutantes de sc-cli que la suite no detecta. El agente recibe solo un reporte del síntoma, escrito como lo haría un usuario; una prueba escondida, que el agente nunca ve, juzga el arreglo.

## Resultados de la primera ronda

| | Azules (n=13) | Naranjas (n=12) |
|---|---|---|
| Diagnóstico correcto | 13/13 | 12/12 |
| La suite pasa | 11/13 | 12/12 |
| Herramientas usadas (mediana) | 6 | 7 |
| Tokens de entrada acumulados (mediana) | 355 mil | 389 mil |
| Código que el agente sumó al contexto (mediana) | 10 mil tokens | 10 mil tokens |
| Tamaño del archivo (mediana) | 385 líneas | 1.145 líneas |

La correlación de Spearman entre la nota del archivo y las herramientas que usó el agente es −0,26: con 25 casos, ruido. Medida en tokens de entrada acumulados, la correlación es −0,18. Cada sesión parte con unos 52 mil tokens fijos (instrucciones y herramientas), que se reenvían en cada turno; lo que el agente suma al contexto leyendo código es `context_growth` en `data/results.json`. Los tokens de salida que registran los transcripts no son confiables y no se usan. El único caso caro fue `black/linegen.py` (nota 32,3): 36 herramientas, 5,5 minutos y 2,8 millones de tokens de entrada, contra 4 a 12 herramientas y una mediana de 370 mil tokens en el resto. Los dos casos en que la suite no pasa (t08, t13) son archivos azules: el agente encontró el bug, aplicó el arreglo con un `sed -i` de sintaxis GNU que falla en macOS y reportó éxito sin ver el resultado.

```bash
python3 scripts/summary.py    # la tabla por intento y los agregados, desde data/results.json
```

## Resultados de la segunda ronda

| | Azules (n=10) | Naranjas (n=12) |
|---|---|---|
| La suite pasa | 10/10 | 11/12 |
| Herramientas usadas (mediana) | 6 | 8 |
| Tokens de entrada acumulados (mediana) | 356 mil | 473 mil |
| Código que el agente sumó al contexto (mediana) | 9 mil tokens | 11 mil tokens |
| Tamaño del archivo (mediana) | 591 líneas | 2.123 líneas |

Los azules están en `git/operations.rs` (92,5) y `git/mod.rs` (99,5); los naranjas en `ui/mod.rs` (15,3), `main.rs` (30,7) y `api/client.rs` (57,3). Spearman entre la nota y los tokens: −0,61. El intento naranja gastó más tokens que el azul en el 90% de los pares, y una prueba de permutación sobre la diferencia de medianas da p = 0,0006. El único intento fallido (r12, `main.rs`) no encontró el bug y atribuyó la falla al entorno.

kalku lanzó 304 mutantes en esos archivos (todos en los azules y en `config.rs`, 60 por archivo en los naranjas) y la suite mató 49. De ellos se descartaron los cambios de texto y los que borran una rama completa, y quedaron los que hacen fallar entre 1 y 15 pruebas.

## Resultados de la tercera ronda

| | Azules (n=10) | Naranjas (n=10) |
|---|---|---|
| Arreglo correcto (la prueba escondida pasa) | 10/10 | 10/10 |
| La suite pasa | 10/10 | 10/10 |
| Herramientas usadas (mediana) | 6 | 7,5 |
| Tokens de entrada acumulados (mediana) | 370 mil | 436 mil |
| Código que el agente sumó al contexto (mediana) | 10 mil tokens | 11 mil tokens |

Los azules están en `git/mod.rs`, `git/operations.rs` y `story_creator.rs` (87,3); los naranjas en `ui/mod.rs`, `main.rs` y `api/client.rs`. Spearman entre la nota y los tokens: −0,42. El naranja gastó más que el azul en el 71% de los pares; permutación sobre la diferencia de medianas, p = 0,054. Ningún agente escribió pruebas, y los 20 deshicieron la mutación exacta en el archivo correcto.

La ronda se corrió dos veces. La primera (`data/results-sc-cli-no-tests.json`), con 20 agentes a la vez, no sirve para comparar: las compilaciones se esperaban entre sí y los agentes vigilaban `cargo test` con bucles de `sleep` y `ps`, lo que triplicó los tokens (922 mil contra 1,35 millones de mediana). La segunda (`data/results-sc-cli-no-tests-nt2.json`) corrió de a 4 agentes, con `prompt-no-tests-2.md`, que les pide correr cada comando en primer plano.

```bash
python3 scripts/setup_trials_nt.py nt2            # copias en work/trials-nt2, con las mutaciones de data/mutations/sc-cli-no-tests.jsonl
python3 scripts/hidden.py work/sc-cli WEKUFE --mutate   # comprueba que la prueba escondida falla con el mutante
python3 scripts/analyze_nt.py work/runs-nt2 nt2   # data/results-sc-cli-no-tests-nt2.json
```

## Contenido

| Ruta | Qué es |
|---|---|
| `repos.txt` | Los repos medidos, con el commit exacto |
| `prompt.md`, `prompt-rust.md` | El prompt de cada agente en cada ronda, idéntico para todos |
| `capturas/` | Los mapas de cada repo |
| `data/maps/` | `km score` de cada repo y el resumen de su mapa (líneas en cada franja, directorios destacados) |
| `data/mutations/` | Las mutaciones: archivo, línea, columna, token original y mutado, tests que fallan |
| `data/trials.json` | Las 25 copias: qué mutación lleva cada una y la nota de su archivo |
| `data/kalku/` | Los reportes de kalku sobre sc-cli y, en `verified.jsonl`, cuántas pruebas hace fallar cada mutante muerto |
| `data/mutations/sc-cli.jsonl`, `data/trials-sc-cli.json`, `data/results-sc-cli.json` | Lo mismo para la segunda ronda |
| `data/mutations/sc-cli-no-tests.jsonl`, `data/reports/`, `data/hidden/` | Tercera ronda: los 20 mutantes, el reporte que recibió cada agente y la prueba escondida que juzga su arreglo |
| `prompt-no-tests.md`, `prompt-no-tests-2.md` | El prompt de la tercera ronda, en su primera y segunda corrida |
| `data/results.json` | Cada intento: herramientas, tokens de entrada acumulados, contexto inicial y su crecimiento, segundos, si la suite pasa, si el arreglo deshace la mutación exacta y el reporte final del agente |

## Reproducir

Requiere `git`, `python3`, [`uv`](https://docs.astral.sh/uv/), [`km`](https://kimun.tools) 0.45 y, para el experimento, [Claude Code](https://claude.com/claude-code).

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

La segunda ronda usa sc-cli en el commit `0d9c860` y kalku 0.24: `kalku init` en una copia, `kalku run` sobre cada archivo, `scripts/failing_rs.py` para contar las pruebas que rompe cada mutante muerto y `scripts/setup_trials_rs.py` para armar las copias. Las pruebas CLI de sc-cli leen la configuración del usuario (`~/.config/sc-cli`), así que conviene correrlas en una máquina sin ella.

`run_trials.sh` corre los agentes sin pedir permisos (`--dangerously-skip-permissions`). Hazlo en una máquina o un contenedor desechable. `MODEL` y `JOBS` eligen el modelo (por omisión `sonnet`) y cuántos corren a la vez (4).

## Cómo se corrió

- **Con quién:** el experimento se diseñó, se corrió y se analizó con Claude (Opus) en Claude Code. Claude escribió los scripts de este repositorio.
- **Modelo de los agentes:** Claude Sonnet, como subagentes de Claude Code (no con `claude -p`), con 20 agentes a la vez (4 en la segunda corrida de la tercera ronda). `analyze.py` lee los dos formatos de sesión.
- **Fecha:** 22 y 23 de octubre de 2026 (tercera ronda: 8 y 9 de noviembre), en macOS con Python 3.13 y Rust estable.
- **Mapas:** kimun 0.45, con la paleta naranja y azul (hasta 0.44 era roja y verde). En black se excluyó `profiling/` (datos de prueba) y en redis `deps/` (código de terceros).

## Límites

- Son 47 casos, con una corrida por bug y un solo modelo.
- En sc-cli los bugs están en solo cinco archivos, y la segunda ronda cambia a la vez el lenguaje, el proyecto y la herramienta de mutaciones.
- Un bug de un token que un test señala es la tarea más fácil posible: el agente lee el traceback, hace grep y lee unas 40 líneas, sin importar el tamaño del archivo. Features, refactors y bugs sin un test que los señale pueden dar otro resultado.
- El tiempo no sirve para comparar: la suite de black es la más lenta, la mayoría de los archivos naranjas son de black y los agentes corrían en paralelo.

## Licencia

MIT. Los repos medidos conservan sus propias licencias y no se incluyen aquí.
