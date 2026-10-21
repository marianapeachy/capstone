# Fuentes de los diagramas de casos de uso

Los PNG de `Anexos/Diseño/` se generan desde estos archivos. Para cambiar
un diagrama, editar su fuente y volver a exportar el PNG con el mismo
nombre.

- `Diagrama General Casos de Uso.drawio`: se abre y exporta en draw.io
  (Archivo > Exportar como > PNG). PNG en
  `Anexos/Diseño/Diagrama General Casos de Uso.png`.
- `Diagrama C.U 0X.mmd`: diagramas de secuencia en Mermaid. PNG en
  `Anexos/Diseño/Diagramas particulares por cada C. U._/`, con tema oscuro
  como los originales. Con mermaid-cli (Node.js), desde esta carpeta:

  ```bash
  npx -y @mermaid-js/mermaid-cli@11 -i "Diagrama C.U 01.mmd" \
    -o "../Diagramas particulares por cada C. U._/Diagrama C.U 01.png" \
    -c mermaid-config.json -b "#111111" -s 2
  ```

  También en draw.io: Organizar > Insertar > Avanzado > Mermaid, pegar el
  contenido y exportar a PNG. CU00-CU06 se regeneraron con mermaid-cli el
  2026-10-21 (ítem #42, app Django); CU07, el 2026-10-19 (ítem #40). Las
  notas largas se parten con `<br/>` para que no se salgan del recuadro.
- `Diagrama de Arquitectura.mmd`: diagrama de arquitectura (flowchart).
  PNG en `Anexos/Diseño/Diagrama de arquitectura/Diagrama de Arquitectura.png`,
  con el mismo comando y configuración.
