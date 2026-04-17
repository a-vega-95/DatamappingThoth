"""
pdf_utils.py — Utilidades de gestión de PDF
Compresión, unión y helpers para archivos PDF usando pypdf.
"""

import os
from pypdf import PdfReader, PdfWriter


def compress_pdf(input_path: str, output_path: str = None, callback=None) -> str:
    """
    Comprime un archivo PDF aplicando compresión de streams en cada página.

    Args:
        input_path:  Ruta del PDF original.
        output_path: Ruta de salida. Si es None, sobreescribe el original.
        callback:    Función opcional para reportar progreso (str → None).

    Returns:
        Ruta del PDF comprimido.
    """
    if not output_path:
        output_path = input_path
        temp_path = input_path + ".tmp"
    else:
        temp_path = output_path + ".tmp"

    try:
        if callback:
            callback(f"Comprimiendo PDF: {os.path.basename(input_path)}...")

        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)
            page.compress_content_streams()

        with open(temp_path, "wb") as f:
            writer.write(f)

        # Reemplazo atómico
        if os.path.exists(temp_path):
            if output_path == input_path and os.path.exists(output_path):
                os.replace(temp_path, output_path)
            else:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_path, output_path)

        if callback:
            size_old = os.path.getsize(input_path) / 1024
            size_new = os.path.getsize(output_path) / 1024
            ahorro = ((size_old - size_new) / size_old * 100) if size_old > 0 else 0
            callback(f"✅ PDF comprimido: {size_old:.1f} KB → {size_new:.1f} KB ({ahorro:.1f}% ahorro)")

        return output_path

    except Exception as e:
        if callback:
            callback(f"⚠️ No se pudo comprimir el PDF: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return input_path


def unir_pdfs(lista_rutas: list, ruta_salida: str, callback=None) -> str:
    """
    Combina múltiples archivos PDF en un único documento.

    Args:
        lista_rutas: Lista de rutas PDF a combinar (en orden).
        ruta_salida: Ruta del PDF resultante.
        callback:    Función opcional de progreso.

    Returns:
        Ruta del PDF combinado.
    """
    if not lista_rutas:
        raise ValueError("La lista de archivos PDF está vacía.")

    if callback:
        callback(f"Uniendo {len(lista_rutas)} archivos PDF...")

    merger = PdfWriter()

    for i, pdf_path in enumerate(lista_rutas):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
        merger.append(pdf_path)
        if callback:
            callback(f"   Agregado [{i+1}/{len(lista_rutas)}]: {os.path.basename(pdf_path)}")

    with open(ruta_salida, "wb") as f:
        merger.write(f)

    merger.close()

    if callback:
        callback(f"✅ PDF unido guardado en: {ruta_salida}")

    return ruta_salida
