"""
extractor.py — Motor de auditoría de código fuente
Macro-Módulo 1-A: Genera árbol de directorios y consolida el código
del proyecto en archivos TXT (por defecto) y/o PDF.
"""

import os
from typing import Optional, Callable, Dict

from fpdf import FPDF

from src.config.settings import (
    EXTENSIONES_IGNORADAS, CARPETAS_IGNORADAS, EXTENSIONES_CODIGO,
)
from src.utils.file_utils import es_archivo_texto
from src.utils.pdf_utils import compress_pdf


# ─────────────────────────────────────────────
# Clases PDF internas
# ─────────────────────────────────────────────

class _PDFCodigo(FPDF):
    """PDF para el consolidado de código fuente."""

    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, 'Consolidado de Código Fuente — DatamappingThoth Pro', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def titulo_archivo(self, titulo: str):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(200, 220, 255)
        t = titulo.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 9, t, 0, 1, 'L', True)
        self.ln(3)

    def cuerpo_codigo(self, body: str):
        self.set_font('Courier', '', 8)
        body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 4, body)
        self.ln()


class _PDFMapa(FPDF):
    """PDF para el mapa de directorios."""

    def __init__(self):
        super().__init__()
        self._titulo = "Estructura de Directorios"

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, self._titulo, 0, 1, 'C')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def seccion(self, titulo: str):
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 7, titulo, 0, 1, 'L', True)
        self.ln(2)

    def linea(self, texto: str):
        self.set_font('Courier', '', 7)
        texto = texto.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 4, texto[:130], 0, 1)


# ─────────────────────────────────────────────
# Función principal
# ─────────────────────────────────────────────

