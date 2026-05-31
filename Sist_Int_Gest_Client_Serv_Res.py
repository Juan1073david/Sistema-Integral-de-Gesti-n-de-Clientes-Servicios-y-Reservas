# ============================================================================
# SISTEMA DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS
# ============================================================================

# ----------------------------------------------------------------------------
# IMPORTACIÓN DE LIBRERÍAS (módulos que Python nos presta)
# ----------------------------------------------------------------------------
import tkinter as tk  # Librería para crear ventanas y botones (interfaz gráfica)
from tkinter import ttk, messagebox, scrolledtext  # Componentes extras de tkinter
from abc import ABC, abstractmethod  # ABC = Clase Abstracta Base (para crear clases abstractas)
from datetime import datetime  # Para manejar fechas y horas
import os  # Para trabajar con archivos y carpetas del sistema
 
# ----------------------------------------------------------------------------
# CONFIGURACIÓN DEL ARCHIVO DE LOGS (registro de eventos y errores)
# ----------------------------------------------------------------------------
LOG_FILE = "sistema_log.txt"  # Nombre del archivo donde se guardarán los logs

def escribir_log(mensaje, tipo="INFO"):
    
    try:
        # Obtenemos la fecha y hora actual para saber cuándo pasó algo
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Abrimos el archivo en modo "a" (append = añadir al final)
        with open(LOG_FILE, "a", encoding="utf-8") as archivo:
            # Escribimos la línea con hora, tipo y mensaje
            archivo.write(f"[{timestamp}] [{tipo}] {mensaje}\n")
    except Exception as e:
        # Si no podemos escribir el log, al menos lo mostramos en consola
        print(f"Error escribiendo log: {e}")


# ----------------------------------------------------------------------------
# 1. EXCEPCIÓN PERSONALIZADA
# ----------------------------------------------------------------------------
class ReservaError(Exception):
    pass
# ----------------------------------------------------------------------------
# 2. CLASE ABSTRACTA (una plantilla para otras clases)
# ----------------------------------------------------------------------------
class EntidadBase(ABC):
    """
    Esta clase es abstracta. Sirve como base para Cliente y Servicio.
    """
    @abstractmethod
    def validar_datos(self):
        pass
    
    @abstractmethod
    def mostrar_informacion(self):
        pass
# ----------------------------------------------------------------------------
# 3. CLASE CLIENTE (hereda de EntidadBase)
# ----------------------------------------------------------------------------
class Cliente(EntidadBase):
    """
    Esta clase representa a un cliente de la empresa Software FJ.
    Guarda datos como nombre, email, teléfono y un ID único.
    """
    _contador_clientes = 0  
    def __init__(self, nombre, email, telefono):
        # Validaciones básicas antes de crear el cliente
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre no puede estar vacío y debe ser texto")
        if not email or "@" not in email:
            raise ValueError("El email debe contener @")
        if not telefono or not telefono.isdigit():
            raise ValueError("El teléfono debe contener solo números")
        # Asignamos los valores al cliente
        self._nombre = nombre  
        self._email = email
        self._telefono = telefono
        Cliente._contador_clientes += 1
        self._id = Cliente._contador_clientes
        escribir_log(f"Cliente creado: {self._nombre} (ID: {self._id})")
    # ------------------------------------------------------------------------
    # Getters y Setters 
    # ------------------------------------------------------------------------
    def get_id(self): 
        return self._id
    def get_nombre(self):
        return self._nombre
    def set_nombre(self, nombre):
        if nombre:
            self._nombre = nombre
        else:
            raise ValueError("El nombre no puede estar vacío")
    def get_email(self):
        return self._email
    def set_email(self, email):
        if "@" in email:
            self._email = email
        else:
            raise ValueError("Email inválido") 
    def get_telefono(self):
        return self._telefono
    
    def set_telefono(self, telefono):
        if telefono.isdigit():
            self._telefono = telefono
        else:
            raise ValueError("Teléfono debe ser numérico")
    
    # Implementación de los métodos abstractos de EntidadBase
    def validar_datos(self):
        return (self._nombre and self._email and self._telefono and 
                "@" in self._email and self._telefono.isdigit())
    def mostrar_informacion(self):
        return f"ID: {self._id} | {self._nombre} | {self._email} | Tel: {self._telefono}"
    
    def __str__(self):
        return self.mostrar_informacion()


# ----------------------------------------------------------------------------
# 4. CLASE ABSTRACTA SERVICIO (hereda de EntidadBase)
# ----------------------------------------------------------------------------
class Servicio(EntidadBase):
    def __init__(self, nombre, precio_base):
        self._nombre = nombre
        self._precio_base = precio_base
        self._id = None  # Se asignará después
    
    def get_nombre(self):
        return self._nombre  
    def get_precio_base(self):
        return self._precio_base
    @abstractmethod
    def calcular_costo(self, duracion, **kwargs):
        pass
    @abstractmethod
    def descripcion_completa(self):
        pass  
    def validar_datos(self):
        return self._nombre and self._precio_base > 0
