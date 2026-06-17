import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import calendar
from datetime import datetime
import os
import easyocr

# Configuración visual de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ==========================================
# GESTIÓN DE LA BASE DE DATOS LOCAL
# ==========================================
class WIN_Database:
    def __init__(self):
        self.conn = sqlite3.connect("tareas.db")
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    def crear_tablas(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                tipo_actividad TEXT,
                descripcion TEXT,
                materia TEXT,
                vencimiento TEXT,
                estado TEXT
            )
        """)
        self.conn.commit()

    def insertar_tarea(self, fecha, tipo_actividad, descripcion, materia, vencimiento, estado):
        self.cursor.execute("""
            INSERT INTO actividades (fecha, tipo_actividad, descripcion, materia, vencimiento, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (fecha, tipo_actividad, descripcion, materia, vencimiento, estado))
        self.conn.commit()

    def obtener_todas_tareas(self):
        self.cursor.execute("SELECT * FROM actividades")
        return self.cursor.fetchall()
    
    def eliminar_tarea_db(self, id_tarea):
        """Borra la actividad por completo de la base de datos usando su ID"""
        self.cursor.execute("DELETE FROM actividades WHERE id = ?", (id_tarea,))
        self.conn.commit()

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass

# ==========================================
# APLICACIÓN PRINCIPAL (WIN)
# ==========================================
class AppWIN(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("W.I.N. - Work Info Notifier")
        self.geometry("1150x780")
        self.resizable(True, True)

        self.db = WIN_Database()

        # Variables para almacenar lo extraído por el OCR temporalmente
        self.ocr_tipo = "Tarea"

        # Configurar grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ==========================================
        # BARRA LATERAL IZQUIERDA
        # ==========================================
        self.barra_lateral = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#121212")
        self.barra_lateral.grid(row=1, column=0, sticky="nsew")
        self.barra_lateral.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.barra_lateral, text="W.I.N. SYSTEM", font=ctk.CTkFont(size=22, weight="bold"), text_color="#C8102E")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        self.btn_dashboard = ctk.CTkButton(self.barra_lateral, text="🏠 Dashboard Académico", font=ctk.CTkFont(size=14, weight="bold"),
                                            fg_color="#2B2B2B", hover_color="#3A3A3A", height=45, corner_radius=10,
                                            command=lambda: self.cambiar_pantalla("Dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=8, sticky="ew")

        self.btn_ingesta = ctk.CTkButton(self.barra_lateral, text="📥 Ingesta (OCR)", font=ctk.CTkFont(size=14, weight="bold"),
                                            fg_color="transparent", hover_color="#2B2B2B", height=45, corner_radius=10,
                                            command=lambda: self.cambiar_pantalla("Ingesta"))
        self.btn_ingesta.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        self.btn_calendario = ctk.CTkButton(self.barra_lateral, text="📆 Mi Calendario", font=ctk.CTkFont(size=14, weight="bold"),
                                            fg_color="transparent", hover_color="#2B2B2B", height=45, corner_radius=10,
                                            command=lambda: self.cambiar_pantalla("Calendario"))
        self.btn_calendario.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        self.user_label = ctk.CTkLabel(self.barra_lateral, text="Sesión: Fernando Alania", font=ctk.CTkFont(size=12), text_color="#888888")
        self.user_label.grid(row=6, column=0, padx=20, pady=25)

        # ==========================================
        # CABECERA ROJA UTP
        # ==========================================
        self.cabecera = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#C8102E")
        self.cabecera.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.cabecera.grid_columnconfigure(0, weight=1)

        lbl_nav = ctk.CTkLabel(self.cabecera, text="Configuración | Cuenta | Calendario", font=ctk.CTkFont(size=13), text_color="white")
        lbl_nav.grid(row=0, column=1, padx=30, pady=20)

        lbl_utp = ctk.CTkLabel(self.cabecera, text="UTP", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        lbl_utp.grid(row=0, column=2, padx=(0, 30), pady=20)

        # ==========================================
        # CONTENEDORES DE PANTALLAS
        # ==========================================
        self.pantalla_dashboard = ctk.CTkFrame(self, corner_radius=15, fg_color="#1A1A1A")
        self.pantalla_ingesta = ctk.CTkFrame(self, corner_radius=15, fg_color="#1A1A1A")
        self.pantalla_calendario = ctk.CTkFrame(self, corner_radius=15, fg_color="#1A1A1A")

        self.inicializar_dashboard()
        self.inicializar_ingesta()
        self.inicializar_calendario()

        self.cambiar_pantalla("Dashboard")

    def cambiar_pantalla(self, nombre):
        self.pantalla_dashboard.grid_forget()
        self.pantalla_ingesta.grid_forget()
        self.pantalla_calendario.grid_forget()

        self.btn_dashboard.configure(fg_color="transparent")
        self.btn_ingesta.configure(fg_color="transparent")
        self.btn_calendario.configure(fg_color="transparent")

        if nombre == "Dashboard":
            self.pantalla_dashboard.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
            self.btn_dashboard.configure(fg_color="#2B2B2B")
            self.actualizar_lista_dashboard()
        elif nombre == "Ingesta":
            self.pantalla_ingesta.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
            self.btn_ingesta.configure(fg_color="#2B2B2B")
        elif nombre == "Calendario":
            self.pantalla_calendario.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
            self.btn_calendario.configure(fg_color="#2B2B2B")
            self.renderizar_mes_calendario(2026, 6)

    # ==========================================
    # PANTALLA: DASHBOARD ACADÉMICO
    # ==========================================
    def inicializar_dashboard(self):
        self.pantalla_dashboard.grid_columnconfigure(0, weight=1)
        self.pantalla_dashboard.grid_rowconfigure(2, weight=1)

        lbl_titulo = ctk.CTkLabel(self.pantalla_dashboard, text="¿QUÉ TENEMOS EL DIA DE HOY?", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        lbl_titulo.grid(row=0, column=0, pady=(25, 10), padx=30, sticky="w")

        self.seccion_agregar = ctk.CTkFrame(self.pantalla_dashboard, fg_color="transparent")
        self.seccion_agregar.grid(row=1, column=0, pady=5, padx=30, sticky="w")

        lbl_agregar = ctk.CTkLabel(self.seccion_agregar, text="AGREGAR TAREA", font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        lbl_agregar.pack(side="left")

        btn_mas = ctk.CTkButton(self.seccion_agregar, text="+", font=ctk.CTkFont(size=22, weight="bold"),
                                fg_color="#107C41", hover_color="#0B592E", width=40, height=40, corner_radius=20,
                                command=self.abrir_ventana_manual)
        btn_mas.pack(side="left", padx=15)

        # Contenedor scrollable principal simplificado a una sola columna expandible para las tarjetas
        self.container_lista_hoy = ctk.CTkScrollableFrame(self.pantalla_dashboard, fg_color="#242424", border_width=1, border_color="#333333", corner_radius=15)
        self.container_lista_hoy.grid(row=2, column=0, pady=15, padx=30, sticky="nsew")
        self.container_lista_hoy.grid_columnconfigure(0, weight=1)

    def actualizar_lista_dashboard(self):
        # 1. Limpiamos por completo el panel
        for widget in self.container_lista_hoy.winfo_children():
            widget.destroy()

        # 2. Modificamos la consulta directamente aquí para traer SOLO las 3 tareas más cercanas que estén pendientes
        self.db.cursor.execute("""
            SELECT id, tipo_actividad, descripcion, materia, vencimiento 
            FROM actividades 
            WHERE estado = 'Pendiente' 
            ORDER BY vencimiento ASC 
            LIMIT 3
        """)
        tareas = self.db.cursor.fetchall()

        # Busca este bloque donde dice si no hay tareas y cambia 'calendar' por 'slant'
        if not tareas:
            lbl_vacio = ctk.CTkLabel(
                self.container_lista_hoy, 
                text="✨ ¡Felicidades! No registras tareas pendientes cercanas.", 
                font=ctk.CTkFont(size=14, slant="italic"), # <-- AQUÍ QUEDA CORREGIDO
                text_color="gray"
            )
            lbl_vacio.pack(pady=50)
            return

        # 3. Dibujamos las 3 tarjetas de forma compacta (una debajo de la otra usando pack)
        for t in tareas:
            id_actividad, tipo_actividad, descripcion, materia, vencimiento = t
            icono = "💬" if tipo_actividad.lower() == "foro" else "📄"

            # Tarjeta oscura contenedora
            tarjeta = ctk.CTkFrame(self.container_lista_hoy, fg_color="#1F1F1F", corner_radius=10)
            tarjeta.pack(fill="x", padx=15, pady=8, ipady=4)

            # Contenedor interno izquierdo para organizar los textos
            info_frame = ctk.CTkFrame(tarjeta, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=8)

            # Nombre de la materia/curso (Arriba en azul)
            lbl_mat = ctk.CTkLabel(info_frame, text=materia.upper(), font=ctk.CTkFont(size=11, weight="bold"), text_color="#3B8ED0", anchor="w")
            lbl_mat.pack(fill="x")

            # Descripción de la tarea (Centro)
            lbl_desc = ctk.CTkLabel(info_frame, text=f"{icono}  {descripcion}", font=ctk.CTkFont(size=14, weight="bold"), text_color="white", anchor="w")
            lbl_desc.pack(fill="x", pady=2)

            # Fecha de vencimiento (Abajo en naranja)
            lbl_venc = ctk.CTkLabel(info_frame, text=f"Vence: {vencimiento}", font=ctk.CTkFont(size=11), text_color="#FF9F43", anchor="w")
            lbl_venc.pack(fill="x")

            # Botón verde "✓ Resuelto" alineado a la derecha de la tarjeta
            btn_resolver = ctk.CTkButton(
                tarjeta, 
                text="✓ Resuelto", 
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#28C76F", 
                hover_color="#1E9451", 
                width=90, 
                height=32, 
                corner_radius=6,
                command=lambda id_act=id_actividad: self.resolver_tarea_interfaz(id_act)
            )
            btn_resolver.pack(side="right", padx=20, pady=10)
    # ==========================================
    # PANTALLA: INGESTA CORREGIDA (EDITABLE)
    # ==========================================
    def inicializar_ingesta(self):
        self.pantalla_ingesta.grid_columnconfigure(0, weight=1)
        
        lbl_ingesta_t = ctk.CTkLabel(self.pantalla_ingesta, text="Panel de Ingesta Inteligente", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        lbl_ingesta_t.pack(pady=(25, 5), padx=40, anchor="w")
        
        btn_cargar = ctk.CTkButton(self.pantalla_ingesta, text="START (Escanear Captura)", font=ctk.CTkFont(size=15, weight="bold"),
                                   fg_color="#C8102E", hover_color="#960B22", height=45, corner_radius=10,
                                   command=self.procesar_ocr_real)
        btn_cargar.pack(pady=15, padx=40, fill="x")

        # --- FORMULARIO DE CORRECCIÓN EN VIVO ---
        self.frame_edit = ctk.CTkFrame(self.pantalla_ingesta, fg_color="#242424", border_width=1, border_color="#333333", corner_radius=12)
        self.frame_edit.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(self.frame_edit, text="Validar y Corregir Datos Extraídos:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#aaaaaa").pack(pady=10, padx=20, anchor="w")

        # Campo: Descripción
        ctk.CTkLabel(self.frame_edit, text="Actividad / Descripción:", text_color="white").pack(padx=20, anchor="w")
        self.ent_ocr_desc = ctk.CTkEntry(self.frame_edit, fg_color="#1A1A1A", width=500)
        self.ent_ocr_desc.pack(pady=(2, 10), padx=20, fill="x")

        # Campo: Materia
        ctk.CTkLabel(self.frame_edit, text="Materia / Curso:", text_color="white").pack(padx=20, anchor="w")
        self.ent_ocr_mat = ctk.CTkEntry(self.frame_edit, fg_color="#1A1A1A")
        self.ent_ocr_mat.pack(pady=(2, 10), padx=20, fill="x")

        # Campo: Vencimiento
        ctk.CTkLabel(self.frame_edit, text="Vencimiento (Formato obligatorio: DD/MM/YYYY):", text_color="white").pack(padx=20, anchor="w")
        self.ent_ocr_venc = ctk.CTkEntry(self.frame_edit, fg_color="#1A1A1A")
        self.ent_ocr_venc.pack(pady=(2, 15), padx=20, fill="x")

        # Botón para confirmar y guardar localmente
        self.btn_sincronizar = ctk.CTkButton(self.pantalla_ingesta, text="💾 Sincronizar y Guardar Localmente", font=ctk.CTkFont(size=15, weight="bold"),
                                             fg_color="#107C41", hover_color="#0B592E", height=45, corner_radius=10,
                                             command=self.guardar_datos_corregidos)
        self.btn_sincronizar.pack(pady=15, padx=40, fill="x")

    def procesar_ocr_real(self):
        file_path = filedialog.askopenfilename(title="Seleccionar captura de UTP", filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if not file_path:
            return

        try:
            lector_ocr = easyocr.Reader(['es'])
            resultado_ocr = lector_ocr.readtext(file_path, detail=0)
            
            if not resultado_ocr:
                messagebox.showwarning("W.I.N.", "No se detectó texto en la imagen.")
                return

            # Variables de control intermedias
            self.ocr_tipo = "Tarea"
            descripcion_detectada = ""
            materia_detectada = ""
            vencimiento_detectado = ""

            # Unificación de texto en minúsculas para análisis global sin importar saltos de línea
            texto_unificado = " ".join(resultado_ocr)
            texto_completo_bajo = texto_unificado.lower()
            
            if "foro" in texto_completo_bajo:
                self.ocr_tipo = "Foro"

            # ==========================================
            # 1. EXTRACCIÓN INMUTABLE DE FECHA (Canvas Detallado o Compacto)
            # ==========================================
            import re
            
            # Caso A: Formato numérico directo (DD/MM/YYYY)
            match_numerico = re.search(r'\d{2}/\d{2}/\d{4}', texto_unificado)
            if match_numerico:
                vencimiento_detectado = match_numerico.group(0)
            else:
                # Caso B: Formato extendido de texto ("Viernes, 19 de junio de 2026")
                meses = {
                    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05", "junio": "06",
                    "julio": "07", "agosto": "08", "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
                }
                
                for mes_nombre, mes_num in meses.items():
                    if mes_nombre in texto_completo_bajo:
                        patron_dinamico = rf'(\d{{1,2}})[^\d]*{mes_nombre}[^\d]*(\d{{4}})'
                        match_dinamico = re.search(patron_dinamico, texto_completo_bajo)
                        if match_dinamico:
                            dia_str = match_dinamico.group(1).zfill(2)
                            año_str = match_dinamico.group(2)
                            vencimiento_detectado = f"{dia_str}/{mes_num}/{año_str}"
                            break

            # ==========================================
            # 2. FILTRADO AGRESIVO DE BASURA Y ETIQUETAS "NUEVAS"
            # ==========================================
            # Lista negra absoluta de palabras que JAMÁS deben asignarse a Curso o Tarea
            basura_canvas = [
                "tarea no calificada", "foro no calificado", "por entregar", "tarea calificada",
                "porentrece", "fecha límite", "fecha limite", "a contenido", "presencial", 
                "precendal", "ptesende", "fecha de vencimiento", "vencido", "evaluaciones", 
                "tareas", "foros", "notas", "anuncios", "zoom", "contenido"
            ]

            lineas_utiles = []
            for linea in resultado_ocr:
                clean = linea.strip()
                # Si es idéntica o el OCR pegó una palabra basura al inicio/fin, la limpiamos
                if any(basura in clean.lower() for basura in basura_canvas) or len(clean) <= 1:
                    # Corrección en caliente: si la línea contiene la sección y basura al costado, preservamos el fragmento útil
                    if "sección" in clean.lower() or "seccion" in clean.lower() or re.search(r'\b\d{5}\b', clean):
                        # Remover palabras basura específicas de la línea del curso
                        for b in basura_canvas:
                            clean = re.sub(rf'\b{b}\b', '', clean, flags=re.IGNORECASE).strip()
                        if len(clean) > 3:
                            lineas_utiles.append(clean)
                    continue
                lineas_utiles.append(clean)

            # ==========================================
            # 3. EXTRACCIÓN ASOCIATIVA POR PALABRAS CLAVE (MALLA UTP)
            # ==========================================
            # Prioridad 1: Identificar el Curso usando palabras core de tus asignaturas
            palabras_curso = ["calidad", "software", "desarrollo", "diseño", "pruebas", "productos", "arquitectura", "full", "stack"]
            
            for linea in lineas_utiles:
                if any(p in linea.lower() for p in palabras_curso):
                    # Si contiene datos de la sección, limpiamos el código numérico para dejar solo el nombre limpio
                    if "sección" in linea.lower() or "seccion" in linea.lower() or "-" in linea:
                        materia_detectada = linea.split("-")[0].split("Sección")[0].split("seccion")[0].strip()
                    else:
                        materia_detectada = linea
                    break

            # Prioridad 2: Identificar la Tarea (Buscamos patrones como Lab S3, S12.s1, Avance, etc.)
            for linea in lineas_utiles:
                linea_lower = linea.lower()
                # Ignorar si es la misma línea que ya elegimos como materia
                if materia_detectada and linea_lower in materia_detectada.lower():
                    continue
                
                # Patrón: Inicial S + número (S12, S7), palabras clave como "lab", "avance", "proyecto"
                if re.search(r'\b[sS]\d+', linea) or "lab" in linea_lower or "avance" in linea_lower or "proyecto" in linea_lower:
                    descripcion_detectada = linea
                    break

            # ==========================================
            # 4. REGLAS DE CAÍDA (FALLBACKS) PARA LISTAS COMPACTAS
            # ==========================================
            # Si el mapeo asociativo falló (vistas rápidas de Canvas), usamos la proximidad clásica
            if not materia_detectada or not descripcion_detectada:
                for idx, linea in enumerate(lineas_utiles):
                    if "vence" in linea.lower():
                        if idx - 1 >= 0 and not materia_detectada:
                            materia_detectada = lineas_utiles[idx - 1]
                        if idx - 2 >= 0 and not descripcion_detectada:
                            descripcion_detectada = lineas_utiles[idx - 2]

            # ==========================================
            # 5. POST-PROCESAMIENTO Y CORRECCIÓN DE CARACTERES RESIDUALES
            # ==========================================
            # Limpieza del Curso
            if materia_detectada:
                materia_detectada = re.sub(r'\b(sección|seccion)\b', '', materia_detectada, flags=re.IGNORECASE)
                materia_detectada = re.sub(r'\b\d{5}\b', '', materia_detectada)  # Quita el NRC de 5 dígitos
                materia_detectada = materia_detectada.replace("|", "").replace("-", "").strip().upper()

            # Limpieza de la Tarea (Corrige EasyOCR interpretando mal los puntos o el prefijo 'S')
            if descripcion_detectada:
                descripcion_detectada = re.sub(r'\.(\d{1})1', r'.s\1', descripcion_detectada)
                descripcion_detectada = re.sub(r'\.51', r'.s1', descripcion_detectada)
                if descripcion_detectada.startswith("5") and len(descripcion_detectada) > 2 and descripcion_detectada[1].isdigit():
                    descripcion_detectada = "S" + descripcion_detectada[1:]
                descripcion_detectada = descripcion_detectada.strip(" | -")

            # Valores por defecto de alta fidelidad si la imagen está totalmente corrupta
            if not materia_detectada or len(materia_detectada) < 3:
                materia_detectada = "CURSO ACADÉMICO UTP"
            if not descripcion_detectada:
                descripcion_detectada = "Actividad Pendiente"
            if not vencimiento_detectado:
                vencimiento_detectado = "19/06/2026"

            # ==========================================
            # 6. ENVIAR DATOS A LOS CAMPOS DE LA INTERFAZ
            # ==========================================
            self.ent_ocr_desc.delete(0, ctk.END)
            self.ent_ocr_desc.insert(0, descripcion_detectada)

            self.ent_ocr_mat.delete(0, ctk.END)
            self.ent_ocr_mat.insert(0, materia_detectada)

            self.ent_ocr_venc.delete(0, ctk.END)
            self.ent_ocr_venc.insert(0, vencimiento_detectado)

            messagebox.showinfo("W.I.N. System", "Lectura de IA completada con éxito.")

        except Exception as e:
            messagebox.showerror("Error OCR", f"Falló el motor al procesar la imagen: {str(e)}")

    def guardar_datos_corregidos(self):
        desc = self.ent_ocr_desc.get().strip()
        mat = self.ent_ocr_mat.get().strip()
        venc = self.ent_ocr_venc.get().strip()

        if not desc or not venc:
            messagebox.showwarning("Campos vacíos", "Por favor completa la descripción y la fecha.")
            return

        # Guardar en base de datos local
        self.db.insertar_tarea("Hoy", self.ocr_tipo, desc, mat, venc, "Pendiente")
        
        messagebox.showinfo("W.I.N. System", "¡Sincronizado! Tarea guardada con éxito en la Base de Datos y vinculada al Calendario.")
        
        # Limpiar formulario e ir al Dashboard en vivo
        self.actualizar_lista_dashboard()
        self.cambiar_pantalla("Dashboard")

    # ==========================================
    # PANTALLA: MI CALENDARIO INTERACTIVO
    # ==========================================
    def inicializar_calendario(self):
        self.pantalla_calendario.grid_columnconfigure(0, weight=1)
        self.pantalla_calendario.grid_rowconfigure(2, weight=1)

        self.lbl_mes_tit = ctk.CTkLabel(self.pantalla_calendario, text="CALENDARIO - JUNIO 2026", font=ctk.CTkFont(size=26, weight="bold"), text_color="white")
        self.lbl_mes_tit.grid(row=0, column=0, pady=20, padx=30, sticky="w")

        self.grid_dias = ctk.CTkFrame(self.pantalla_calendario, fg_color="transparent")
        self.grid_dias.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")

    def renderizar_mes_calendario(self, año, mes):
        for w in self.grid_dias.winfo_children():
            w.destroy()

        for i in range(7):
            self.grid_dias.grid_columnconfigure(i, weight=1, uniform="b")

        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for idx, dia in enumerate(dias_semana):
            lbl = ctk.CTkLabel(self.grid_dias, text=dia, font=ctk.CTkFont(size=13, weight="bold"), text_color="#888888")
            lbl.grid(row=0, column=idx, pady=10)

        tareas = self.db.obtener_todas_tareas()

        cal = calendar.Calendar(firstweekday=0)
        mes_dias = cal.monthdayscalendar(año, mes)

        for row_idx, semana in enumerate(mes_dias):
            for col_idx, dia_num in enumerate(semana):
                if dia_num == 0:
                    celda_vacia = ctk.CTkFrame(self.grid_dias, height=90, fg_color="#1F1F1F", corner_radius=8)
                    celda_vacia.grid(row=row_idx+1, column=col_idx, padx=4, pady=4, sticky="nsew")
                else:
                    celda = ctk.CTkFrame(self.grid_dias, height=90, fg_color="#242424", border_width=1, border_color="#333333", corner_radius=8)
                    celda.grid(row=row_idx+1, column=col_idx, padx=4, pady=4, sticky="nsew")
                    
                    lbl_num = ctk.CTkLabel(celda, text=str(dia_num), font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
                    lbl_num.pack(anchor="nw", padx=8, pady=4)

                    # Mapear las fechas guardadas: Formato esperado DD/MM/YYYY
                    fecha_string_buscar = f"{str(dia_num).zfill(2)}/{str(mes).zfill(2)}/{año}"
                    
                    for t in tareas:
                        # Comparamos la fecha limpia de la Base de Datos
                        if t[5] == fecha_string_buscar:
                            lbl_tag = ctk.CTkLabel(celda, text=t[4][:12], font=ctk.CTkFont(size=10, weight="bold"), 
                                                   fg_color="#C8102E", text_color="white", corner_radius=4, height=18)
                            lbl_tag.pack(fill="x", padx=4, pady=2)

    # ==========================================
    # FORMULARIO MANUAL
    # ==========================================
    def abrir_ventana_manual(self):
        vent = ctk.CTkToplevel(self)
        vent.title("Agregar Tarea Manual")
        vent.geometry("400x450")
        vent.resizable(False, False)
        vent.attributes("-topmost", True)

        ctk.CTkLabel(vent, text="Nueva Tarea", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        entry_desc = ctk.CTkEntry(vent, placeholder_text="Descripción de la actividad", width=300)
        entry_desc.pack(pady=10)

        entry_mat = ctk.CTkEntry(vent, placeholder_text="Materia (Ejm: DESARROLLO FULL STACK)", width=300)
        entry_mat.pack(pady=10)

        entry_venc = ctk.CTkEntry(vent, placeholder_text="Vencimiento (DD/MM/YYYY)", width=300)
        entry_venc.pack(pady=10)

        def guardar():
            if entry_desc.get() and entry_venc.get():
                self.db.insertar_tarea("Manual", "Tarea", entry_desc.get().strip(), entry_mat.get().strip(), entry_venc.get().strip(), "Pendiente")
                self.actualizar_lista_dashboard()
                vent.destroy()
                messagebox.showinfo("W.I.N.", "Tarea guardada correctamente.")
            else:
                messagebox.showwarning("Error", "Completa los campos obligatorios.")

        ctk.CTkButton(vent, text="Guardar en Base de Datos", fg_color="#107C41", command=guardar, width=200).pack(pady=25)
    
    def resolver_tarea_interfaz(self, id_tarea):
        """Elimina la actividad a través de la base de datos y refresca el dashboard"""
        # Llamamos al método de borrado usando el objeto de base de datos que ya tienes inicializado (self.db)
        self.db.eliminar_tarea_db(id_tarea)
        
        # Volvemos a llamar a tu función para que la lista de la pantalla se actualice sola
        self.actualizar_lista_dashboard()

if __name__ == "__main__":
    app = AppWIN()
    app.mainloop()