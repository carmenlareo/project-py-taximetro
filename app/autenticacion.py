import hashlib
import hmac
import os

class GestorAutenticacion:
    """
    Clase responsable única de la seguridad y autenticación (Principio SOLID).
    Maneja el hash de contraseñas con PBKDF2 y sal (salt).
    """
    def __init__(self, salt_hex: str = None, hash_hex: str = None):
        # Si no se pasan credenciales, generamos una sal por defecto y un hash para "1234"
        self.salt = bytes.fromhex(salt_hex) if salt_hex else os.urandom(16)
        self.hash_almacenado = bytes.fromhex(hash_hex) if hash_hex else hashlib.pbkdf2_hmac(
            'sha256', b'taxi1234', self.salt, 100000
        )

    def verificar_password(self, password_ingresada: str) -> bool:
        """Compara la contraseña introducida con el hash seguro almacenado."""
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