# ----------------------------------------------------------------------------
# 5. SERVICIO ESPECÍFICO: RESERVA DE SALAS
# ----------------------------------------------------------------------------
class ReservaSalas(Servicio):
    def __init__(self, nombre, precio_base, capacidad_maxima, tiene_proyector=False):
        super().__init__(nombre, precio_base)  # Llamamos al constructor de la clase padre
        self._capacidad_maxima = capacidad_maxima
        self._tiene_proyector = tiene_proyector
    def calcular_costo(self, duracion, **kwargs):
        costo = self._precio_base * duracion
        if self._tiene_proyector:
            costo = costo * 1.20 
        return round(costo, 2)
    def descripcion_completa(self):
        proyector_texto = "Sí" if self._tiene_proyector else "No"
        return f"Sala: {self._nombre} | Capacidad: {self._capacidad_maxima} | Proyector: {proyector_texto} | Precio base/hora: ${self._precio_base}"
    def mostrar_informacion(self):
        return self.descripcion_completa()
# ----------------------------------------------------------------------------
# 6. SERVICIO ESPECÍFICO: ALQUILER DE EQUIPOS
# ----------------------------------------------------------------------------
class AlquilerEquipos(Servicio):    
    def __init__(self, nombre, precio_base, tipo_equipo):
        super().__init__(nombre, precio_base)
        self._tipo_equipo = tipo_equipo
    def calcular_costo(self, duracion, **kwargs):
        cantidad = kwargs.get('cantidad', 1) 
        costo = self._precio_base * cantidad * duracion
        return round(costo, 2) 
    def descripcion_completa(self):
        return f"Alquiler: {self._nombre} | Tipo: {self._tipo_equipo} | Precio base/día/equipo: ${self._precio_base}"
    def mostrar_informacion(self):
        return self.descripcion_completa()

# ----------------------------------------------------------------------------
# 7. SERVICIO ESPECÍFICO: ASESORÍAS ESPECIALIZADAS
# ----------------------------------------------------------------------------
class AsesoriaEspecializada(Servicio):
    NIVELES = {"básico": 1.0, "intermedio": 1.3, "avanzado": 1.6}
    def __init__(self, nombre, precio_base, especialidad, nivel_experto="básico"):
        super().__init__(nombre, precio_base)
        self._especialidad = especialidad
        self._nivel_experto = nivel_experto.lower() if nivel_experto.lower() in self.NIVELES else "básico"
    def calcular_costo(self, duracion, **kwargs):
        multiplicador = self.NIVELES.get(self._nivel_experto, 1.0)
        costo = self._precio_base * duracion * multiplicador
        return round(costo, 2)
    def descripcion_completa(self):
        return f"Asesoría: {self._nombre} | Especialidad: {self._especialidad} | Nivel: {self._nivel_experto} | Precio base/hora: ${self._precio_base}"
    def mostrar_informacion(self):
        return self.descripcion_completa()
# ----------------------------------------------------------------------------
# 8. CLASE RESERVA (integra cliente, servicio, duración y estado)
# ----------------------------------------------------------------------------
class Reserva:
    
    _contador_reservas = 0    
    def __init__(self, cliente, servicio, duracion, **kwargs):
        if not isinstance(cliente, Cliente):
            raise TypeError("cliente debe ser un objeto Cliente")
        if not isinstance(servicio, Servicio):
            raise TypeError("servicio debe ser un objeto Servicio")
        if duracion <= 0:
            raise ValueError("La duración debe ser mayor a 0")
        
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._parametros_extra = kwargs
        self._costo_total = servicio.calcular_costo(duracion, **kwargs)
        self._estado = "Pendiente"
        Reserva._contador_reservas += 1
        self._id = Reserva._contador_reservas
        escribir_log(f"Reserva creada: ID {self._id} - Cliente: {cliente.get_nombre()} - Costo: ${self._costo_total}")
    
    def get_id(self):
        return self._id
  
    def get_cliente(self):
        return self._cliente
  
    def get_servicio(self):
        return self._servicio
  
    def get_costo_total(self):
        return self._costo_total
    
    def get_estado(self):
        return self._estado

    def get_duracion(self):
        return self._duracion
    
    def confirmar(self):
        if self._estado == "Cancelada":
            raise ReservaError("No se puede confirmar una reserva cancelada")
        self._estado = "Confirmada"
        escribir_log(f"Reserva {self._id} confirmada")
        return True
    
    def cancelar(self):
        if self._estado == "Confirmada":
            raise ReservaError("No se puede cancelar una reserva ya confirmada (política de la empresa)")
        self._estado = "Cancelada"
        escribir_log(f"Reserva {self._id} cancelada")
        return True
    
    def mostrar_informacion(self):
        return (f"=== RESERVA #{self._id} ===\n"
                f"Cliente: {self._cliente.get_nombre()}\n"
                f"Servicio: {self._servicio.get_nombre()}\n"
                f"Duración: {self._duracion}\n"
                f"Costo total: ${self._costo_total}\n"
                f"Estado: {self._estado}\n"
                f"Detalle: {self._servicio.descripcion_completa()}")
