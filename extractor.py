"""
Extractor de Código Fuente a PDF
Genera: mapa de directorios, reporte de distribución y PDF consolidado
"""

import os
from fpdf import FPDF

# CONFIGURACIÓN POR DEFECTO
EXTENSIONES_IGNORADAS = {'.exe', '.dll', '.png', '.jpg', '.jpeg', '.pyc', '.git', '.zip', '.pdf', '.ico', '.gif', '.bmp', '.mp3', '.mp4', '.avi', '.mov', '.db', '.sqlite'}
CARPETAS_IGNORADAS = {'.git', '__pycache__', 'node_modules', 'venv', '.idea', '.vscode', 'env', '.env', 'dist', 'build', '.pytest_cache', '.mypy_cache'}

# Extensiones de código fuente (para filtrar en PDF)
EXTENSIONES_CODIGO = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
    '.sql', '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
    '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.sh', '.bash', '.ps1', '.bat', '.cmd', '.dockerfile',
    '.md', '.rst', '.txt', '.gitignore', '.env.example',
    '.gradle', '.maven', '.cmake', '.makefile'
}


class PDFGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, 'Documentación de Código Fuente', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Courier', '', 8)
        # Limpiar caracteres problemáticos para latin-1
        body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, body)
        self.ln()


class PDFReporte(FPDF):
    """Clase para generar reportes de estructura en PDF"""
    def __init__(self, titulo="Reporte"):
        super().__init__()
        self.titulo_reporte = titulo
    
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, self.titulo_reporte, 0, 1, 'C')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    
    def seccion(self, titulo):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 8, titulo, 0, 1, 'L', 1)
        self.ln(2)
    
    def contenido(self, texto):
        self.set_font('Courier', '', 7)
        texto = texto.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 4, texto)
    
    def linea(self, texto, negrita=False):
        if negrita:
            self.set_font('Arial', 'B', 9)
        else:
            self.set_font('Courier', '', 7)
        texto = texto.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 4, texto[:120], 0, 1)  # Limitar largo


def es_archivo_texto(ruta_archivo):
    """Intenta leer el archivo para ver si es texto o binario"""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, PermissionError, IOError):
        return False