def generar_auditoria(
    ruta_raiz: str,
    carpeta_salida: Optional[str] = None,
    nombre_mapa: str = "mapa_proyecto.txt",
    nombre_txt: str = "Codigo_Fuente_Completo.txt",
    nombre_pdf: str = "Codigo_Fuente_Completo.pdf",
    generar_mapa: bool = True,
    generar_txt: bool = True,
    generar_pdf: bool = False,
    solo_codigo: bool = True,
    extensiones_custom: Optional[set] = None,
    callback: Optional[Callable[[str], None]] = None,
) -> Dict:
    """
    Escanea un proyecto y genera:
      - Árbol de directorios (TXT o PDF)
      - Código fuente consolidado (TXT y/o PDF)

    Args:
        ruta_raiz:         Directorio raíz a escanear.
        carpeta_salida:    Dónde guardar los archivos (None = misma carpeta).
        nombre_mapa:       Nombre del mapa (extensión determina formato).
        nombre_txt:        Nombre del TXT consolidado.
        nombre_pdf:        Nombre del PDF consolidado.
        generar_mapa:      Si True, genera el árbol de directorios.
        generar_txt:       Si True, genera el TXT consolidado (ideal para IA).
        generar_pdf:       Si True, genera el PDF consolidado.
        solo_codigo:       Si True, usa EXTENSIONES_CODIGO; si False, incluye
                           todo lo que sea texto y no esté ignorado.
        extensiones_custom: Conjunto personalizado de extensiones (override).
        callback:          Función para reportar progreso.

    Returns:
        Dict con claves: archivos_procesados, total_archivos,
        conteo_formatos, ruta_mapa, ruta_txt, ruta_pdf.
    """
    if not any([generar_mapa, generar_txt, generar_pdf]):
        return {}

    def log(msg: str):
        if callback:
            callback(msg)
        print(msg)

    # Normalizar rutas
    ruta_raiz = os.path.normpath(os.path.abspath(ruta_raiz))
    carpeta_salida = os.path.normpath(os.path.abspath(carpeta_salida)) \
        if carpeta_salida else ruta_raiz

    # Extensiones efectivas
    if extensiones_custom:
        ext_permitidas = extensiones_custom
    elif solo_codigo:
        ext_permitidas = EXTENSIONES_CODIGO
    else:
        ext_permitidas = None  # None = incluir todo texto no ignorado

    # Inicializar acumuladores
    estructura_arbol: list[str] = []
    txt_bloques: list[str] = []
    conteo_formatos: Dict[str, int] = {}
    total_archivos = 0
    archivos_procesados = 0

    pdf_codigo = None
    if generar_pdf:
        pdf_codigo = _PDFCodigo()
        pdf_codigo.add_page()

    log(f"Iniciando auditoría en: {ruta_raiz}")

    # Primera pasada: contar totales
    for root, dirs, files in os.walk(ruta_raiz):
        dirs[:] = [d for d in dirs if d not in CARPETAS_IGNORADAS]
        total_archivos += len(files)

    # Segunda pasada: procesar
    for root, dirs, files in os.walk(ruta_raiz):
        dirs[:] = [d for d in dirs if d not in CARPETAS_IGNORADAS]

        try:
            rel_dir = os.path.relpath(root, ruta_raiz)
            nivel = 0 if rel_dir == '.' else rel_dir.count(os.sep) + 1
        except ValueError:
            nivel = 0

        indent = '    ' * nivel
        nombre_carpeta = os.path.basename(root) or os.path.basename(ruta_raiz)
        estructura_arbol.append(f"{indent}[DIR] {nombre_carpeta}/")
        sub = '    ' * (nivel + 1)

        for nombre_f in sorted(files):
            ruta_f = os.path.join(root, nombre_f)
            ext = os.path.splitext(nombre_f)[1].lower()

            # Mapa de árbol
            estructura_arbol.append(f"{sub}|-- {nombre_f}")
            conteo_formatos[ext] = conteo_formatos.get(ext, 0) + 1

            # Determinar si incluir en consolidado
            if generar_txt or generar_pdf:
                if ext_permitidas is not None:
                    incluir = (ext in ext_permitidas or
                               nombre_f.lower() in ext_permitidas)
                else:
                    incluir = ext not in EXTENSIONES_IGNORADAS

                if incluir and es_archivo_texto(ruta_f):
                    try:
                        with open(ruta_f, 'r', encoding='utf-8',
                                  errors='replace') as fh:
                            contenido = fh.read()

                        ruta_rel = os.path.relpath(ruta_f, ruta_raiz)

                        if generar_txt:
                            separador = '=' * 80
                            txt_bloques.append(
                                f"\n{separador}\n"
                                f"ARCHIVO: {ruta_rel}\n"
                                f"{separador}\n"
                            )
                            txt_bloques.append(contenido)
                            txt_bloques.append("\n")

                        if generar_pdf and pdf_codigo:
                            pdf_codigo.titulo_archivo(f"Archivo: {ruta_rel}")
                            pdf_codigo.cuerpo_codigo(contenido)

                        archivos_procesados += 1
                        if archivos_procesados % 10 == 0:
                            log(f"  Procesados: {archivos_procesados} archivos de código...")

                    except Exception as exc:
                        log(f"  ⚠ Error leyendo {nombre_f}: {exc}")

    # ── Crear carpeta de salida ──
    os.makedirs(carpeta_salida, exist_ok=True)

    ruta_mapa = ruta_txt = ruta_pdf = None

    # ── Guardar MAPA ──
    if generar_mapa:
        ruta_mapa = os.path.join(carpeta_salida, nombre_mapa)
        es_pdf_mapa = ruta_mapa.lower().endswith('.pdf')
        try:
            if es_pdf_mapa:
                pdf_mapa = _PDFMapa()
                pdf_mapa.add_page()
                pdf_mapa.seccion("ÁRBOL DE DIRECTORIOS")
                for linea in estructura_arbol:
                    pdf_mapa.linea(linea)
                pdf_mapa.ln(4)
                pdf_mapa.seccion("DISTRIBUCIÓN POR EXTENSIÓN")
                for ext_k, cnt in sorted(conteo_formatos.items()):
                    pdf_mapa.linea(f"{ext_k or 'Sin ext'}: {cnt} archivos")
                pdf_mapa.output(ruta_mapa)
                ruta_mapa = compress_pdf(ruta_mapa, callback=log)
            else:
                with open(ruta_mapa, 'w', encoding='utf-8') as fm:
                    fm.write("ESTRUCTURA DE DIRECTORIOS\n")
                    fm.write("=" * 60 + "\n\n")
                    for linea in estructura_arbol:
                        fm.write(linea + "\n")
                    fm.write("\n\nDISTRIBUCIÓN POR EXTENSIÓN\n")
                    fm.write("=" * 60 + "\n")
                    for ext_k, cnt in sorted(conteo_formatos.items()):
                        fm.write(f"{ext_k or 'Sin ext'}: {cnt} archivos\n")
            log(f"✅ Mapa guardado: {ruta_mapa}")
        except Exception as exc:
            log(f"❌ Error guardando mapa: {exc}")

    # ── Guardar TXT CONSOLIDADO ──
    if generar_txt and txt_bloques:
        ruta_txt = os.path.join(carpeta_salida, nombre_txt)
        try:
            with open(ruta_txt, 'w', encoding='utf-8') as ft:
                ft.write(f"REPORTE DE CÓDIGO FUENTE CONSOLIDADO\n")
                ft.write(f"Proyecto : {os.path.basename(ruta_raiz)}\n")
                ft.write(f"Archivos : {archivos_procesados} procesados "
                         f"de {total_archivos} encontrados\n")
                ft.write("=" * 80 + "\n\n")
                ft.write("".join(txt_bloques))
            log(f"✅ TXT consolidado guardado: {ruta_txt}")
        except Exception as exc:
            log(f"❌ Error guardando TXT: {exc}")

    # ── Guardar PDF CONSOLIDADO ──
    if generar_pdf and pdf_codigo and archivos_procesados > 0:
        ruta_pdf = os.path.join(carpeta_salida, nombre_pdf)
        try:
            pdf_codigo.output(ruta_pdf)
            ruta_pdf = compress_pdf(ruta_pdf, callback=log)
            log(f"✅ PDF consolidado guardado: {ruta_pdf}")
        except Exception as exc:
            log(f"❌ Error guardando PDF: {exc}")

    log(f"\n🏁 Auditoría finalizada — {archivos_procesados} archivos de código procesados.")

    return {
        'archivos_procesados': archivos_procesados,
        'total_archivos': total_archivos,
        'conteo_formatos': conteo_formatos,
        'ruta_mapa': ruta_mapa,
        'ruta_txt': ruta_txt,
        'ruta_pdf': ruta_pdf,
    }