# ----------------------------------------------------------------------------
# 9. CLASE PRINCIPAL DEL SISTEMA (GESTOR)
# ----------------------------------------------------------------------------
class SistemaGestion:    
    def __init__(self):
        self._clientes = []      # Lista para guardar todos los clientes
        self._servicios = []     # Lista para guardar todos los servicios disponibles
        self._reservas = []      # Lista para guardar todas las reservas
        escribir_log("Sistema de Gestión inicializado")
    
    # ------------------- MÉTODOS PARA CLIENTES -------------------
    def agregar_cliente(self, nombre, email, telefono):
        try:
            cliente = Cliente(nombre, email, telefono)
            self._clientes.append(cliente)
            escribir_log(f"Cliente agregado al sistema: {cliente.get_nombre()}")
            return cliente
        except ValueError as e:
            error_msg = f"Error al crear cliente: {str(e)}"
            escribir_log(error_msg, "ERROR")
            raise     
    def listar_clientes(self):
        return self._clientes.copy()
    
    def buscar_cliente_por_id(self, id_cliente):
        for cliente in self._clientes:
            if cliente.get_id() == id_cliente:
                return cliente
        return None
    
    def buscar_cliente_por_nombre(self, nombre):
        resultados = []
        for cliente in self._clientes:
            if nombre.lower() in cliente.get_nombre().lower():
                resultados.append(cliente)
        return resultados
    
    # ------------------- MÉTODOS PARA SERVICIOS -------------------
    def agregar_servicio(self, servicio):
        if isinstance(servicio, Servicio):
            self._servicios.append(servicio)
            escribir_log(f"Servicio agregado: {servicio.get_nombre()}")
        else:
            raise TypeError("Debe ser un objeto Servicio")
    
    def listar_servicios(self):
        return self._servicios.copy()
    
    # ------------------- MÉTODOS PARA RESERVAS -------------------
    def crear_reserva(self, id_cliente, id_servicio, duracion, **kwargs):
        try:
            # Buscamos el cliente
            cliente = self.buscar_cliente_por_id(id_cliente)
            if not cliente:
                raise ReservaError(f"No se encontró cliente con ID {id_cliente}")
            
            if id_servicio < 1 or id_servicio > len(self._servicios):
                raise ReservaError(f"No se encontró servicio con ID {id_servicio}")
            
            servicio = self._servicios[id_servicio - 1]  # -1 porque las listas empiezan en 0
            reserva = Reserva(cliente, servicio, duracion, **kwargs)
            self._reservas.append(reserva)
            return reserva
        except (ValueError, ReservaError, TypeError) as e:
            escribir_log(f"Error creando reserva: {str(e)}", "ERROR")
            raise
    
    def listar_reservas(self):
        return self._reservas.copy()
    
    def cancelar_reserva(self, id_reserva):
        for reserva in self._reservas:
            if reserva.get_id() == id_reserva:
                reserva.cancelar()
                return True
        raise ReservaError(f"No se encontró reserva con ID {id_reserva}")
    
    def confirmar_reserva(self, id_reserva):
        for reserva in self._reservas:
            if reserva.get_id() == id_reserva:
                reserva.confirmar()
                return True
        raise ReservaError(f"No se encontró reserva con ID {id_reserva}")
    
    # ------------------- MÉTODOS DE ESTADÍSTICAS -------------------
    def obtener_resumen(self):
        total_clientes = len(self._clientes)
        total_reservas = len(self._reservas)
        total_ingresos = sum(r.get_costo_total() for r in self._reservas if r.get_estado() == "Confirmada")
        return {
            "clientes": total_clientes,
            "reservas": total_reservas,
            "ingresos": round(total_ingresos, 2)
        }