def generar_arbol_y_extraer(ruta_raiz, nombre_pdf="Codigo_Fuente_Completo.pdf", 
                            nombre_mapa="mapa_proyecto.txt", callback=None,
                            generar_mapa=True, generar_pdf=True,
                            extensiones_codigo=None, carpeta_salida=None):
    """
    Genera el árbol de directorios, estadísticas y PDF.
    
    Args:
        ruta_raiz: Directorio a escanear
        nombre_pdf: Nombre del archivo PDF de salida
        nombre_mapa: Nombre del archivo de mapa de salida
        callback: Función opcional para reportar progreso (mensaje)
        generar_mapa: Si True, genera el archivo de mapa de directorios
        generar_pdf: Si True, genera el PDF con código fuente
        extensiones_codigo: Set de extensiones a incluir en PDF (None = todas las de texto)
        carpeta_salida: Carpeta donde guardar los archivos (None = misma que ruta_raiz)
    
    Returns:
        dict con estadísticas del proceso
    """
    if not generar_mapa and not generar_pdf:
        return None
    
    # 0. Normalizar rutas para evitar problemas de slash/backslash
    ruta_raiz = os.path.normpath(os.path.abspath(ruta_raiz))
    if carpeta_salida:
        carpeta_salida = os.path.normpath(os.path.abspath(carpeta_salida))
    else:
        carpeta_salida = ruta_raiz

    pdf = None
    if generar_pdf:
        pdf = PDFGenerator()
        pdf.add_page()
    
    estructura_arbol = []
    conteo_formatos = {}
    archivos_procesados = 0
    total_archivos = 0
    
    def log(mensaje):
        if callback:
            callback(mensaje)
        print(mensaje)
    
    log(f"Iniciando escaneo en: {ruta_raiz}...")

    # Primer paso: contar archivos totales
    for root, dirs, files in os.walk(ruta_raiz):
        dirs[:] = [d for d in dirs if d not in CARPETAS_IGNORADAS]
        total_archivos += len(files)
    
    archivos_analizados = 0
    
    for root, dirs, files in os.walk(ruta_raiz):
        # Filtrar carpetas ignoradas
        dirs[:] = [d for d in dirs if d not in CARPETAS_IGNORADAS]
        
        # Nivel de indentación para el mapa visual
        # Usar os.path.relpath es más seguro que replace para rutas
        try:
            ruta_relativa_dir = os.path.relpath(root, ruta_raiz)
            if ruta_relativa_dir == '.':
                level = 0
            else:
                level = ruta_relativa_dir.count(os.sep) + 1
        except ValueError:
             level = 0 # Fallback si hay error con path
        
        indent = '    ' * level
        nombre_carpeta = os.path.basename(root)
        if nombre_carpeta == '':
            nombre_carpeta = os.path.basename(ruta_raiz) or ruta_raiz
        
        estructura_arbol.append(f"{indent}[DIR] {nombre_carpeta}/")
        subindent = '    ' * (level + 1)
        
        for f in files:
            archivos_analizados += 1
            ruta_completa = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            
            # 1. Actualizar Mapa
            estructura_arbol.append(f"{subindent}|-- {f}")
            
            # 2. Actualizar Estadísticas
            conteo_formatos[ext] = conteo_formatos.get(ext, 0) + 1
            
            # 3. Procesar PDF (Solo si está habilitado, es código y es texto)
            if generar_pdf and pdf is not None:
                # Verificar si debe incluirse en el PDF
                incluir_en_pdf = False
                if extensiones_codigo is not None:
                    # Solo extensiones específicas de código
                    incluir_en_pdf = ext.lower() in extensiones_codigo or f.lower() in extensiones_codigo
                else:
                    # Incluir todo lo que sea texto y no esté ignorado
                    incluir_en_pdf = ext not in EXTENSIONES_IGNORADAS
                
                if incluir_en_pdf and es_archivo_texto(ruta_completa):
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8', errors='replace') as codigo:
                            contenido = codigo.read()
                            
                            # Agregar al PDF
                            ruta_relativa_archivo = os.path.relpath(ruta_completa, ruta_raiz)
                            pdf.chapter_title(f"Archivo: {ruta_relativa_archivo}")
                            pdf.chapter_body(contenido)
                            archivos_procesados += 1
                            
                            if archivos_analizados % 10 == 0:
                                log(f"Procesando... {archivos_analizados}/{total_archivos} archivos")
                                
                    except Exception as e:
                        log(f"Error leyendo {f}: {e}")

    # Crear carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        try:
            os.makedirs(carpeta_salida)
        except OSError as e:
            log(f"Error creando carpeta de salida: {e}")
            return None
    
    ruta_pdf = os.path.join(carpeta_salida, nombre_pdf) if generar_pdf else None
    ruta_mapa = os.path.join(carpeta_salida, nombre_mapa.replace('.txt', '.pdf')) if generar_mapa else None

    # GUARDAR MAPA PDF
    if generar_mapa and ruta_mapa:
        try:
            pdf_mapa = PDFReporte("Estructura de Directorios")
            pdf_mapa.add_page()
            
            pdf_mapa.seccion("ARBOL DE DIRECTORIOS")
            for linea in estructura_arbol:
                pdf_mapa.linea(linea)
            
            pdf_mapa.ln(5)
            pdf_mapa.seccion("DISTRIBUCION DE ARCHIVOS")
            for ext, count in sorted(conteo_formatos.items()):
                pdf_mapa.linea(f"{ext if ext else 'Sin ext'}: {count} archivos")
            
            pdf_mapa.output(ruta_mapa)
            if os.path.exists(ruta_mapa):
                log(f"Mapa guardado en: {ruta_mapa}")
            else:
                log(f"Error: Mapa no se pudo guardar en {ruta_mapa}")

        except Exception as e:
            log(f"Error guardando mapa PDF: {e}")
    
    # GUARDAR PDF
    if generar_pdf and pdf is not None and ruta_pdf:
        if archivos_procesados == 0:
            log("AVISO: No se encontraron archivos de código compatibles para generar el PDF.")
        else:
            try:
                pdf.output(ruta_pdf)
                if os.path.exists(ruta_pdf):
                    size_kb = os.path.getsize(ruta_pdf) / 1024
                    log(f"PDF guardado en: {ruta_pdf} ({size_kb:.2f} KB)")
                else:
                    log(f"Error CRÍTICO: El archivo PDF no aparece en {ruta_pdf}")
            except Exception as e:
                log(f"Error guardando PDF (¿está abierto?): {e}")
                return None
    
    resultado = {
        'archivos_procesados': archivos_procesados,
        'total_archivos': total_archivos,
        'conteo_formatos': conteo_formatos,
        'ruta_pdf': ruta_pdf,
        'ruta_mapa': ruta_mapa
    }
    
    if archivos_procesados > 0:
        log(f"\n¡Éxito! Procesados {archivos_procesados} archivos de código.")
    else:
        log("\nProceso finalizado. No se generó contenido para el PDF de código.")
        
    return resultado


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        directorio = sys.argv[1]
    else:
        directorio = "."
    
    generar_arbol_y_extraer(directorio)
