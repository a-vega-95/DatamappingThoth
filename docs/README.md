# DatamappingThoth Pro — Documentación Técnica

## Arquitectura

```
REFACTORIZACION/
├── main.py                  # Punto de entrada → ejecutar con: python main.py
├── requirements.txt         # Dependencias: pip install -r requirements.txt
├── .gitignore
└── src/
    ├── config/
    │   └── settings.py      # Constantes centralizadas (extensiones, chunks, etc.)
    ├── core/
    │   ├── extractor.py     # Macro-Módulo 1-A: Auditoría de código
    │   ├── analyzer.py      # Macro-Módulo 1-B: Mapeador de datos (Head/Tail)
    │   └── converter.py     # Macro-Módulo 2: Conversiones universales
    ├── ui/
    │   ├── app.py           # GUI principal con dos pestañas Notebook
    │   └── styles.py        # Paleta de colores y estilos ttk centralizados
    └── utils/
        ├── pdf_utils.py     # compress_pdf() + unir_pdfs()
        └── file_utils.py    # es_archivo_texto(), inferencia de tipos, formato_bytes()
```

## Cómo ejecutar

```bash
# Desde la carpeta REFACTORIZACION/
python main.py
```

## Macro-Módulo 1 — Investigador & Mapeador

### 1-A: Extractor de Código (extractor.py)
- Genera árbol de directorios en TXT o PDF
- Consolida código fuente en TXT (para IA) y/o PDF
- Filtros inteligentes por extensión y tipo de archivo

### 1-B: Analizador de Datos (analyzer.py)
- Formatos: CSV, XLSX, XLS, XLSM, Parquet
- **Names**: Detección inteligente de encabezados
- **Dtypes**: Tipos de dato por columna (entero, decimal, fecha, texto)
- **Head** (primeras 5 filas) + **Tail** (últimas 5 filas)
- Exporta a TXT (por defecto), PDF profesional o CSV plano

## Macro-Módulo 2 — Centro de Conversión Universal

### Documentos (converter.py)
| Origen | Destino |
|--------|---------|
| TXT    | PDF, DOCX |
| PDF    | TXT, DOCX |
| PNG/JPG/JPEG | PDF |
| Múltiples PDF | PDF unido |

### Datos ETL (con chunks — sin riesgo de RAM)
| Origen | Destino |
|--------|---------|
| CSV    | XLSX, JSON, Parquet |
| XLSX/XLS | CSV, Parquet |
| JSON   | CSV |
| Parquet | CSV, XLSX |

## Dependencias opcionales
- `python-docx` → para conversiones a/desde DOCX
  ```bash
  pip install python-docx
  ```
