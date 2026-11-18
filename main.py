from app.autenticacion import GestorAutenticacion
from app.taximetro import TaximetroMVP

def main():
    # 1. Validamos la seguridad antes de arrancar el taxímetro (Principio SOLID / Responsabilidad Única)
    auth = GestorAutenticacion()
    if not auth.solicitar_inicio_sesion():
        return  # Si la contraseña falla o se agotan los intentos, la app se detiene de forma segura.

    # 2. Si el acceso es correcto, arrancamos el taxímetro con normalidad
    app = TaximetroMVP()
    app.ejecutar()  # El método principal que arranca el bucle del taxímetro

if __name__ == "__main__":
    main()