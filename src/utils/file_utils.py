"""
file_utils.py — Utilidades de detección de archivos
Detecta si un archivo es texto o binario, y los tipos de dato de sus valores.
"""


def es_archivo_texto(ruta_archivo: str) -> bool:
    """
    Intenta leer las primeras 1024 bytes del archivo para determinar
    si es texto legible (UTF-8) o un binario.

    Returns:
        True si el archivo puede leerse como texto, False si es binario.
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, PermissionError, IOError):
        return False


def detectar_tipo_str(valor_str: str) -> str:
    """
    Infiere el tipo de dato de un string.

    Returns:
        'entero' | 'decimal' | 'fecha' | 'texto'
    """
    if not valor_str or valor_str.strip() == '':
        return 'texto'

    # Entero / Decimal
    try:
        cleaned = valor_str.replace(',', '').replace('.', '').strip()
        int(cleaned)
        return 'decimal' if ('.' in valor_str or ',' in valor_str) else 'entero'
    except ValueError:
        pass

    try:
        float(valor_str.replace(',', '.').strip())
        return 'decimal'
    except ValueError:
        pass

    # Fecha heurística
    if any(sep in valor_str for sep in ['/', '-']) and len(valor_str) <= 20:
        if any(c.isdigit() for c in valor_str):
            return 'fecha'

    return 'texto'


def detectar_tipo_valor(valor) -> str:
    """
    Infiere el tipo de dato de un valor Python nativo (int, float, datetime, bool…).

    Returns:
        'entero' | 'decimal' | 'fecha' | 'booleano' | 'texto'
    """
    if valor is None:
        return 'texto'

    tipo = type(valor).__name__

    if tipo in ('int', 'int64', 'int32'):
        return 'entero'
    elif tipo in ('float', 'float64', 'float32'):
        return 'decimal'
    elif tipo == 'datetime':
        return 'fecha'
    elif tipo == 'bool':
        return 'booleano'

    return 'texto'


def formato_bytes(bytes_num: int) -> str:
    """Formatea un número de bytes a una unidad legible (KB, MB, GB, TB)."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_num < 1024:
            return f"{bytes_num:.1f} {unit}"
        bytes_num /= 1024
    return f"{bytes_num:.1f} TB"
