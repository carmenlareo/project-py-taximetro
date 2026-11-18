import hashlib
import hmac
import os
import json


class GestorAutenticacion:
    """
    Clase responsable única de la seguridad. 
    Gestiona la carga y validación de credenciales desde un archivo JSON externo.
    """
    def __init__(self, ruta_archivo: str = "data/credenciales.json"):
        self.ruta_archivo = ruta_archivo
        self._cargar_o_crear_credenciales()

    def _cargar_o_crear_credenciales(self):
        """Carga las credenciales desde el JSON o las crea por defecto si no existen."""
        # 1. Asegurarse de que la carpeta 'data' exista
        directorio = os.path.dirname(self.ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)

        # 2. Si el archivo de credenciales existe, los leemos
        if os.path.exists(self.ruta_archivo):
            with open(self.ruta_archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                self.salt = bytes.fromhex(datos["salt"])
                self.hash_almacenado = bytes.fromhex(datos["hash"])
        else:
            # 3. Si no existe, creamos credenciales iniciales por defecto (Contraseña: "1234")
            self.salt = os.urandom(16)
            self.hash_almacenado = hashlib.pbkdf2_hmac(
                'sha256', b'taxi1234', self.salt, 100000
            )
            
            # Guardamos los valores en formato hexadecimal dentro del JSON
            datos = {
                "salt": self.salt.hex(),
                "hash": self.hash_almacenado.hex()
            }
            with open(self.ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4)
            print(f"⚠️ Archivo de credenciales creado automáticamente en '{self.ruta_archivo}' (Contraseña por defecto: 1234)")

    def verificar_password(self, password_ingresada: str) -> bool:
        """Compara la contraseña introducida con el hash seguro del archivo."""
        nuevo_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password_ingresada.encode('utf-8'), 
            self.salt, 
            100000
        )
        return hmac.compare_digest(nuevo_hash, self.hash_almacenado)

    def solicitar_inicio_sesion(self, max_intentos: int = 3) -> bool:
        """Gestiona la interacción de la terminal para solicitar la contraseña."""
        intentos = max_intentos
        while intentos > 0:
            password = input("🔒 Introduce la contraseña de seguridad para iniciar el taxímetro: ")
            if self.verificar_password(password):
                print("✅ Acceso autorizado. ¡Bienvenido!")
                return True
            intentos -= 1
            print(f"❌ Contraseña incorrecta. Intentos restantes: {intentos}")
        
        print("🚫 Acceso bloqueado por seguridad. Demasiados intentos fallidos.")
        return False