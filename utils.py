import os
from pypdf import PdfReader, PdfWriter

def compress_pdf(input_path, output_path=None, callback=None):
    """
    Comprime un archivo PDF de forma eficiente usando streams.
    
    Args:
        input_path: Ruta del archivo PDF original.
        output_path: Ruta donde guardar el PDF comprimido. Si es None, sobreescribe el original.
        callback: Función opcional para reportar progreso.
    """
    if not output_path:
        # Generar un nombre temporal para evitar conflictos durante la escritura
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
            # Añadir página al escritor
            writer.add_page(page)
            # Aplicar compresión de contenido si es posible
            page.compress_content_streams()

        # Escribir el resultado a un archivo temporal para mayor seguridad
        with open(temp_path, "wb") as f:
            writer.write(f)

        # Reemplazar el archivo destino con el comprimido
        if os.path.exists(temp_path):
            if os.path.exists(output_path) and output_path == input_path:
                os.replace(temp_path, output_path)
            else:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_path, output_path)

        if callback:
            size_old = os.path.getsize(input_path) / 1024
            size_new = os.path.getsize(output_path) / 1024
            ahorro = ((size_old - size_new) / size_old) * 100 if size_old > 0 else 0
            callback(f"✅ PDF comprimido: {size_old:.1f}KB -> {size_new:.1f}KB ({ahorro:.1f}% ahorro)")

        return output_path

    except Exception as e:
        if callback:
            callback(f"⚠️ Aviso: No se pudo comprimir el PDF: {str(e)}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return input_path
