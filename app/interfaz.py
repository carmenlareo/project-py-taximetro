import tkinter as tk
from tkinter import messagebox
from app.autenticacion import GestorAutenticacion
from app.taximetro import TaximetroMVP

class VentanaLogin:
    """Ventana gráfica de inicio de sesión segura."""
    def __init__(self, root):
        self.root = root
        self.root.title("Taxímetro - Acceso Seguro")
        self.root.geometry("400x300")
        self.root.config(bg="#f0f0f0")
        
        self.auth = GestorAutenticacion()

        lbl_titulo = tk.Label(root, text="🔒 Acceso Restringido", font=("Arial", 16, "bold"), bg="#f0f0f0")
        lbl_titulo.pack(pady=20)

        lbl_pass = tk.Label(root, text="Introduce la contraseña:", font=("Arial", 12), bg="#f0f0f0")
        lbl_pass.pack(pady=5)

        self.entry_pass = tk.Entry(root, show="*", font=("Arial", 14), justify="center")
        self.entry_pass.pack(pady=10, ipady=5, ipadx=10)
        self.entry_pass.focus()
        self.entry_pass.bind("<Return>", lambda event: self.intentar_login())

        btn_login = tk.Button(root, text="ENTRAR", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", 
                              width=15, height=2, command=self.intentar_login)
        btn_login.pack(pady=15)

    def intentar_login(self):
        password = self.entry_pass.get()
        if self.auth.verificar_password(password):
            messagebox.showinfo("Éxito", "✅ Acceso autorizado.")
            self.root.destroy()
            iniciar_aplicacion_principal()
        else:
            messagebox.showerror("Error", "❌ Contraseña incorrecta.")
            self.entry_pass.delete(0, tk.END)


