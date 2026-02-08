"""
Interfaz Gráfica para el Extractor de Código Fuente
Aplicación con GUI usando tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os

from extractor import generar_arbol_y_extraer, EXTENSIONES_CODIGO
from analizador_datos import generar_reporte_datos


class InvestigadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📁 Investigador de Proyectos")
        self.root.geometry("750x650")
        self.root.minsize(700, 550)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Segoe UI', 10))
        self.style.configure('Big.TButton', font=('Segoe UI', 11), padding=10)
        
        self.crear_widgets()
        
    def crear_widgets(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Investigador de Proyectos", 
                          style='Title.TLabel')
        titulo.pack(pady=(0, 5))
        
        subtitulo = ttk.Label(main_frame, 
                             text="Genera mapa de directorios, estadísticas y PDF de código fuente",
                             style='Subtitle.TLabel')
        subtitulo.pack(pady=(0, 20))
        
        # Frame para selección de directorio
        dir_frame = ttk.LabelFrame(main_frame, text="Directorio del Proyecto (origen)", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.directorio_var = tk.StringVar()
        
        entry_frame = ttk.Frame(dir_frame)
        entry_frame.pack(fill=tk.X)
        
        self.dir_entry = ttk.Entry(entry_frame, textvariable=self.directorio_var, 
                                   font=('Segoe UI', 10))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_buscar = ttk.Button(entry_frame, text="📂 Buscar...", 
                               command=self.seleccionar_directorio)
        btn_buscar.pack(side=tk.RIGHT)
        
        # Frame para carpeta de destino
        destino_frame = ttk.LabelFrame(main_frame, text="Carpeta de Salida (destino)", padding="10")
        destino_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.destino_var = tk.StringVar()
        self.usar_misma_carpeta_var = tk.BooleanVar(value=True)
        
        check_misma = ttk.Checkbutton(destino_frame, 
                                      text="Usar misma carpeta del proyecto",
                                      variable=self.usar_misma_carpeta_var,
                                      command=self.toggle_carpeta_destino)
        check_misma.pack(anchor=tk.W)
        
        self.destino_entry_frame = ttk.Frame(destino_frame)
        self.destino_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.destino_entry = ttk.Entry(self.destino_entry_frame, textvariable=self.destino_var, 
                                       font=('Segoe UI', 10), state='disabled')
        self.destino_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.btn_destino = ttk.Button(self.destino_entry_frame, text="📁 Seleccionar/Crear...", 
                                      command=self.seleccionar_destino, state='disabled')
        self.btn_destino.pack(side=tk.RIGHT)
        
        # Frame para nombres de archivo
        nombres_frame = ttk.LabelFrame(main_frame, text="Nombres de Archivos de Salida", 
                                       padding="10")
        nombres_frame.pack(fill=tk.X, pady=(0, 15))
        
        # PDF
        pdf_frame = ttk.Frame(nombres_frame)
        pdf_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(pdf_frame, text="Nombre PDF:", width=15).pack(side=tk.LEFT)
        self.pdf_var = tk.StringVar(value="Codigo_Fuente_Completo.pdf")
        ttk.Entry(pdf_frame, textvariable=self.pdf_var, 
                  font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Mapa
        mapa_frame = ttk.Frame(nombres_frame)
        mapa_frame.pack(fill=tk.X)
        ttk.Label(mapa_frame, text="Nombre Mapa:", width=15).pack(side=tk.LEFT)
        self.mapa_var = tk.StringVar(value="mapa_proyecto.pdf")
        ttk.Entry(mapa_frame, textvariable=self.mapa_var,
                  font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame para opciones de generación
        opciones_frame = ttk.LabelFrame(main_frame, text="Opciones de Generación", 
                                        padding="10")
        opciones_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Checkboxes para elegir qué generar
        checks_frame = ttk.Frame(opciones_frame)
        checks_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.generar_mapa_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(checks_frame, text="Generar Mapa de Directorios (.txt)", 
                       variable=self.generar_mapa_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.generar_pdf_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(checks_frame, text="Generar PDF de Código Fuente", 
                       variable=self.generar_pdf_var,
                       command=self.toggle_opciones_pdf).pack(side=tk.LEFT)
        
        # Frame para opciones de PDF (solo código)
        self.pdf_opciones_frame = ttk.Frame(opciones_frame)
        self.pdf_opciones_frame.pack(fill=tk.X)
        
        self.solo_codigo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.pdf_opciones_frame, 
                       text="Solo archivos de código fuente (recomendado)", 
                       variable=self.solo_codigo_var).pack(anchor=tk.W)
        
        # Mostrar extensiones que se incluirán
        ext_label = ttk.Label(self.pdf_opciones_frame, 
                             text="Extensiones: .py, .js, .ts, .java, .c, .cpp, .html, .css, .json, etc.",
                             font=('Segoe UI', 8), foreground='gray')
        ext_label.pack(anchor=tk.W, padx=(20, 0))
        
        # Separador
        ttk.Separator(opciones_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Opción para mapeo de datos
        datos_frame = ttk.Frame(opciones_frame)
        datos_frame.pack(fill=tk.X)
        
        self.generar_mapa_datos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(datos_frame, 
                       text="Generar Mapa de Archivos de Datos (CSV, Excel, Parquet)", 
                       variable=self.generar_mapa_datos_var).pack(anchor=tk.W)
        
        datos_info = ttk.Label(datos_frame, 
                              text="Analiza estructura: columnas, tipos de datos y muestra de valores",
                              font=('Segoe UI', 8), foreground='gray')
        datos_info.pack(anchor=tk.W, padx=(20, 0))
        
        # Botón principal
        self.btn_generar = ttk.Button(main_frame, text="🚀 Generar Documentación",
                                      style='Big.TButton', command=self.iniciar_proceso)
        self.btn_generar.pack(pady=15)
        
        # Barra de progreso
        self.progreso = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progreso.pack(fill=tk.X, pady=(0, 10))
        
        # Área de log
        log_frame = ttk.LabelFrame(main_frame, text="Registro de Actividad", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, 
                                                   font=('Consolas', 9),
                                                   state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame de estadísticas
        self.stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding="10")
        self.stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(self.stats_frame, text="Esperando ejecución...")
        self.stats_label.pack()
        
    def seleccionar_directorio(self):
        directorio = filedialog.askdirectory(title="Selecciona la carpeta del proyecto")
        if directorio:
            self.directorio_var.set(directorio)
            self.log("Directorio seleccionado: " + directorio)
    
    def toggle_carpeta_destino(self):
        """Habilitar/deshabilitar selección de carpeta de destino"""
        if self.usar_misma_carpeta_var.get():
            self.destino_entry.configure(state='disabled')
            self.btn_destino.configure(state='disabled')
            self.destino_var.set("")
        else:
            self.destino_entry.configure(state='normal')
            self.btn_destino.configure(state='normal')
    
    def seleccionar_destino(self):
        """Seleccionar o crear carpeta de destino"""
        # Primero intentar seleccionar carpeta existente
        directorio = filedialog.askdirectory(title="Selecciona o crea la carpeta de destino")
        if directorio:
            self.destino_var.set(directorio)
            self.log("Carpeta de destino: " + directorio)
    
    def toggle_opciones_pdf(self):
        """Habilitar/deshabilitar opciones de PDF según el checkbox"""
        if self.generar_pdf_var.get():
            for child in self.pdf_opciones_frame.winfo_children():
                child.configure(state='normal')
        else:
            for child in self.pdf_opciones_frame.winfo_children():
                try:
                    child.configure(state='disabled')
                except:
                    pass
            
    def log(self, mensaje):
        """Agregar mensaje al área de log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, mensaje + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def iniciar_proceso(self):
        directorio = self.directorio_var.get().strip()
        
        if not directorio:
            messagebox.showwarning("Aviso", "Por favor selecciona un directorio primero.")
            return
            
        if not os.path.isdir(directorio):
            messagebox.showerror("Error", "El directorio seleccionado no existe.")
            return
        
        if not self.generar_mapa_var.get() and not self.generar_pdf_var.get() and not self.generar_mapa_datos_var.get():
            messagebox.showwarning("Aviso", "Debes seleccionar al menos una opción de generación.")
            return
        
        # Deshabilitar botón y mostrar progreso
        self.btn_generar.config(state=tk.DISABLED)
        self.progreso.start(10)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Ejecutar en hilo separado para no bloquear la UI
        thread = threading.Thread(target=self.ejecutar_extraccion, daemon=True)
        thread.start()
        
    def ejecutar_extraccion(self):
        directorio = self.directorio_var.get().strip()
        nombre_pdf = self.pdf_var.get().strip() or "Codigo_Fuente_Completo.pdf"
        nombre_mapa = self.mapa_var.get().strip() or "mapa_proyecto.txt"
        generar_mapa = self.generar_mapa_var.get()
        generar_pdf = self.generar_pdf_var.get()
        solo_codigo = self.solo_codigo_var.get()
        generar_mapa_datos = self.generar_mapa_datos_var.get()
        
        # Determinar carpeta de salida
        if self.usar_misma_carpeta_var.get():
            carpeta_salida = None  # Usará la misma carpeta del proyecto
        else:
            carpeta_salida = self.destino_var.get().strip() or None
        
        # Determinar extensiones a usar
        extensiones = EXTENSIONES_CODIGO if (generar_pdf and solo_codigo) else None
        
        def callback_log(mensaje):
            self.root.after(0, lambda: self.log(mensaje))
        
        resultado = None
        resultado_datos = None
        
        try:
            # Generar mapa de directorios y/o PDF de código
            if generar_mapa or generar_pdf:
                resultado = generar_arbol_y_extraer(
                    directorio,
                    nombre_pdf=nombre_pdf,
                    nombre_mapa=nombre_mapa,
                    callback=callback_log,
                    generar_mapa=generar_mapa,
                    generar_pdf=generar_pdf,
                    extensiones_codigo=extensiones,
                    carpeta_salida=carpeta_salida
                )
            
            # Generar mapa de archivos de datos
            if generar_mapa_datos:
                self.root.after(0, lambda: self.log("\n📊 Iniciando análisis de archivos de datos..."))
                resultado_datos = generar_reporte_datos(
                    directorio,
                    archivo_salida="mapa_datos.txt",
                    carpeta_salida=carpeta_salida,
                    callback=callback_log
                )
            
            # Mostrar resultados
            if resultado or resultado_datos:
                self.root.after(0, lambda: self.mostrar_resultado(resultado, resultado_datos))
            else:
                self.root.after(0, lambda: self.log("❌ Error durante el proceso"))
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self.finalizar_proceso)
            
    def mostrar_resultado(self, resultado=None, resultado_datos=None):
        """Mostrar estadísticas del resultado"""
        mensajes = []
        
        # Resultados de código/estructura
        if resultado:
            stats_text = (f"✅ Archivos procesados: {resultado['archivos_procesados']} / "
                         f"{resultado['total_archivos']}")
            self.stats_label.config(text=stats_text)
            
            # Mostrar formatos encontrados
            formatos = resultado.get('conteo_formatos', {})
            if formatos:
                top_formatos = sorted(formatos.items(), key=lambda x: x[1], reverse=True)[:5]
                self.log("\n📊 Top 5 tipos de archivo:")
                for ext, count in top_formatos:
                    ext_name = ext if ext else "(sin extensión)"
                    self.log(f"   {ext_name}: {count} archivos")
            
            self.log(f"\n📄 Archivos generados:")
            
            if resultado.get('ruta_pdf'):
                self.log(f"   PDF: {resultado['ruta_pdf']}")
                mensajes.append(f"PDF: {resultado['ruta_pdf']}")
            if resultado.get('ruta_mapa'):
                self.log(f"   Mapa: {resultado['ruta_mapa']}")
                mensajes.append(f"Mapa: {resultado['ruta_mapa']}")
        
        # Resultados de datos
        if resultado_datos:
            self.log(f"\n📊 Análisis de datos completado:")
            self.log(f"   Archivos analizados: {resultado_datos.get('archivos_analizados', 0)}")
            if resultado_datos.get('ruta_reporte'):
                self.log(f"   Reporte: {resultado_datos['ruta_reporte']}")
                mensajes.append(f"Mapa Datos: {resultado_datos['ruta_reporte']}")
        
        if mensajes:
            messagebox.showinfo("¡Completado!", 
                               f"Documentación generada exitosamente.\n\n" + "\n".join(mensajes))
        else:
            self.stats_label.config(text="Proceso completado")
        
    def finalizar_proceso(self):
        """Restaurar estado de la UI después del proceso"""
        self.progreso.stop()
        self.btn_generar.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    
    # Intentar usar icono si está disponible
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = InvestigadorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
