"""
settings.py — Configuración centralizada de DatamappingThoth
Centraliza extensiones soportadas, carpetas ignoradas y constantes globales.
"""

# ─────────────────────────────────────────────
# EXTRACTOR DE CÓDIGO: Filtros de exclusión
# ─────────────────────────────────────────────

EXTENSIONES_IGNORADAS = {
    '.exe', '.dll', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
    '.pyc', '.pyo', '.pyd',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.pdf',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.wav',
    '.db', '.sqlite', '.sqlite3',
    '.git', '.svn',
}

CARPETAS_IGNORADAS = {
    '.git', '__pycache__', 'node_modules',
    'venv', '.venv', 'env', '.env',
    '.idea', '.vscode',
    'dist', 'build',
    '.pytest_cache', '.mypy_cache',
    'REFACTORIZACION',  # Ignorar esta misma carpeta al escanear
}

# Extensiones de código fuente reconocidas para consolidación
EXTENSIONES_CODIGO = {
    # Python / Scripts
    '.py', '.pyw',
    # Web
    '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
    '.html', '.htm', '.css', '.scss', '.sass', '.less',
    # Backend / Sistema
    '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go',
    '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
    '.r', '.m',
    # Datos / Config
    '.sql', '.json', '.xml', '.yaml', '.yml',
    '.toml', '.ini', '.cfg', '.conf', '.env.example',
    # Shell / Scripts
    '.sh', '.bash', '.ps1', '.bat', '.cmd',
    # Docs / Markdown
    '.md', '.rst', '.txt', '.gitignore',
    # Build
    '.dockerfile', '.gradle', '.cmake', '.makefile',
}

# ─────────────────────────────────────────────
# MAPEADOR DE DATOS: Formatos soportados
# ─────────────────────────────────────────────

EXTENSIONES_DATOS = {'.csv', '.xlsx', '.xls', '.xlsm', '.parquet', '.pq'}

# ─────────────────────────────────────────────
# ANÁLISIS: Constantes de muestreo
# ─────────────────────────────────────────────

CHUNK_SIZE = 10_000          # Filas por bloque de lectura
MUESTRA_VALORES = 5          # Valores únicos a mostrar por columna
MAX_FILAS_BUSQUEDA_HEADER = 20  # Filas máximas para detectar encabezados
HEAD_TAIL_ROWS = 5           # Filas para Head & Tail

# ─────────────────────────────────────────────
# CONVERSOR: Mapeo de rutas origen → destino
# ─────────────────────────────────────────────

CHUNK_EXCEL = 50_000  # Filas por chunk al escribir Excel

# Versión del proyecto
VERSION = "2.0.0"
APP_NAME = "DatamappingThoth Pro"
