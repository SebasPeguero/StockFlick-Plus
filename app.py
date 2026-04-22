from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# importar las clases desde logica.py
from logica import Producto, GestorInventario

# Importar la lógica personalizada
from logica import Producto, GestorInventario

# 1. Inicializamos la aplicación FastAPI
app = FastAPI()

# 2. Configuramos la carpeta de archivos estáticos (CSS, Imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. Configuramos el motor de plantillas (HTML)
templates = Jinja2Templates(directory="templates")

# 4. Creamos el gestor de inventario apuntando a tu archivo JSON
gestor = GestorInventario("inventario.json")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # 1. Cargamos los datos
    lista_productos = gestor.cargar_datos()
    
    # 2. Retornamos (fíjate que ahora request va afuera del diccionario también)
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"productos": lista_productos}
    )

# RUTA 2: Formulario para agregar (Vista)
@app.get("/agregar", response_class=HTMLResponse)
async def vista_agregar(request: Request):
    return templates.TemplateResponse(
            request=request, 
            name="agregar.html", 
            context={}
        )

@app.post("/agregar")
async def procesar_formulario(
    codigo: int = Form(...), 
    nombre: str = Form(...), 
    precio: float = Form(...), 
    stock: int = Form(...), 
    descripcion: str = Form(...)
):
    # 1. Cargamos el inventario actual
    lista_actual = gestor.cargar_datos()
    
    # 2. Creamos un nuevo objeto usando tu clase de logica.py
    nuevo_p = Producto(codigo, nombre, precio, stock, descripcion)
    
    # 3. Lo convertimos a diccionario y lo agregamos a la lista
    lista_actual.append(nuevo_p.a_diccionario())
    
    # 4. Guardamos la lista actualizada en el JSON
    gestor.guardar_datos(lista_actual)
    
    # 5. Redirigimos al inventario para ver el cambio
    return RedirectResponse(url="/", status_code=303)

@app.get("/eliminar/{codigo}")
async def eliminar_producto(codigo: int):
    # 1. Cargamos la lista actual
    lista_actual = gestor.cargar_datos()
    
    # 2. Creamos una nueva lista EXCLUYENDO el producto que tiene ese código
    # Esto es como "filtrar" el inventario
    lista_nueva = [p for p in lista_actual if p['codigo'] != codigo]
    
    # 3. Guardamos la nueva lista en el archivo JSON
    gestor.guardar_datos(lista_nueva)
    
    # 4. Redirigimos al inicio para ver que ya no está
    return RedirectResponse(url="/", status_code=303)

from fastapi.responses import FileResponse

@app.get("/exportar")
async def exportar_datos():
    return FileResponse(path="inventario.json", filename="respaldo_inventario.json")

# RUTA PARA MOSTRAR EL FORMULARIO DE EDICIÓN
@app.get("/editar/{codigo}", response_class=HTMLResponse)
async def vista_editar(request: Request, codigo: int):
    lista = gestor.cargar_datos()
    # Buscamos el producto específico para llenar los campos del formulario
    producto = next((p for p in lista if p['codigo'] == codigo), None)
    
    if not producto:
        return RedirectResponse(url="/", status_code=303)
        
    return templates.TemplateResponse(
        request=request, 
        name="editar.html", 
        context={"producto": producto}
    )

# RUTA PARA PROCESAR LOS CAMBIOS (POST)
@app.post("/editar/{codigo_original}")
async def procesar_edicion(
    codigo_original: int, 
    codigo: int = Form(...), 
    nombre: str = Form(...), 
    precio: float = Form(...), 
    stock: int = Form(...), 
    descripcion: str = Form(...)
):
    lista = gestor.cargar_datos()
    # Buscamos el producto por su código original y actualizamos sus datos
    for p in lista:
        if p['codigo'] == codigo_original:
            p.update({
                "codigo": codigo,
                "nombre": nombre,
                "precio": precio,
                "stock": stock,
                "descripcion": descripcion
            })
            break
            
    gestor.guardar_datos(lista)
    return RedirectResponse(url="/", status_code=303)