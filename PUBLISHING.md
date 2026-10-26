# Primera publicación (solo tras autorización humana)

## Estado de revisión

La rama inicial del portal contiene todo el sitio; `main` comienza únicamente
con el README para permitir un PR inicial revisable. No hacer merge ni activar
la variable de publicación durante la preparación. No existe un primer despliegue
autorizado.

GitHub activó Pages automáticamente para este repositorio de organización y
rechazó desactivarlo por API. La compilación Jekyll inicial se canceló sin
desplegar. La fuente quedó en **GitHub Actions** y `USO_PAGES_ENABLED=false`:
ningún workflow del portal puede publicar hasta la autorización y el merge.

## Aprobar y publicar

1. Revisar las cuatro capturas de portada (escritorio/móvil, claro/oscuro),
   y abrir el artefacto local siguiendo README. Revisar navegación por teclado,
   catálogo, textos, autoría y licencias. Resolver las conversaciones del PR.
2. Autorizar expresamente el primer despliegue y verificar que `validate` esté
   verde para el último commit del PR y que la rama esté actualizada con `main`.
3. Confirmar en Settings → Pages → Build and deployment → Source: **GitHub Actions**
   (ya configurada para impedir el despliegue automático mediante Jekyll).
   Para este sitio de organización la URL es https://ustudyopen.github.io/.
   No configurar un prefijo `/ustudyopen.github.io/`, dominio personalizado ni CNAME.
4. Verificar Settings → Environments → `github-pages`: permitir despliegues solo
   desde ramas protegidas. No exigir otro revisor a un único mantenedor ni impedir
   la autoaprobación. La aprobación se materializa al revisar y fusionar el PR.
5. Activar la variable del repositorio:
   `gh variable set USO_PAGES_ENABLED --body true -R UStudyOpen/ustudyopen.github.io`
6. Fusionar el PR mediante la interfaz de GitHub, respetando la protección de
   `main`. El push del merge ejecuta `Publish portal`, recompila desde fuentes
   limpias, valida y despliega el artefacto oficial de Pages.
7. Esperar el workflow y comprobar https://ustudyopen.github.io/, ambos temas,
   las rutas `proyecto.html` y `licencias.html`, los avisos y los tres enlaces de cursos.

Si el PR se fusiona antes de activar la variable, no se publicará. Tras activar
Pages y la variable ejecutar `gh workflow run deploy.yml --ref main -R
UStudyOpen/ustudyopen.github.io` para publicar el mismo `main` revisado.

## Operación posterior

Cada cambio entra por PR. El workflow de validación tiene solo `contents: read`;
únicamente el job de despliegue posee `pages: write` e `id-token: write`.
Las acciones están fijadas a commits; Quarto, Node, Python, REUSE y axe están fijados.
El workflow no copia secretos, tests, fuentes ni archivos de trabajo al artefacto.

Para detener futuros despliegues automáticos, poner `USO_PAGES_ENABLED=false`.
Esto no retira el sitio ya publicado. Para revertir contenido, abrir un PR que
revierta el cambio y validarlo; no forzar `main`. Nunca usar el artefacto del
portal para borrar ni modificar los repositorios de los cursos.
