"""
app.py — Interfaz Gráfica Principal de DatamappingThoth Pro
Dos macro-módulos como pestañas independientes en ttk.Notebook:
  1. 🔍 Investigador & Mapeador  (Extractor + Analyzer)
  2. 🔄 Centro de Conversión      (Converter)
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from src.config.settings import EXTENSIONES_CODIGO, APP_NAME, VERSION
from src.core.extractor import generar_auditoria
from src.core.analyzer import generar_informe_datos
from src.core.converter import convertir_archivo, unir_pdfs_wrapper, formatos_soportados_para
from src.ui.styles import aplicar_estilos


class DatamappingApp:
    """Ventana principal con dos pestañas: Investigador y Conversor."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"📁 {APP_NAME} v{VERSION}")
        self.root.geometry("820x720")
        self.root.minsize(750, 600)

        self.style = aplicar_estilos(root)
        self._construir_ui()

    # ──────────────────────────────────────────
    # Construcción inicial de la UI
    # ──────────────────────────────────────────

    def _construir_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Pestaña 1: Investigador & Mapeador
        self.tab_inv = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_inv, text="🔍 Investigador & Mapeador")
        self._ui_investigador(self.tab_inv)

        # Pestaña 2: Centro de Conversión
        self.tab_conv = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_conv, text="🔄 Centro de Conversión")
        self._ui_conversor(self.tab_conv)

    # ══════════════════════════════════════════
    # PESTAÑA 1 — INVESTIGADOR & MAPEADOR
    # ══════════════════════════════════════════

    def _ui_investigador(self, parent: ttk.Frame):
        mf = ttk.Frame(parent, padding=16)
        mf.pack(fill=tk.BOTH, expand=True)

        # Encabezado
        ttk.Label(mf, text="Investigador & Mapeador de Proyectos",
                  style='Title.TLabel').pack(pady=(0, 4))
        ttk.Label(mf,
                  text="Auditoría de código fuente · Mapeo de datos (Head/Tail · Dtypes · Names)",
                  style='Subtitle.TLabel').pack(pady=(0, 14))

        # ── Directorio origen ──
        lf_dir = ttk.LabelFrame(mf, text="Directorio del Proyecto (origen)", padding=10)
        lf_dir.pack(fill=tk.X, pady=(0, 8))
        self.inv_dir_var = tk.StringVar()
        row_dir = ttk.Frame(lf_dir)
        row_dir.pack(fill=tk.X)
        ttk.Entry(row_dir, textvariable=self.inv_dir_var,
                  font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(row_dir, text="📂 Buscar…",
                   command=self._elegir_directorio_inv).pack(side=tk.RIGHT)

        # ── Carpeta de salida ──
        lf_dest = ttk.LabelFrame(mf, text="Carpeta de Salida", padding=10)
        lf_dest.pack(fill=tk.X, pady=(0, 8))
        self.inv_misma_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(lf_dest, text="Usar misma carpeta del proyecto",
                        variable=self.inv_misma_var,
                        command=self._toggle_dest_inv).pack(anchor=tk.W)
        self._dest_frame = ttk.Frame(lf_dest)
        self._dest_frame.pack(fill=tk.X, pady=(4, 0))
        self.inv_dest_var = tk.StringVar()
        self._dest_entry = ttk.Entry(self._dest_frame, textvariable=self.inv_dest_var,
                                     state='disabled', font=('Segoe UI', 10))
        self._dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._dest_btn = ttk.Button(self._dest_frame, text="📁 Seleccionar…",
                                    command=self._elegir_dest_inv, state='disabled')
        self._dest_btn.pack(side=tk.RIGHT)

        # ── Sub-módulo 1-A: Auditoría de código ──
        lf_codigo = ttk.LabelFrame(mf, text="📄 Sub-módulo A — Auditoría de Código Fuente", padding=10)
        lf_codigo.pack(fill=tk.X, pady=(0, 8))

        fila_checks = ttk.Frame(lf_codigo)
        fila_checks.pack(fill=tk.X, pady=(0, 6))
        self.inv_mapa_var   = tk.BooleanVar(value=True)
        self.inv_txt_var    = tk.BooleanVar(value=True)
        self.inv_pdf_var    = tk.BooleanVar(value=False)
        self.inv_solo_var   = tk.BooleanVar(value=True)

        ttk.Checkbutton(fila_checks, text="Árbol de Directorios",
                        variable=self.inv_mapa_var).pack(side=tk.LEFT, padx=(0, 14))
        ttk.Checkbutton(fila_checks, text="Consolidado TXT (IA)",
                        variable=self.inv_txt_var).pack(side=tk.LEFT, padx=(0, 14))
        ttk.Checkbutton(fila_checks, text="Consolidado PDF",
                        variable=self.inv_pdf_var).pack(side=tk.LEFT, padx=(0, 14))
        ttk.Checkbutton(fila_checks, text="Solo código fuente",
                        variable=self.inv_solo_var).pack(side=tk.LEFT)

        fila_nombres = ttk.Frame(lf_codigo)
        fila_nombres.pack(fill=tk.X)
        ttk.Label(fila_nombres, text="Nombre Mapa:", width=14).grid(row=0, column=0, sticky=tk.W)
        self.inv_mapa_nombre = tk.StringVar(value="mapa_proyecto.txt")
        ttk.Entry(fila_nombres, textvariable=self.inv_mapa_nombre,
                  font=('Segoe UI', 9)).grid(row=0, column=1, sticky=tk.EW, padx=(4, 0))
        ttk.Label(fila_nombres, text="Nombre TXT:", width=14).grid(row=1, column=0, sticky=tk.W, pady=(4, 0))
        self.inv_txt_nombre = tk.StringVar(value="Codigo_Fuente_Completo.txt")
        ttk.Entry(fila_nombres, textvariable=self.inv_txt_nombre,
                  font=('Segoe UI', 9)).grid(row=1, column=1, sticky=tk.EW, padx=(4, 0), pady=(4, 0))
        fila_nombres.columnconfigure(1, weight=1)

        # ── Sub-módulo 1-B: Mapeador de datos ──
        lf_datos = ttk.LabelFrame(mf, text="📊 Sub-módulo B — Mapeador de Archivos de Datos", padding=10)
        lf_datos.pack(fill=tk.X, pady=(0, 8))

        self.inv_datos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(lf_datos,
                        text="Analizar CSV · Excel (XLSX/XLS/XLSM) · Parquet  [incluye Head & Tail]",
                        variable=self.inv_datos_var).pack(anchor=tk.W)

        fila_fmt = ttk.Frame(lf_datos)
        fila_fmt.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(fila_fmt, text="Formato informe:", width=16).pack(side=tk.LEFT)
        self.inv_fmt_var = tk.StringVar(value="TXT")
        ttk.Combobox(fila_fmt, textvariable=self.inv_fmt_var,
                     values=["TXT", "PDF", "CSV"],
                     state="readonly", width=8).pack(side=tk.LEFT, padx=(4, 0))

        # ── Botón y progreso ──
        self.inv_btn = ttk.Button(mf, text="🚀 Generar Documentación",
                                  style='Big.TButton', command=self._iniciar_investigacion)
        self.inv_btn.pack(pady=10)
        self.inv_progress = ttk.Progressbar(mf, mode='indeterminate')
        self.inv_progress.pack(fill=tk.X, pady=(0, 8))

        # ── Log ──
        lf_log = ttk.LabelFrame(mf, text="Registro de Actividad", padding=8)
        lf_log.pack(fill=tk.BOTH, expand=True)
        self.inv_log = scrolledtext.ScrolledText(lf_log, height=9,
                                                  font=('Consolas', 9),
                                                  state=tk.DISABLED)
        self.inv_log.pack(fill=tk.BOTH, expand=True)

        self.inv_stats = ttk.Label(mf, text="Esperando…", style='Info.TLabel')
        self.inv_stats.pack(pady=(4, 0))

    # ══════════════════════════════════════════
    # PESTAÑA 2 — CENTRO DE CONVERSIÓN
    # ══════════════════════════════════════════

    def _ui_conversor(self, parent: ttk.Frame):
        mf = ttk.Frame(parent, padding=16)
        mf.pack(fill=tk.BOTH, expand=True)

        ttk.Label(mf, text="Centro de Conversión Universal",
                  style='Title.TLabel').pack(pady=(0, 4))
        ttk.Label(mf,
                  text="PDF · TXT · DOCX · Imágenes · CSV · Excel · JSON · Parquet",
                  style='Subtitle.TLabel').pack(pady=(0, 14))

        # ── Sección: Conversión individual ──
        lf_ind = ttk.LabelFrame(mf, text="🔄 Conversión de Archivo Individual", padding=10)
        lf_ind.pack(fill=tk.X, pady=(0, 8))

        row_f = ttk.Frame(lf_ind)
        row_f.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row_f, text="Archivo origen:", width=16).pack(side=tk.LEFT)
        self.conv_origen_var = tk.StringVar()
        ttk.Entry(row_f, textvariable=self.conv_origen_var,
                  font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X,
                                               expand=True, padx=(4, 8))
        ttk.Button(row_f, text="📄 Seleccionar…",
                   command=self._elegir_origen_conv).pack(side=tk.RIGHT)

        row_fmt = ttk.Frame(lf_ind)
        row_fmt.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row_fmt, text="Convertir a:", width=16).pack(side=tk.LEFT)
        self.conv_fmt_var = tk.StringVar()
        self.conv_combo = ttk.Combobox(row_fmt, textvariable=self.conv_fmt_var,
                                        state="readonly", font=('Segoe UI', 10))
        self.conv_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        self.conv_combo['values'] = ["Selecciona un archivo primero…"]

        row_dest = ttk.Frame(lf_ind)
        row_dest.pack(fill=tk.X)
        ttk.Label(row_dest, text="Carpeta salida:", width=16).pack(side=tk.LEFT)
        self.conv_dest_var = tk.StringVar()
        ttk.Entry(row_dest, textvariable=self.conv_dest_var,
                  font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X,
                                               expand=True, padx=(4, 8))
        ttk.Button(row_dest, text="📁 …",
                   command=self._elegir_dest_conv).pack(side=tk.RIGHT)

        # ── Sección: Unir PDFs ──
        lf_union = ttk.LabelFrame(mf, text="📎 Unir múltiples PDFs en uno solo", padding=10)
        lf_union.pack(fill=tk.X, pady=(0, 8))

        row_pdfs = ttk.Frame(lf_union)
        row_pdfs.pack(fill=tk.X, pady=(0, 6))
        self.union_lista_var = tk.StringVar(value="(ningún archivo seleccionado)")
        ttk.Label(row_pdfs, textvariable=self.union_lista_var,
                  style='Info.TLabel', wraplength=550).pack(side=tk.LEFT,
                                                             fill=tk.X, expand=True)
        ttk.Button(row_pdfs, text="📂 Seleccionar PDFs…",
                   command=self._elegir_pdfs_union).pack(side=tk.RIGHT)

        row_union_dest = ttk.Frame(lf_union)
        row_union_dest.pack(fill=tk.X)
        ttk.Label(row_union_dest, text="Nombre salida:", width=16).pack(side=tk.LEFT)
        self.union_salida_var = tk.StringVar(value="PDFs_Unidos.pdf")
        ttk.Entry(row_union_dest, textvariable=self.union_salida_var,
                  font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X,
                                               expand=True, padx=(4, 8))
        self.union_dest_var = tk.StringVar()
        ttk.Button(row_union_dest, text="📁 Carpeta…",
                   command=self._elegir_dest_union).pack(side=tk.RIGHT)

        # ── Botones de acción ──
        row_btns = ttk.Frame(mf)
        row_btns.pack(pady=8)

        self.conv_btn = ttk.Button(row_btns, text="🔄 Convertir Archivo",
                                    style='Big.TButton',
                                    command=self._iniciar_conversion)
        self.conv_btn.pack(side=tk.LEFT, padx=(0, 12))

        self.union_btn = ttk.Button(row_btns, text="📎 Unir PDFs",
                                     style='Big.TButton',
                                     command=self._iniciar_union)
        self.union_btn.pack(side=tk.LEFT)

        self.conv_progress = ttk.Progressbar(mf, mode='indeterminate')
        self.conv_progress.pack(fill=tk.X, pady=(0, 8))

        lf_log = ttk.LabelFrame(mf, text="Registro de Conversión", padding=8)
        lf_log.pack(fill=tk.BOTH, expand=True)
        self.conv_log = scrolledtext.ScrolledText(lf_log, height=10,
                                                   font=('Consolas', 9),
                                                   state=tk.DISABLED)
        self.conv_log.pack(fill=tk.BOTH, expand=True)

        # Lista interna de PDFs para unir
        self._pdfs_a_unir: list = []

    # ──────────────────────────────────────────
    # Helpers UI — Investigador
    # ──────────────────────────────────────────

    def _elegir_directorio_inv(self):
        d = filedialog.askdirectory(title="Selecciona la carpeta del proyecto")
        if d:
            self.inv_dir_var.set(d)
            self._log_inv(f"Directorio seleccionado: {d}")

    def _toggle_dest_inv(self):
        estado = 'disabled' if self.inv_misma_var.get() else 'normal'
        self._dest_entry.configure(state=estado)
        self._dest_btn.configure(state=estado)

    def _elegir_dest_inv(self):
        d = filedialog.askdirectory(title="Selecciona carpeta de salida")
        if d:
            self.inv_dest_var.set(d)

    def _log_inv(self, msg: str):
        self.inv_log.config(state=tk.NORMAL)
        self.inv_log.insert(tk.END, msg + "\n")
        self.inv_log.see(tk.END)
        self.inv_log.config(state=tk.DISABLED)

    # ──────────────────────────────────────────
    # Lógica — Investigador
    # ──────────────────────────────────────────

    def _iniciar_investigacion(self):
        directorio = self.inv_dir_var.get().strip()
        if not directorio or not os.path.isdir(directorio):
            messagebox.showwarning("Aviso", "Selecciona un directorio válido primero.")
            return
        if not any([self.inv_mapa_var.get(), self.inv_txt_var.get(),
                    self.inv_pdf_var.get(), self.inv_datos_var.get()]):
            messagebox.showwarning("Aviso", "Selecciona al menos una opción.")
            return

        self.inv_btn.config(state=tk.DISABLED)
        self.inv_progress.start(10)
        self.inv_log.config(state=tk.NORMAL)
        self.inv_log.delete(1.0, tk.END)
        self.inv_log.config(state=tk.DISABLED)

        threading.Thread(target=self._ejecutar_investigacion, daemon=True).start()

    def _ejecutar_investigacion(self):
        directorio  = self.inv_dir_var.get().strip()
        carpeta_sal = (None if self.inv_misma_var.get()
                       else self.inv_dest_var.get().strip() or None)
        generar_mapa  = self.inv_mapa_var.get()
        generar_txt   = self.inv_txt_var.get()
        generar_pdf   = self.inv_pdf_var.get()
        solo_codigo   = self.inv_solo_var.get()
        generar_datos = self.inv_datos_var.get()
        fmt_datos     = self.inv_fmt_var.get()

        ext_custom = EXTENSIONES_CODIGO if solo_codigo else None

        def cb(msg):
            self.root.after(0, lambda m=msg: self._log_inv(m))

        resultado = resultado_datos = None

        try:
            if generar_mapa or generar_txt or generar_pdf:
                resultado = generar_auditoria(
                    ruta_raiz=directorio,
                    carpeta_salida=carpeta_sal,
                    nombre_mapa=self.inv_mapa_nombre.get() or "mapa_proyecto.txt",
                    nombre_txt=self.inv_txt_nombre.get() or "Codigo_Fuente_Completo.txt",
                    generar_mapa=generar_mapa,
                    generar_txt=generar_txt,
                    generar_pdf=generar_pdf,
                    extensiones_custom=ext_custom,
                    callback=cb,
                )

            if generar_datos:
                cb("\n📊 Iniciando análisis de archivos de datos…")
                resultado_datos = generar_informe_datos(
                    ruta_directorio=directorio,
                    carpeta_salida=carpeta_sal,
                    nombre_informe="mapa_datos",
                    formato=fmt_datos.lower(),
                    callback=cb,
                )

            self.root.after(0, lambda: self._mostrar_resultado_inv(resultado, resultado_datos))

        except Exception as exc:
            self.root.after(0, lambda e=exc: (
                self._log_inv(f"❌ Error: {e}"),
                messagebox.showerror("Error", str(e))
            ))
        finally:
            self.root.after(0, self._finalizar_inv)

    def _mostrar_resultado_inv(self, resultado, resultado_datos):
        msgs = []
        if resultado:
            total = resultado.get('total_archivos', 0)
            proc  = resultado.get('archivos_procesados', 0)
            self.inv_stats.config(text=f"✅ {proc} archivos de código procesados de {total} encontrados")

            formatos = resultado.get('conteo_formatos', {})
            if formatos:
                top = sorted(formatos.items(), key=lambda x: x[1], reverse=True)[:5]
                self._log_inv("\n📊 Top 5 extensiones encontradas:")
                for ext_k, cnt in top:
                    self._log_inv(f"   {ext_k or '(sin ext)'}: {cnt}")

            self._log_inv("\n📄 Archivos generados:")
            for clave, etiqueta in [('ruta_mapa', 'Mapa'),
                                     ('ruta_txt', 'TXT Código'),
                                     ('ruta_pdf', 'PDF Código')]:
                ruta = resultado.get(clave)
                if ruta:
                    self._log_inv(f"   {etiqueta}: {ruta}")
                    msgs.append(f"{etiqueta}: {os.path.basename(ruta)}")

        if resultado_datos:
            n = resultado_datos.get('archivos_analizados', 0)
            ruta_rep = resultado_datos.get('ruta_reporte')
            self._log_inv(f"\n📊 Datos analizados: {n} archivos")
            if ruta_rep:
                self._log_inv(f"   Informe: {ruta_rep}")
                msgs.append(f"Informe Datos: {os.path.basename(ruta_rep)}")

        if msgs:
            messagebox.showinfo("¡Completado!",
                                "Documentación generada.\n\n" + "\n".join(msgs))

    def _finalizar_inv(self):
        self.inv_progress.stop()
        self.inv_btn.config(state=tk.NORMAL)

    # ──────────────────────────────────────────
    # Helpers UI — Conversor
    # ──────────────────────────────────────────

    def _elegir_origen_conv(self):
        archivo = filedialog.askopenfilename(title="Selecciona el archivo a convertir")
        if archivo:
            self.conv_origen_var.set(archivo)
            self.conv_dest_var.set(os.path.dirname(archivo))
            ext = os.path.splitext(archivo)[1].lower()
            opciones = formatos_soportados_para(ext)
            if opciones:
                self.conv_combo['values'] = [o.upper() for o in opciones]
                self.conv_combo.current(0)
            else:
                self.conv_combo['values'] = ["Formato no soportado"]
                self.conv_combo.set("Formato no soportado")

    def _elegir_dest_conv(self):
        d = filedialog.askdirectory(title="Carpeta de salida")
        if d:
            self.conv_dest_var.set(d)

    def _elegir_pdfs_union(self):
        archivos = filedialog.askopenfilenames(
            title="Selecciona los PDFs a unir",
            filetypes=[("PDF", "*.pdf")]
        )
        if archivos:
            self._pdfs_a_unir = list(archivos)
            n = len(self._pdfs_a_unir)
            self.union_lista_var.set(f"{n} PDF(s) seleccionados: " +
                                     ", ".join(os.path.basename(p) for p in self._pdfs_a_unir[:3]) +
                                     ("…" if n > 3 else ""))

    def _elegir_dest_union(self):
        d = filedialog.askdirectory(title="Carpeta de salida para PDF unido")
        if d:
            self.union_dest_var.set(d)

    def _log_conv(self, msg: str):
        self.conv_log.config(state=tk.NORMAL)
        self.conv_log.insert(tk.END, msg + "\n")
        self.conv_log.see(tk.END)
        self.conv_log.config(state=tk.DISABLED)

    # ──────────────────────────────────────────
    # Lógica — Conversor Individual
    # ──────────────────────────────────────────

    def _iniciar_conversion(self):
        archivo = self.conv_origen_var.get()
        fmt     = self.conv_fmt_var.get()
        carpeta = self.conv_dest_var.get()
        if not archivo or not fmt or "Selecciona" in fmt or "soportado" in fmt:
            messagebox.showwarning("Aviso", "Completa todos los campos.")
            return

        self.conv_btn.config(state=tk.DISABLED)
        self.union_btn.config(state=tk.DISABLED)
        self.conv_progress.start(10)
        self.conv_log.config(state=tk.NORMAL)
        self.conv_log.delete(1.0, tk.END)
        self.conv_log.config(state=tk.DISABLED)

        threading.Thread(target=self._ejecutar_conversion, daemon=True).start()

    def _ejecutar_conversion(self):
        archivo = self.conv_origen_var.get()
        fmt     = self.conv_fmt_var.get().lower()
        carpeta = self.conv_dest_var.get()

        def cb(msg):
            self.root.after(0, lambda m=msg: self._log_conv(m))

        try:
            ruta_final = convertir_archivo(archivo, fmt, carpeta, cb)
            self.root.after(0, lambda: (
                self._log_conv(f"\n✅ Conversión completada: {ruta_final}"),
                messagebox.showinfo("Éxito", f"Archivo convertido:\n{os.path.basename(ruta_final)}")
            ))
        except Exception as exc:
            self.root.after(0, lambda e=exc: (
                self._log_conv(f"❌ Error: {e}"),
                messagebox.showerror("Error", str(e))
            ))
        finally:
            self.root.after(0, self._finalizar_conv)

    # ──────────────────────────────────────────
    # Lógica — Unión de PDFs
    # ──────────────────────────────────────────

    def _iniciar_union(self):
        if not self._pdfs_a_unir:
            messagebox.showwarning("Aviso", "Selecciona al menos un PDF.")
            return
        carpeta = self.union_dest_var.get() or os.path.dirname(self._pdfs_a_unir[0])
        if not carpeta:
            messagebox.showwarning("Aviso", "Selecciona una carpeta de destino.")
            return

        self.conv_btn.config(state=tk.DISABLED)
        self.union_btn.config(state=tk.DISABLED)
        self.conv_progress.start(10)
        self.conv_log.config(state=tk.NORMAL)
        self.conv_log.delete(1.0, tk.END)
        self.conv_log.config(state=tk.DISABLED)

        threading.Thread(target=self._ejecutar_union, daemon=True).start()

    def _ejecutar_union(self):
        nombre_sal = self.union_salida_var.get() or "PDFs_Unidos.pdf"
        carpeta    = self.union_dest_var.get() or os.path.dirname(self._pdfs_a_unir[0])
        ruta_sal   = os.path.join(carpeta, nombre_sal)

        def cb(msg):
            self.root.after(0, lambda m=msg: self._log_conv(m))

        try:
            ruta_final = unir_pdfs_wrapper(self._pdfs_a_unir, ruta_sal, cb)
            self.root.after(0, lambda: (
                self._log_conv(f"\n✅ PDFs unidos: {ruta_final}"),
                messagebox.showinfo("Éxito", f"PDF creado:\n{os.path.basename(ruta_final)}")
            ))
        except Exception as exc:
            self.root.after(0, lambda e=exc: (
                self._log_conv(f"❌ Error: {e}"),
                messagebox.showerror("Error", str(e))
            ))
        finally:
            self.root.after(0, self._finalizar_conv)

    def _finalizar_conv(self):
        self.conv_progress.stop()
        self.conv_btn.config(state=tk.NORMAL)
        self.union_btn.config(state=tk.NORMAL)
