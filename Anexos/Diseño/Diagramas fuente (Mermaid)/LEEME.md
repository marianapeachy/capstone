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
  contenido y exportar a PNG. CU01-CU04 y CU07 se regeneraron con
  mermaid-cli el 2026-10-19 (ítem #40); CU05 y CU06, con draw.io.

CU00 no cambió y no tiene fuente aquí (solo su PNG).