# ----------------------------------------------------------------------------
# 10. INTERFAZ GRÁFICA CON TKINTER (la ventana que verás al ejecutar)
# ----------------------------------------------------------------------------
class AplicacionTkinter:    
    def __init__(self, sistema):
        self.sistema = sistema  # Guardamos el sistema para usarlo después
        self.ventana = tk.Tk()
        self.ventana.title("Software FJ - Sistema de Gestión de Clientes, Servicios y Reservas")
        self.ventana.geometry("1200x700")  # Tamaño de la ventana
        self.ventana.configure(bg="#f0f0f0")  # Color de fondo gris claro
        self.frame_actual = None
        self.crear_menu()
        self.mostrar_pantalla_inicio()
    
    def crear_menu(self):
        barra_menu = tk.Menu(self.ventana)
        self.ventana.config(menu=barra_menu)
        menu_clientes = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Clientes", menu=menu_clientes)
        menu_clientes.add_command(label="Registrar nuevo cliente", command=self.mostrar_registro_cliente)
        menu_clientes.add_command(label="Listar clientes", command=self.mostrar_lista_clientes)
        menu_clientes.add_separator()
        menu_clientes.add_command(label="Buscar cliente", command=self.mostrar_buscar_cliente)
        menu_servicios = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Servicios", menu=menu_servicios)
        menu_servicios.add_command(label="Ver servicios disponibles", command=self.mostrar_servicios)
        menu_reservas = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Reservas", menu=menu_reservas)
        menu_reservas.add_command(label="Crear nueva reserva", command=self.mostrar_crear_reserva)
        menu_reservas.add_command(label="Listar reservas", command=self.mostrar_reservas)
        menu_reservas.add_command(label="Cancelar reserva", command=self.mostrar_cancelar_reserva)
        menu_reservas.add_command(label="Confirmar reserva", command=self.mostrar_confirmar_reserva)
        
        # Menú "Reportes"
        menu_reportes = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Reportes", menu=menu_reportes)
        menu_reportes.add_command(label="Resumen del sistema", command=self.mostrar_resumen)
        menu_reportes.add_command(label="Ver archivo de logs", command=self.mostrar_logs)
        
        # Menú "Ayuda"
        menu_ayuda = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)
    
    def limpiar_frame(self):
        if self.frame_actual:
            self.frame_actual.destroy()
    
    def mostrar_pantalla_inicio(self):
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="SOFTWARE FJ", 
                          font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=30)
        
        subtitulo = tk.Label(self.frame_actual, 
                             text="Sistema Integral de Gestión de Clientes, Servicios y Reservas",
                             font=("Arial", 14), bg="#f0f0f0", fg="#34495e")
        subtitulo.pack(pady=10)
        info_frame = tk.Frame(self.frame_actual, bg="white", relief=tk.RAISED, bd=2)
        info_frame.pack(pady=40, padx=50, fill="both", expand=True)

        texto_info = """
        🏢 BIENVENIDO AL SISTEMA
        
        El sistema ya tiene datos de ejemplo para que puedas probarlo:
        
        • Clientes: 3 clientes registrados
        • Servicios: 3 tipos de servicios disponibles
        • Reservas: 5 reservas de ejemplo (algunas válidas, otras con errores)
        
        📌 PARA COMENZAR:
        Usa el menú superior para navegar entre las opciones.
        
        ✅ PRUEBA DE MANEJO DE ERRORES:
        El sistema está preparado para capturar errores sin cerrarse.
        Por ejemplo, intenta crear un cliente con email sin @.
        """
        
        label_info = tk.Label(info_frame, text=texto_info, font=("Arial", 11), 
                              bg="white", justify="left", fg="#2c3e50")
        label_info.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Botones rápidos
        botones_frame = tk.Frame(self.frame_actual, bg="#f0f0f0")
        botones_frame.pack(pady=20)
        
        btn_clientes = tk.Button(botones_frame, text="➕ Registrar Cliente", 
                                 command=self.mostrar_registro_cliente,
                                 bg="#3498db", fg="white", font=("Arial", 11), padx=20, pady=10)
        btn_clientes.pack(side="left", padx=10)
        
        btn_reservas = tk.Button(botones_frame, text="📅 Crear Reserva", 
                                 command=self.mostrar_crear_reserva,
                                 bg="#2ecc71", fg="white", font=("Arial", 11), padx=20, pady=10)
        btn_reservas.pack(side="left", padx=10)
        
        btn_reportes = tk.Button(botones_frame, text="📊 Ver Resumen", 
                                 command=self.mostrar_resumen,
                                 bg="#e67e22", fg="white", font=("Arial", 11), padx=20, pady=10)
        btn_reportes.pack(side="left", padx=10)
    
    # ------------------- PANTALLAS DE CLIENTES -------------------
    def mostrar_registro_cliente(self):
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="📝 REGISTRO DE NUEVO CLIENTE", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)
        formulario = tk.Frame(self.frame_actual, bg="white", relief=tk.RAISED, bd=1)
        formulario.pack(pady=10, padx=50, fill="both", expand=True)
        campos = [
            ("Nombre completo:", "entry_nombre"),
            ("Email:", "entry_email"),
            ("Teléfono (solo números):", "entry_telefono")
        ] 
        self.entries = {}
        for i, (label_text, key) in enumerate(campos):
            lbl = tk.Label(formulario, text=label_text, font=("Arial", 11), 
                           bg="white", anchor="w")
            lbl.grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            entry = tk.Entry(formulario, font=("Arial", 11), width=40)
            entry.grid(row=i, column=1, padx=20, pady=10)
            self.entries[key] = entry
        def registrar():
            nombre = self.entries["entry_nombre"].get()
            email = self.entries["entry_email"].get()
            telefono = self.entries["entry_telefono"].get()
            
            try:
                cliente = self.sistema.agregar_cliente(nombre, email, telefono)
                messagebox.showinfo("Éxito", f"¡Cliente {cliente.get_nombre()} registrado con ID {cliente.get_id()}!")
                # Limpiar campos
                for entry in self.entries.values():
                    entry.delete(0, tk.END)
            except ValueError as e:
                messagebox.showerror("Error", f"No se pudo registrar el cliente:\n{str(e)}")
        btn_registrar = tk.Button(formulario, text="Registrar Cliente", command=registrar,
                                  bg="#27ae60", fg="white", font=("Arial", 12), padx=20, pady=10)
        btn_registrar.grid(row=len(campos), column=0, columnspan=2, pady=20)

        btn_volver = tk.Button(self.frame_actual, text="← Volver al inicio", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white", font=("Arial", 10), padx=10, pady=5)
        btn_volver.pack(pady=10)
    
    def mostrar_lista_clientes(self):
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="👥 LISTA DE CLIENTES", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)

        frame_tabla = tk.Frame(self.frame_actual)
        frame_tabla.pack(fill="both", expand=True, pady=10, padx=20)
        
        scroll_y = tk.Scrollbar(frame_tabla, orient="vertical")
        scroll_y.pack(side="right", fill="y")
        
        columnas = ("ID", "Nombre", "Email", "Teléfono")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", 
                             yscrollcommand=scroll_y.set)
        scroll_y.config(command=tabla.yview)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=150)

        clientes = self.sistema.listar_clientes()
        for cliente in clientes:
            tabla.insert("", "end", values=(cliente.get_id(), cliente.get_nombre(),
                                           cliente.get_email(), cliente.get_telefono()))
        
        tabla.pack(fill="both", expand=True)
        lbl_info = tk.Label(self.frame_actual, text=f"Total de clientes: {len(clientes)}", 
                            font=("Arial", 10), bg="#f0f0f0", fg="#7f8c8d")
        lbl_info.pack(pady=5)
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    def mostrar_buscar_cliente(self):
        """Buscar clientes por nombre"""
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="🔍 BUSCAR CLIENTE", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)
 
        frame_busqueda = tk.Frame(self.frame_actual, bg="white", relief=tk.RAISED)
        frame_busqueda.pack(pady=10, padx=50, fill="x")
        
        lbl_nombre = tk.Label(frame_busqueda, text="Nombre a buscar:", 
                              font=("Arial", 11), bg="white")
        lbl_nombre.pack(side="left", padx=10, pady=10)
        
        entry_busqueda = tk.Entry(frame_busqueda, font=("Arial", 11), width=30)
        entry_busqueda.pack(side="left", padx=10, pady=10)
        
        frame_resultados = tk.Frame(self.frame_actual)
        frame_resultados.pack(fill="both", expand=True, pady=10, padx=20)
        
        def buscar(): # Limpiar resultados anteriores
            for widget in frame_resultados.winfo_children():
                widget.destroy()
            
            nombre = entry_busqueda.get()
            if not nombre:
                messagebox.showwarning("Advertencia", "Escribe un nombre para buscar")
                return
            
            resultados = self.sistema.buscar_cliente_por_nombre(nombre)
            
            if resultados:
                lbl_res = tk.Label(frame_resultados, text=f"🔎 {len(resultados)} resultado(s) encontrado(s):", 
                                   font=("Arial", 12), bg="#f0f0f0")
                lbl_res.pack(anchor="w", pady=5)
                
                for cliente in resultados:
                    frame_cliente = tk.Frame(frame_resultados, bg="white", relief=tk.RIDGE, bd=1)
                    frame_cliente.pack(fill="x", pady=2)
                    texto = tk.Label(frame_cliente, text=cliente.mostrar_informacion(), 
                                     font=("Arial", 10), bg="white", anchor="w")
                    texto.pack(padx=10, pady=5, fill="x")
            else:
                lbl_no = tk.Label(frame_resultados, text="❌ No se encontraron clientes con ese nombre", 
                                  font=("Arial", 11), bg="#f0f0f0", fg="red")
                lbl_no.pack(pady=20)
        
        btn_buscar = tk.Button(frame_busqueda, text="Buscar", command=buscar,
                               bg="#3498db", fg="white", font=("Arial", 10))
        btn_buscar.pack(side="left", padx=10, pady=10)
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    # ------------------- PANTALLAS DE SERVICIOS -------------------
    def mostrar_servicios(self):
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="🛠️ SERVICIOS DISPONIBLES", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)
        
        servicios = self.sistema.listar_servicios()
        
        for i, servicio in enumerate(servicios, 1):
            frame_servicio = tk.Frame(self.frame_actual, bg="white", relief=tk.RAISED, bd=1)
            frame_servicio.pack(fill="x", pady=5, padx=50)            
            texto = f"[{i}] {servicio.mostrar_informacion()}"
            lbl = tk.Label(frame_servicio, text=texto, font=("Arial", 11), 
                           bg="white", justify="left", anchor="w")
            lbl.pack(padx=10, pady=10, fill="x")
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    # ------------------- PANTALLAS DE RESERVAS -------------------
    def mostrar_crear_reserva(self):
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="📅 CREAR NUEVA RESERVA", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)
        
        formulario = tk.Frame(self.frame_actual, bg="white", relief=tk.RAISED, bd=1)
        formulario.pack(pady=10, padx=50, fill="both", expand=True)

        clientes = self.sistema.listar_clientes()
        if not clientes:
            lbl_error = tk.Label(formulario, text="⚠️ No hay clientes registrados. Primero registra un cliente.",
                                 font=("Arial", 11), bg="white", fg="red")
            lbl_error.pack(pady=20)
        else: # Lista de clientes (para elegir por ID)
            lbl_cliente = tk.Label(formulario, text="Seleccione Cliente (ID):", 
                                   font=("Arial", 11), bg="white")
            lbl_cliente.pack(anchor="w", padx=20, pady=(10,0))
            
            self.combo_clientes = ttk.Combobox(formulario, values=[f"{c.get_id()} - {c.get_nombre()}" for c in clientes],
                                               width=40, font=("Arial", 10))
            self.combo_clientes.pack(padx=20, pady=5, anchor="w")
            
            # Lista de servicios
            servicios = self.sistema.listar_servicios()
            lbl_servicio = tk.Label(formulario, text="Seleccione Servicio (número):", 
                                    font=("Arial", 11), bg="white")
            lbl_servicio.pack(anchor="w", padx=20, pady=(10,0))
            
            self.combo_servicios = ttk.Combobox(formulario, values=[f"{i+1} - {s.get_nombre()}" for i, s in enumerate(servicios)],
                                                width=40, font=("Arial", 10))
            self.combo_servicios.pack(padx=20, pady=5, anchor="w")
            
            # Duración
            lbl_duracion = tk.Label(formulario, text="Duración (horas o días según servicio):", 
                                    font=("Arial", 11), bg="white")
            lbl_duracion.pack(anchor="w", padx=20, pady=(10,0))
            self.entry_duracion = tk.Entry(formulario, font=("Arial", 11), width=20)
            self.entry_duracion.pack(anchor="w", padx=20, pady=5)
            lbl_extra = tk.Label(formulario, text="Cantidad de equipos (solo para Alquiler de Equipos):", 
                                 font=("Arial", 11), bg="white")
            lbl_extra.pack(anchor="w", padx=20, pady=(10,0))
            self.entry_cantidad = tk.Entry(formulario, font=("Arial", 11), width=10)
            self.entry_cantidad.pack(anchor="w", padx=20, pady=5)
            self.entry_cantidad.insert(0, "1")
            
            def crear_reserva_accion():
                try:   # Obtener ID del cliente del combo
                    cliente_texto = self.combo_clientes.get()
                    if not cliente_texto:
                        messagebox.showwarning("Datos incompletos", "Seleccione un cliente")
                        return
                    id_cliente = int(cliente_texto.split(" - ")[0])
                     # Obtener ID del servicio
                    servicio_texto = self.combo_servicios.get()
                    if not servicio_texto:
                        messagebox.showwarning("Datos incompletos", "Seleccione un servicio")
                        return
                    id_servicio = int(servicio_texto.split(" - ")[0])
                    
                    duracion = float(self.entry_duracion.get())
                    if duracion <= 0:
                        messagebox.showwarning("Duración inválida", "La duración debe ser mayor a 0")
                        return
                    
                    cantidad = int(self.entry_cantidad.get()) if self.entry_cantidad.get() else 1
                    
                    # Crear la reserva
                    reserva = self.sistema.crear_reserva(id_cliente, id_servicio, duracion, cantidad=cantidad)
                    messagebox.showinfo("Éxito", f"¡Reserva #{reserva.get_id()} creada!\nCosto total: ${reserva.get_costo_total()}")

                    self.combo_clientes.set("")
                    self.combo_servicios.set("")
                    self.entry_duracion.delete(0, tk.END)
                    self.entry_cantidad.delete(0, tk.END)
                    self.entry_cantidad.insert(0, "1")
                    
                except ValueError as e:
                    messagebox.showerror("Error de datos", str(e))
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo crear la reserva:\n{str(e)}")
            
            btn_crear = tk.Button(formulario, text="Crear Reserva", command=crear_reserva_accion,
                                  bg="#2ecc71", fg="white", font=("Arial", 12), padx=20, pady=10)
            btn_crear.pack(pady=20)
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    def mostrar_reservas(self):# Muestra todas las reservas
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="📋 LISTA DE RESERVAS", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)
        
        frame_tabla = tk.Frame(self.frame_actual)
        frame_tabla.pack(fill="both", expand=True, pady=10, padx=20)
        
        scroll_y = tk.Scrollbar(frame_tabla, orient="vertical")
        scroll_y.pack(side="right", fill="y")
        
        columnas = ("ID", "Cliente", "Servicio", "Duración", "Costo", "Estado")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", 
                             yscrollcommand=scroll_y.set)
        scroll_y.config(command=tabla.yview)
        
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=150)
        
        reservas = self.sistema.listar_reservas()
        for r in reservas:
            tabla.insert("", "end", values=(
                r.get_id(),
                r.get_cliente().get_nombre(),
                r.get_servicio().get_nombre(),
                r.get_duracion(),
                f"${r.get_costo_total()}",
                r.get_estado()
            ))
        
        tabla.pack(fill="both", expand=True)
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    def mostrar_cancelar_reserva(self):#  Cancelar una reserva por ID
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="❌ CANCELAR RESERVA", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)
        
        frame_form = tk.Frame(self.frame_actual, bg="white", relief=tk.RAISED)
        frame_form.pack(pady=20, padx=50, fill="x")
        
        lbl_id = tk.Label(frame_form, text="ID de la reserva a cancelar:", 
                          font=("Arial", 11), bg="white")
        lbl_id.pack(padx=20, pady=(10,0), anchor="w")
        
        entry_id = tk.Entry(frame_form, font=("Arial", 11), width=15)
        entry_id.pack(padx=20, pady=5, anchor="w")
        
        def cancelar():
            try:
                id_reserva = int(entry_id.get())
                self.sistema.cancelar_reserva(id_reserva)
                messagebox.showinfo("Éxito", f"Reserva #{id_reserva} cancelada correctamente")
                entry_id.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número de ID válido")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        btn_cancelar = tk.Button(frame_form, text="Cancelar Reserva", command=cancelar,
                                 bg="#e74c3c", fg="white", font=("Arial", 12), padx=20, pady=10)
        btn_cancelar.pack(pady=20)
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    def mostrar_confirmar_reserva(self):#  Confirmar una reserva por ID"""
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="✅ CONFIRMAR RESERVA", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)
        
        frame_form = tk.Frame(self.frame_actual, bg="white", relief=tk.RAISED)
        frame_form.pack(pady=20, padx=50, fill="x")
        
        lbl_id = tk.Label(frame_form, text="ID de la reserva a confirmar:", 
                          font=("Arial", 11), bg="white")
        lbl_id.pack(padx=20, pady=(10,0), anchor="w")
        
        entry_id = tk.Entry(frame_form, font=("Arial", 11), width=15)
        entry_id.pack(padx=20, pady=5, anchor="w")
        
        def confirmar():
            try:
                id_reserva = int(entry_id.get())
                self.sistema.confirmar_reserva(id_reserva)
                messagebox.showinfo("Éxito", f"Reserva #{id_reserva} confirmada correctamente")
                entry_id.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número de ID válido")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        btn_confirmar = tk.Button(frame_form, text="Confirmar Reserva", command=confirmar,
                                  bg="#27ae60", fg="white", font=("Arial", 12), padx=20, pady=10)
        btn_confirmar.pack(pady=20)
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    # ------------------- REPORTES -------------------
    def mostrar_resumen(self):
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="📊 RESUMEN DEL SISTEMA", 
                          font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=20)
        
        resumen = self.sistema.obtener_resumen()
        
        frame_resumen = tk.Frame(self.frame_actual, bg="white", relief=tk.RAISED, bd=2)
        frame_resumen.pack(pady=20, padx=50, fill="both", expand=True)
        
        texto = f"""
        ┌─────────────────────────────────────────┐
        │           ESTADÍSTICAS GENERALES        │
        ├─────────────────────────────────────────┤
        │                                         │
        │   👥 Clientes registrados: {resumen['clientes']}                    │
        │                                         │
        │   📅 Reservas realizadas: {resumen['reservas']}                    │
        │                                         │
        │   💰 Ingresos totales (confirmadas): ${resumen['ingresos']}               │
        │                                         │
        └─────────────────────────────────────────┘
        """
        
        lbl_texto = tk.Label(frame_resumen, text=texto, font=("Courier", 12), 
                             bg="white", justify="left")
        lbl_texto.pack(padx=20, pady=20)
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    def mostrar_logs(self):# "Muestra el contenido del archivo de logs"""
        self.limpiar_frame()
        self.frame_actual = tk.Frame(self.ventana, bg="#f0f0f0")
        self.frame_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
        titulo = tk.Label(self.frame_actual, text="📜 ARCHIVO DE LOGS (Eventos y Errores)", 
                          font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
        titulo.pack(pady=10)

        frame_texto = tk.Frame(self.frame_actual)
        frame_texto.pack(fill="both", expand=True, pady=10, padx=20)
        
        scroll = tk.Scrollbar(frame_texto)
        scroll.pack(side="right", fill="y")
        
        texto_log = scrolledtext.ScrolledText(frame_texto, wrap=tk.WORD, 
                                               font=("Courier", 9),
                                               yscrollcommand=scroll.set)
        texto_log.pack(fill="both", expand=True)
        scroll.config(command=texto_log.yview)

        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    texto_log.insert("1.0", contenido)
            else:
                texto_log.insert("1.0", "No hay archivo de logs aún. El sistema lo creará automáticamente.")
        except Exception as e:
            texto_log.insert("1.0", f"Error al leer logs: {str(e)}")
        
        texto_log.config(state="disabled")  # Solo lectura
        
        btn_volver = tk.Button(self.frame_actual, text="← Volver", 
                               command=self.mostrar_pantalla_inicio,
                               bg="#7f8c8d", fg="white")
        btn_volver.pack(pady=10)
    
    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", 
                            "SISTEMA DE GESTIÓN - SOFTWARE FJ\n\n"
                            "Versión: 1.0\n"
                            "Curso: Programación - UNAD\n"
                            "Código: 213023\n\n"
                            "Tecnologías: Python, POO, Tkinter\n"
                            "Manejo de excepciones y logs\n\n"
                            "© 2025 - Todos los derechos reservados")
    
    def ejecutar(self):
        self.ventana.mainloop()


