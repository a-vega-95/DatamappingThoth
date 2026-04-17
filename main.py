"""
main.py — Punto de entrada de DatamappingThoth Pro
Ejecuta: python main.py (desde la carpeta REFACTORIZACION/)
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path para imports absolutos
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import tkinter as tk
from src.ui.app import DatamappingApp


def main():
    root = tk.Tk()

    # Icono opcional
    icon_path = os.path.join(ROOT, 'icon.ico')
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass

    app = DatamappingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
