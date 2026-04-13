import os
import pandas as pd
import json
from PIL import Image
from fpdf import FPDF

def csv_to_excel(csv_path, excel_path, callback=None):
    """Convierte CSV a Excel por chunks para ahorrar RAM."""
    if callback: callback("Convirtiendo CSV a Excel (por chunks)...")
    
    # Usar pandas con chunksize
    chunk_size = 50000
    reader = pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False)
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for i, chunk in enumerate(reader):
            sheet_name = 'Data'
            # Escribir solo el primer chunk con header, el resto append
            startrow = i * chunk_size
            chunk.to_excel(writer, sheet_name=sheet_name, index=False, startrow=startrow, header=(i==0))
            if callback: callback(f"   Procesado bloque {i+1}...")
    
    return excel_path

def excel_to_csv(excel_path, csv_path, callback=None):
    """Convierte Excel a CSV eficiente."""
    if callback: callback("Convirtiendo Excel a CSV...")
    # Para Excel, pandas suele cargar la hoja entera, pero podemos limitar
    df = pd.read_excel(excel_path)
    df.to_csv(csv_path, index=False)
    return csv_path

def json_to_csv(json_path, csv_path, callback=None):
    """Convierte JSON a CSV."""
    if callback: callback("Convirtiendo JSON a CSV...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame([data])
    df.to_csv(csv_path, index=False)
    return csv_path

def images_to_pdf(image_paths, pdf_path, callback=None):
    """Convierte múltiples imágenes a un solo PDF de forma eficiente."""
    if callback: callback(f"Convirtiendo {len(image_paths)} imágenes a PDF...")
    
    if not image_paths:
        return None
        
    first_image = Image.open(image_paths[0])
    # Convertir a RGB si es necesario (para formatos con transparencia)
    if first_image.mode != 'RGB':
        first_image = first_image.convert('RGB')
        
    remaining_images = []
    for img_path in image_paths[1:]:
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        remaining_images.append(img)
        
    first_image.save(pdf_path, save_all=True, append_images=remaining_images)
    
    # Cerrar archivos para liberar memoria
    for img in [first_image] + remaining_images:
        img.close()
        
    return pdf_path

def txt_to_pdf(txt_path, pdf_path, callback=None):
    """Convierte archivo de texto a PDF."""
    if callback: callback("Convirtiendo Texto a PDF...")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            # Limpiar caracteres problemáticos
            line_clean = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, line_clean)
            
    pdf.output(pdf_path)
    return pdf_path

def convertir_archivo(ruta_origen, formato_destino, carpeta_salida, callback=None):
    """Función maestra de conversión."""
    nombre_base = os.path.basename(ruta_origen)
    nombre_sin_ext = os.path.splitext(nombre_base)[0]
    ext_origen = os.path.splitext(nombre_base)[1].lower()
    
    ruta_destino = os.path.join(carpeta_salida, f"{nombre_sin_ext}.{formato_destino.lower()}")
    
    try:
        # Lógica de ruteo según extensiones
        if ext_origen == '.csv' and formato_destino.lower() == 'xlsx':
            return csv_to_excel(ruta_origen, ruta_destino, callback)
        elif ext_origen in ('.xlsx', '.xls') and formato_destino.lower() == 'csv':
            return excel_to_csv(ruta_origen, ruta_destino, callback)
        elif ext_origen == '.json' and formato_destino.lower() == 'csv':
            return json_to_csv(ruta_origen, ruta_destino, callback)
        elif ext_origen in ('.png', '.jpg', '.jpeg') and formato_destino.lower() == 'pdf':
            return images_to_pdf([ruta_origen], ruta_destino, callback)
        elif ext_origen == '.txt' and formato_destino.lower() == 'pdf':
            return txt_to_pdf(ruta_origen, ruta_destino, callback)
        else:
            raise ValueError(f"Conversión de {ext_origen} a {formato_destino} no soportada aún.")
            
    except Exception as e:
        if callback: callback(f"❌ Error en conversión: {str(e)}")
        raise e