# ----------------------------------------------------------------------------
# 11. DATOS DE EJEMPLO (para probar el sistema)
# ----------------------------------------------------------------------------
def cargar_datos_ejemplo(sistema):
    print("\n=== CARGANDO DATOS DE EJEMPLO ===\n")
    print("Creando clientes de ejemplo...")
    try:
        cliente1 = sistema.agregar_cliente("Ana María González", "ana@email.com", "3001234567")
        cliente2 = sistema.agregar_cliente("Carlos López", "carlos@email.com", "3109876543")
        cliente3 = sistema.agregar_cliente("Luisa Fernández", "luisa@email.com", "3205551234")
        print("✓ 3 clientes creados correctamente")
    except Exception as e:
        print(f"✗ Error creando clientes: {e}")
    
    # ----- SERVICIOS (creamos 3 tipos) -----
    print("\nCreando servicios de ejemplo...")
    sala_vip = ReservaSalas("Sala VIP Ejecutiva", 50.0, 20, True)
    sala_standard = ReservaSalas("Sala Estándar", 30.0, 10, False)
    alquiler_laptops = AlquilerEquipos("Alquiler de Laptops", 15.0, "Laptop Dell")
    asesoria_redes = AsesoriaEspecializada("Consultoría en Redes", 80.0, "Redes", "avanzado")
    asesoria_datos = AsesoriaEspecializada("Análisis de Datos", 60.0, "Big Data", "intermedio")
    
    sistema.agregar_servicio(sala_vip)
    sistema.agregar_servicio(sala_standard)
    sistema.agregar_servicio(alquiler_laptops)
    sistema.agregar_servicio(asesoria_redes)
    sistema.agregar_servicio(asesoria_datos)
    print("✓ 5 servicios creados correctamente")

    print("\nCreando reservas de ejemplo (incluyendo algunas con errores)...")

    try:
        r1 = sistema.crear_reserva(1, 1, 3)  # Cliente 1, Sala VIP, 3 horas
        r1.confirmar()
        print(f"✓ Reserva #{r1.get_id()} - Cliente: {r1.get_cliente().get_nombre()} - Servicio: {r1.get_servicio().get_nombre()} - Costo: ${r1.get_costo_total()}")
    except Exception as e:
        print(f"✗ Error en reserva 1: {e}")
 
    try:
        r2 = sistema.crear_reserva(2, 3, 5, cantidad=3)  # Cliente 2, laptops, 5 días, 3 equipos
        print(f"✓ Reserva #{r2.get_id()} - Cliente: {r2.get_cliente().get_nombre()} - Servicio: {r2.get_servicio().get_nombre()} - Costo: ${r2.get_costo_total()}")
    except Exception as e:
        print(f"✗ Error en reserva 2: {e}")

    try:
        r3 = sistema.crear_reserva(3, 4, 2)  # Cliente 3, asesoría redes, 2 horas
        r3.confirmar()
        print(f"✓ Reserva #{r3.get_id()} - Cliente: {r3.get_cliente().get_nombre()} - Servicio: {r3.get_servicio().get_nombre()} - Costo: ${r3.get_costo_total()}")
    except Exception as e:
        print(f"✗ Error en reserva 3: {e}")

    try:
        r_invalida1 = sistema.crear_reserva(99, 1, 2)
        print("✗ Esto no debería aparecer: se creó reserva con cliente inexistente")
    except Exception as e:
        print(f"✓ (Error esperado) No se pudo crear reserva con cliente inexistente: {e}")

    try:
        r_invalida2 = sistema.crear_reserva(1, 99, 2)
        print("✗ Esto no debería aparecer: se creó reserva con servicio inexistente")
    except Exception as e:
        print(f"✓ (Error esperado) No se pudo crear reserva con servicio inexistente: {e}")

    try:
        r_invalida3 = sistema.crear_reserva(1, 1, -5)
        print("✗ Esto no debería aparecer: se creó reserva con duración negativa")
    except Exception as e:
        print(f"✓ (Error esperado) No se pudo crear reserva con duración negativa: {e}")
    
    print("\n=== CARGA DE DATOS COMPLETADA ===\n")
    print("El sistema está listo para usarse. Todos los errores fueron registrados en el log.")
    print(f"Revisa el archivo '{LOG_FILE}' para ver el registro de eventos.\n")
# ----------------------------------------------------------------------------
# 12. PUNTO DE ENTRADA PRINCIPAL (donde empieza todo)
# ----------------------------------------------------------------------------
if __name__ == "__main__":

    print("=" * 70)
    print("SOFTWARE FJ - SISTEMA DE GESTIÓN")
    print("=" * 70)
    print("Iniciando el sistema...")
    
    sistema = SistemaGestion()
    cargar_datos_ejemplo(sistema)
    
    # Mostramos un resumen en consola
    resumen = sistema.obtener_resumen()
    print("\n--- RESUMEN INICIAL DEL SISTEMA ---")
    print(f"Clientes: {resumen['clientes']}")
    print(f"Reservas totales: {resumen['reservas']}")
    print(f"Ingresos confirmados: ${resumen['ingresos']}")
    print("-" * 40)
    print("\n🖥️ Abriendo interfaz gráfica...")
    print("Si no ves la ventana, revisa que tengas instalado Tkinter.")
    print("Puedes cerrar la ventana cuando termines.\n")
    
    # Creamos la aplicación con interfaz gráfica
    app = AplicacionTkinter(sistema)
    app.ejecutar()
    
    # Cuando se cierra la ventana, el programa termina
    print("\nPrograma finalizado.")
