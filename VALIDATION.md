# Validación inicial — 26 de octubre de 2026

Ejecutada localmente con Quarto 1.10.18, Python 3.14.8, Node 24.21.0,
REUSE 6.2.0, actionlint 1.7.12 y axe-core 4.14.0. Las dependencias externas
se verifican con hashes; el navegador usa un perfil temporal y sandbox activo.

- Render limpio y aislado: tres páginas, sin errores ni advertencias finales.
- Integridad de salida: 79 referencias locales, anclas, recursos CSS, temas y
  manifiesto de 41 archivos legales correctos. Sitio de organización en `/`.
- Catálogo: seis pruebas, incluidas promoción académica indebida, páginas sin
  revisión, duplicados, rutas equivocadas y referencias sin commit fijo.
- Procedencia: SHA-256 y metadatos de los tres `course.yml` comparados con
  archivos públicos en commits exactos. Los tres sitios responden HTTP 200.
- Licencias: validador compartido y REUSE en el alcance declarado, sin errores.
  Se conservan los textos y manifiestos del diseño. No se afirma conformidad
  REUSE total de todos los archivos heredados.
- actionlint: workflows sin errores; acciones fijadas y permisos comprobados.
- Navegador: 37 comprobaciones correctas; navegación por teclado, enlace para
  saltar al contenido, foco visible, cambio de tema, menú móvil y enlaces.
- Responsive: 1440px, 390px y reflow a 320px sin desbordamiento horizontal.
- Axe: 12 auditorías (tres páginas × dos tamaños × dos temas), cero infracciones
  automáticas con etiquetas WCAG 2 A/AA, 2.1 A/AA y 2.2 AA. Axe pide comprobar
  contraste de dos flechas decorativas `aria-hidden` de la portada; se revisaron
  visualmente en ambos temas. Esto no es una certificación WCAG 2.2 AA.
- Artefacto: sin fuentes QMD/Python, directorios privados, secretos, rutas de
  la máquina ni repositorios de trabajo. Tamaño aproximado 1.73 MiB sin comprimir.
- Enlaces públicos del proyecto, plantilla, diseño, autor y avisos de las tres
  asignaturas: HTTP 200. El repositorio público del portal ya existe; el dominio
  raíz se verificará tras el primer despliegue autorizado.
- Preservación: archivos, estado Git y HEAD de los tres cursos y del diseño
  comparados antes/después sin cambios. Los cambios previos en docs de BD siguen
  tal como estaban al inicio; no se renderizó ni modificó ningún curso.

Evidencia local ignorada por Git: `artifacts/platform/portal-browser.json`,
cuatro `home-{desktop,mobile}-{light,dark}.png` y `artifacts/validation.json`.
El directorio hermano `review/portal-2026-10-26/` conserva logs y comparación de
preservación. En GitHub, la evidencia de cada ejecución estará en su artefacto
`validation-evidence` (siete días).

Tras la autorización del titular, se creó el repositorio público y el
[PR inicial #1](https://github.com/UStudyOpen/ustudyopen.github.io/pull/1).
`main` conserva solo el README; el sitio permanece en la rama del PR.
Los resultados de CI y las capturas se consultan en los checks y el artefacto
`validation-evidence` del PR, sin publicar el portal.

GitHub activó Pages automáticamente al crear el repositorio de organización e
inició una compilación Jekyll. Se canceló antes de desplegar:
[ejecución cancelada](https://github.com/UStudyOpen/ustudyopen.github.io/actions/runs/40409405027).
La API rechazó desactivar Pages (HTTP 422); se cambió su fuente a GitHub Actions
para impedir las compilaciones automáticas desde la rama. No hubo despliegues.
`USO_PAGES_ENABLED=false` bloquea el workflow de publicación del portal y el
entorno `github-pages` admite solo ramas protegidas. La protección de `main`
exige PR y check `validate` de GitHub Actions. La primera publicación sigue
pendiente de revisión y autorización expresa; véase PUBLISHING.md.
