// Proyectos (cursos): agrupan clips ordenados con continuidad narrativa y
// estilo compartido.
//
// Este archivo solo ENRUTA. Con `routeId` en el hash se pinta el detalle de
// un curso; sin el, el indice. Todo lo demas vive en `components/proyectos/`:
//
//   ProjectsList  el indice — familias plegables, buscador, filtro y orden
//   FamilyGroup   una familia con su progreso agregado (ProjectGrid dentro)
//   ProjectCard   la tarjeta de un curso
//   ProjectDetail el detalle — cabecera, panel de estado, acciones y clips
//   ClipCard      un clip (+ FilaAudio: voz, musica y SFX en una fila)
//   insignias     ProgressBar, CountsLine, NarrBadge, Stat, DurationBadge
//   meta.js       el vocabulario compartido (estados, rangos, agrupacion)
//   *Dialog       nuevo proyecto, anadir clip, estilo, duplicar, historial
//
// Hasta R5a esto era UN archivo de 1 667 lineas con trece subcomponentes
// dentro, y cualquier cambio en la fila de audio de un clip obligaba a leer
// el indice de cursos entero.

import ProjectsList from './components/proyectos/ProjectsList.jsx'
import ProjectDetail from './components/proyectos/ProjectDetail.jsx'

export default function Projects({ jobs, onEditClip, routeId, onRoute, aiEnabled }) {
  if (routeId) {
    return (
      <ProjectDetail key={routeId} projectId={routeId} jobs={jobs} aiEnabled={aiEnabled}
        onEditClip={onEditClip} onBack={() => onRoute(null)} onOpen={(id) => onRoute(id)} />
    )
  }
  return <ProjectsList onOpen={(id) => onRoute(id)} />
}
