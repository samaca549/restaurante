import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

# =======================================================
# CONFIGURACIÓN
# =======================================================

SERVICE_ACCOUNT_PATH = 'serviceAccountKey.json'

# =======================================================
# DATOS DEL MENÚ (Tus 4 Productos Reales)
# =======================================================

PLATO_MENU_INICIAL = [
    {
        "id": "Platos Fuertes",
        "nombre": "Hamburguesa Clásica",
        "precio": 15000,
        "descripcion": "Carne de res 150g, queso cheddar, lechuga, tomate y salsas.",
        "categoria": "Platos Fuertes"
    },
    {
        "id": "ensalada_cesar_con_pollo",
        "nombre": "Ensalada César con Pollo",
        "precio": 18000,
        "descripcion": "Lechuga romana, pechuga de pollo grillada, crutones, parmesano y aderezo.",
        "categoria": "Ensaladas"
    },
    {
        "id": "papas_fritas_medianas",
        "nombre": "Papas Fritas Medianas",
        "precio": 8000,
        "descripcion": "Porción de papas bastón crujientes con sal.",
        "categoria": "Entradas"
    },
    {
        "id": "tacos_al_pastor_3_pzas",
        "nombre": "Tacos al Pastor (3 pzas)",
        "precio": 12000,
        "descripcion": "Tres tacos de cerdo marinado con piña, cilantro y cebolla.",
        "categoria": "Platos Fuertes"
    },
]

# =======================================================
# INVENTARIO
# =======================================================

INVENTARIO_INICIAL = [
    {"id": "pan_hamburguesa", "nombre": "Pan de Hamburguesa", "cantidad": 50.0, "unidad": "unidad", "minimo": 20},
    {"id": "carne_res", "nombre": "Carne de Res Molida", "cantidad": 10.0, "unidad": "kg", "minimo": 5},
    {"id": "queso_cheddar", "nombre": "Queso Cheddar", "cantidad": 2.0, "unidad": "kg", "minimo": 1},

    {"id": "lechuga_romana", "nombre": "Lechuga Romana", "cantidad": 15.0, "unidad": "unidad", "minimo": 5},
    {"id": "pechuga_pollo", "nombre": "Pechuga de Pollo", "cantidad": 8.0, "unidad": "kg", "minimo": 3},
    {"id": "aderezo_cesar", "nombre": "Aderezo César", "cantidad": 3.0, "unidad": "lt", "minimo": 1},

    {"id": "papas_baston", "nombre": "Papas Bastón Congeladas", "cantidad": 20.0, "unidad": "kg", "minimo": 10},
    {"id": "aceite_freir", "nombre": "Aceite para Freír", "cantidad": 10.0, "unidad": "lt", "minimo": 5},

    {"id": "tortillas_maiz", "nombre": "Tortillas de Maíz", "cantidad": 100.0, "unidad": "unidad", "minimo": 50},
    {"id": "carne_cerdo_pastor", "nombre": "Carne de Cerdo (Pastor)", "cantidad": 6.0, "unidad": "kg", "minimo": 2},
    {"id": "pina_fresca", "nombre": "Piña Fresca", "cantidad": 3.0, "unidad": "unidad", "minimo": 1},
]

# =======================================================
# EMPLEADOS (Como en tu imagen – ID automático)
# =======================================================

empleados = [
    {
        "email": "bryandavid2109@gmail.com",
        "rol": "gerente"
    }
]

# =======================================================
# INICIALIZAR FIREBASE
# =======================================================

def inicializar_firebase():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f" ERROR: No encuentro el archivo '{SERVICE_ACCOUNT_PATH}'.")
        return None
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f" Error conectando a Firebase: {e}")
        return None

# =======================================================
# FUNCIÓN PARA CARGAR COLECCIONES
# =======================================================

def cargar_datos(db, coleccion, lista_datos):
    print(f"\n--- Cargando colección: '{coleccion}' ---")
    batch = db.batch()

    # Eliminar documentos anteriores
    docs = db.collection(coleccion).stream()
    for doc in docs:
        batch.delete(doc.reference)

    # Agregar nuevos documentos
    for item in lista_datos:
        if "id" in item:
            doc_ref = db.collection(coleccion).document(item["id"])
        else:
            doc_ref = db.collection(coleccion).document()  # ID automático
        batch.set(doc_ref, item)

    batch.commit()
    print(f" {len(lista_datos)} items actualizados en '{coleccion}'.")

# =======================================================
# EJECUCIÓN PRINCIPAL
# =======================================================

if __name__ == "__main__":
    print("Iniciando script de población de base de datos...")
    db = inicializar_firebase()

    if db:

        cargar_datos(db, "platos", PLATO_MENU_INICIAL)
        cargar_datos(db, "inventario", INVENTARIO_INICIAL)
        cargar_datos(db, "empleados", empleados)

        print("\n ¡BASE DE DATOS ACTUALIZADA CON ÉXITO!")
        print("Ahora puedes abrir tu app y verás el menú correcto.")
