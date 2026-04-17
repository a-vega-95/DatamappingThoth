"""
styles.py — Definición centralizada de estilos ttk para DatamappingThoth Pro
Aplica el tema visual de forma consistente en toda la aplicación.
"""

import tkinter as tk
from tkinter import ttk


# ── Paleta de colores ──────────────────────────────────────
AZUL_PRIMARIO  = "#2563EB"   # Botones de acción principal
AZUL_CLARO     = "#EFF6FF"   # Fondos de sección
VERDE_EXITO    = "#16A34A"   # Indicadores de éxito
GRIS_FONDO     = "#F8FAFC"   # Fondo general de la app
GRIS_TEXTO     = "#374151"   # Texto principal
GRIS_SUAVE     = "#E5E7EB"   # Bordes y separadores
ROJO_ERROR     = "#DC2626"   # Mensajes de error
BLANCO         = "#FFFFFF"


def aplicar_estilos(root: tk.Tk) -> ttk.Style:
    """
    Configura y aplica todos los estilos ttk a la ventana raíz.

    Args:
        root: Ventana principal de tkinter.

    Returns:
        Objeto ttk.Style configurado.
    """
    style = ttk.Style(root)

    # Intentar tema claro nativo; fallback a 'clam'
    try:
        style.theme_use('vista')
    except tk.TclError:
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

    # ── Tipografías ──
    style.configure('Title.TLabel',
                    font=('Segoe UI', 16, 'bold'),
                    foreground=AZUL_PRIMARIO)

    style.configure('Subtitle.TLabel',
                    font=('Segoe UI', 10),
                    foreground=GRIS_TEXTO)

    style.configure('Info.TLabel',
                    font=('Segoe UI', 8, 'italic'),
                    foreground='#6B7280')

    # ── Botones ──
    style.configure('Big.TButton',
                    font=('Segoe UI', 11, 'bold'),
                    padding=(18, 10),
                    background=AZUL_PRIMARIO,
                    foreground=BLANCO)

    style.map('Big.TButton',
              background=[('active', '#1D4ED8'), ('disabled', GRIS_SUAVE)],
              foreground=[('disabled', '#9CA3AF')])

    style.configure('Action.TButton',
                    font=('Segoe UI', 9),
                    padding=(10, 6))

    # ── LabelFrames ──
    style.configure('TLabelframe',
                    background=GRIS_FONDO,
                    bordercolor=GRIS_SUAVE)

    style.configure('TLabelframe.Label',
                    font=('Segoe UI', 9, 'bold'),
                    foreground=AZUL_PRIMARIO)

    # ── Entradas ──
    style.configure('TEntry',
                    fieldbackground=BLANCO,
                    font=('Segoe UI', 10))

    # ── Combobox ──
    style.configure('TCombobox',
                    font=('Segoe UI', 10),
                    fieldbackground=BLANCO)

    # ── Progreso ──
    style.configure('TProgressbar',
                    thickness=6,
                    troughcolor=GRIS_SUAVE,
                    background=AZUL_PRIMARIO)

    # ── Notebook (pestañas) ──
    style.configure('TNotebook',
                    background=GRIS_FONDO,
                    tabposition='nw')

    style.configure('TNotebook.Tab',
                    font=('Segoe UI', 10, 'bold'),
                    padding=(14, 8),
                    background=GRIS_SUAVE)

    style.map('TNotebook.Tab',
              background=[('selected', BLANCO)],
              foreground=[('selected', AZUL_PRIMARIO)])

    # ── Checkbutton ──
    style.configure('TCheckbutton',
                    font=('Segoe UI', 9),
                    background=GRIS_FONDO)

    root.configure(bg=GRIS_FONDO)

    return style
