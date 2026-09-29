// Human-readable labels for the API values. Unknown values fall back to the raw value,
// so a new category added in the backend still displays without changing this file.
export const LABELS = {
  categoria: {
    bug: "Error / Bug",
    datos: "Pedido de datos",
    acceso: "Pedido de acceso",
    automatizacion: "Automatización",
    consulta: "Consulta",
    otro: "Otro",
  },
  prioridad: { alta: "Alta", media: "Media", baja: "Baja" },
  area_sugerida: {
    backend: "Backend",
    frontend: "Frontend",
    data: "Data",
    devops: "DevOps",
    producto: "Producto",
    digital_transformation: "Digital Transformation",
  },
  idioma: { es: "Español", pt: "Portugués" },
};

export function label(field, value) {
  return LABELS[field]?.[value] ?? value;
}