class VentanaTaximetro:
    """Interfaz gráfica principal conectada a TaximetroMVP para mantener la consistencia en los logs."""
    def __init__(self, root):
        self.root = root
        self.root.title("Taxímetro Digital - Panel de Control")
        self.root.geometry("650x550")
        self.root.config(bg="#ffffff")

        # Instancia de la lógica de negocio oficial (Fuente de la verdad y logs)
        self.taximetro_logica = TaximetroMVP()
        
        # Variables de control visual en GUI
        self.carrera_activa = False
        self.tiempo_segundos = 0
        self.importe_total = 0.0
        self.estado_actual = "INACTIVO"

        # --- Panel Superior: Estado ---
        self.lbl_estado = tk.Label(root, text="[ESPERA | Sin carrera activa]", font=("Arial", 14, "bold"), bg="#ffeb3b", fg="#333", pady=10)
        self.lbl_estado.pack(fill=tk.X, padx=10, pady=10)

        # --- Panel Central: Importe y Métricas ---
        frame_metricas = tk.Frame(root, bg="#f9f9f9", bd=2, relief=tk.GROOVE)
        frame_metricas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame_metricas, text="IMPORTE ACTUAL", font=("Arial", 12), bg="#f9f9f9", fg="#666").pack(pady=5)
        self.lbl_importe = tk.Label(frame_metricas, text="0.00 €", font=("Arial", 40, "bold"), bg="#f9f9f9", fg="#2196F3")
        self.lbl_importe.pack(pady=10)

        self.lbl_info = tk.Label(frame_metricas, text="Tiempo: 0s | Distancia: 0.0 km", font=("Arial", 14), bg="#f9f9f9")
        self.lbl_info.pack(pady=10)

        # --- Panel Inferior: Botones Táctiles Grandes ---
        frame_botones = tk.Frame(root, bg="#ffffff")
        frame_botones.pack(fill=tk.X, padx=10, pady=15)

        btn_iniciar = tk.Button(frame_botones, text="🏁 Iniciar", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=12, height=2, command=self.cmd_iniciar)
        btn_iniciar.grid(row=0, column=0, padx=5, pady=5)

        btn_parado = tk.Button(frame_botones, text="⏸ Parado", font=("Arial", 12, "bold"), bg="#FF9800", fg="white", width=12, height=2, command=self.cmd_parado)
        btn_parado.grid(row=0, column=1, padx=5, pady=5)

        btn_movimiento = tk.Button(frame_botones, text="🚗 Movimiento", font=("Arial", 12, "bold"), bg="#00BCD4", fg="white", width=12, height=2, command=self.cmd_movimiento)
        btn_movimiento.grid(row=0, column=2, padx=5, pady=5)

        btn_fin = tk.Button(frame_botones, text="🛑 Finalizar", font=("Arial", 12, "bold"), bg="#F44336", fg="white", width=12, height=2, command=self.cmd_fin)
        btn_fin.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

        # Bucle de actualización en tiempo real no bloqueante
        self.actualizar_tiempo_real()

    def cmd_iniciar(self):
        # Llama al método real de la lógica para registrar el inicio en el log
        if hasattr(self.taximetro_logica, 'iniciar_carrera'):
            self.taximetro_logica.iniciar_carrera()
        
        self.carrera_activa = True
        self.tiempo_segundos = 0
        self.importe_total = 0.0
        self.estado_actual = "MOVIMIENTO"
        self.lbl_estado.config(text="[EN CURSO | Movimiento]", bg="#00BCD4")

    def cmd_parado(self):
        if self.carrera_activa:
            self.estado_actual = "PARADO"
            if hasattr(self.taximetro_logica, 'cambiar_estado'):
                self.taximetro_logica.cambiar_estado('parado')
            self.lbl_estado.config(text="[PARADO (Tarifa espera)]", bg="#FF9800")

    def cmd_movimiento(self):
        if self.carrera_activa:
            self.estado_actual = "MOVIMIENTO"
            if hasattr(self.taximetro_logica, 'cambiar_estado'):
                self.taximetro_logica.cambiar_estado('movimiento')
            self.lbl_estado.config(text="[EN MOVIMIENTO (Tarifa ruta)]", bg="#00BCD4")

    def cmd_fin(self):
        if self.carrera_activa:
            # Llama al método final para cerrar tramos, calcular el total y escribir en taximetro.log
            if hasattr(self.taximetro_logica, 'finalizar_carrera'):
                self.taximetro_logica.finalizar_carrera()
            
            self.carrera_activa = False
            self.lbl_estado.config(text="[CARRERA FINALIZADA]", bg="#E91E63")
            messagebox.showinfo("Resumen de Carrera", "La carrera ha finalizado y se ha registrado correctamente en los logs.")
            
            # Resetear pantalla
            self.tiempo_segundos = 0
            self.importe_total = 0.0
            self.lbl_importe.config(text="0.00 €")
            self.lbl_info.config(text="Tiempo: 0s | Distancia: 0.0 km")
            self.lbl_estado.config(text="[ESPERA | Sin carrera activa]", bg="#ffeb3b")

    def actualizar_tiempo_real(self):
        """Actualiza la visualización de la tablet segundo a segundo de forma fluida."""
        if self.carrera_activa:
            self.tiempo_segundos += 1
            
            if self.estado_actual == "PARADO":
                self.importe_total += getattr(self.taximetro_logica, 'TARIFA_PARADO', 0.02)
            else:
                self.importe_total += getattr(self.taximetro_logica, 'TARIFA_MOVIMIENTO', 0.05)

            self.lbl_importe.config(text=f"{self.importe_total:.2f} €")
            self.lbl_info.config(text=f"Tiempo: {self.tiempo_segundos}s | Distancia: {(self.tiempo_segundos * 0.01):.1f} km")

        self.root.after(1000, self.actualizar_tiempo_real)


def iniciar_aplicacion_principal():
    root_app = tk.Tk()
    app = VentanaTaximetro(root_app)
    root_app.mainloop()