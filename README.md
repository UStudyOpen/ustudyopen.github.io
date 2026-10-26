# UStudyOpen — portal central

Portal Quarto para https://ustudyopen.github.io/, con UStudyOpen Design 0.3.0.
La versión inicial se prepara en un PR para revisión visual. No habilitar Pages
ni fusionar el PR inicial hasta la autorización de ngulloa.

## Desarrollo

Requiere Quarto 1.10.18, Python 3.14.8 y Node 24.21.0. Para las pruebas visuales,
Chrome/Chromium con sandbox activo (`BROWSER_EXECUTABLE` permite elegir el binario).

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r tests/requirements-licensing.txt
python3 tests/licensing.py --reuse
python3 tests/test_catalog.py
python3 tools/catalog.py --verify-sources
python3 tests/render_clean.py
python3 tests/validate.py
python3 tests/browser_portal.py
python3 tests/install_actionlint.py
artifacts/tools/actionlint -shellcheck= .github/workflows/*.yml
python3 -m http.server 8766 --bind 127.0.0.1 --directory _site
```

Abrir http://127.0.0.1:8766/. El artefacto y las capturas están ignorados por Git.
La auditoría automática WCAG 2.2 AA no sustituye la revisión humana.

## Estructura

- `index.qmd`: presentación y catálogo generado.
- `proyecto.qmd`, `licencias.qmd`: proyecto, autoría y avisos.
- `data/catalog.json`: única fuente editable del catálogo.
- `tools/catalog.py`: importación, validación y generación de las tarjetas.
- `assets/portal.css`: composición local con tokens del diseño compartido.
- `_extensions/ustudyopen-design/`: extensión sin modificaciones.
- `design-vendor.json`, `platform-vendor.json`: integridad SHA-256.
- `LICENSE`, `LICENSES/`, `LICENSING.md`, `THIRD-PARTY-NOTICES.md`: licencias.
- `tests/`: render aislado, metadatos, enlaces, legal y navegador.
- `.github/workflows/`: validación de PR y publicación protegida desde `main`.

## Añadir o actualizar una asignatura

Publicar y revisar su propio repositorio primero. Desde este portal:

```sh
python3 tools/catalog.py --import-course ../nueva-asignatura \
  --area 'Matemáticas' --summary 'Descripción breve y verificada del curso.'
```

El importador exige `course.yml` sin cambios pendientes y verifica el archivo
público en el commit exacto, su SHA-256 y el sitio HTTP antes de modificar
`data/catalog.json`. Actualiza el registro existente por slug o añade uno nuevo.
Revisar el único diff de metadatos, ejecutar las pruebas y abrir un PR.
No editar `_catalog.qmd`: se genera antes del render, no se versiona.
Para ejecutar `quarto render` directamente por primera vez, ejecutar antes
`python3 tools/catalog.py --generate`; `tests/render_clean.py` ya lo hace.
No hay consultas a la API de GitHub durante las visitas al portal.

La copia de metadatos conserva páginas, estados y revisión humana declarada,
no los cuerpos de las lecciones. Una actualización académica exige importar y
revisar un nuevo commit. Los campos publicado y estado académico son distintos.
`lista` exige todas las páginas requeridas revisadas y ningún tema requerido pendiente.

## Publicación y licencias

Seguir [PUBLISHING.md](PUBLISHING.md) solo después de aprobar la revisión inicial.
Las protecciones exigen PR, check `validate`, rama actualizada y conversaciones
resueltas. Un único mantenedor puede revisar su propio diff y fusionar: se exigen
cero revisiones ajenas para evitar un bloqueo imposible de satisfacer.

El scaffolding y la documentación usan MIT de ngulloa. Los cursos mantienen sus
licencias académicas y avisos independientes. Véase [LICENSING.md](LICENSING.md).
