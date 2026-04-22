import json
import os
import datetime


def confirmacion(func):
    def envoltura(*args, **kwargs):
        # 1. Esto le da valor al decorador:
        ahora = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{ahora}] Intentando ejecutar: {func.__name__}")
        
        # 2. Se ejecuta la función real
        resultado = func(*args, **kwargs)
        
        # 3. Confirmación de salida
        print(f"[{ahora}] {func.__name__} finalizada con éxito.")
        
        return resultado
    return envoltura


class Producto:
    def __init__(self, codigo: int, nombre: str, precio: float, stock: int, descripcion: str):
        self.codigo = codigo           # Entero (int)
        self.nombre = nombre           # Texto (str)
        self.precio = precio           # Decimal (float)
        self.stock = stock             # Entero (int)
        self.descripcion = descripcion # Texto (str)
    
    def a_diccionario(self):
        return{
            "codigo" : self.codigo,
            "nombre" : self.nombre,
            "precio" : self.precio,
            "stock" : self.stock,
            "descripcion" : self.descripcion
        }

class GestorInventario:
    def __init__(self, ruta_archivo: str):
        # Guardamos la ruta del archivo que vamos a usar
        self.archivo = ruta_archivo

    @confirmacion  # <-- Aquí usamos tu vigilante
    def cargar_datos(self):
        try:
            # Intentamos abrir el archivo en modo lectura ('r')
            with open(self.archivo, 'r', encoding='utf-8') as f:
                 return json.load(f)
        
        except FileNotFoundError:
            # Si el archivo no existe (primera vez que corre la app)
            print("Aviso: No se encontró el archivo, iniciando inventario vacío.")
            return []
            
        except json.JSONDecodeError:
            # Si el archivo existe pero está mal escrito o dañado
            print("Error: El archivo está corrupto. Iniciando lista vacía.")
            return []
        
    @confirmacion
    def guardar_datos(self, lista_productos):
        try:
            # Abrimos el archivo en modo escritura ('w')
            # Esto sobreescribe el archivo con la nueva información actualizada
            with open(self.archivo, 'w') as f:
                # El parámetro 'indent=4' hace que el archivo sea legible para humanos
                json.dump(lista_productos, f, indent=4)
                
        except IOError as e:
            # Este error ocurre si, por ejemplo, el disco está lleno o no tienes permisos
            print(f"Error crítico al guardar los datos: {e}")