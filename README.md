## 📋 Descripción General

Este proyecto es una aplicación de escritorio desarrollada en Python utilizando un patrón de arquitectura (presentaion_domain_ui_data). No solo permite gestionar pedidos e inventarios, sino que integra un **"Cerebro Digital"** que analiza datos en tiempo real para sugerir estrategias de venta, alertar sobre quiebres de stock críticos y responder consultas financieras complejas.
<img width="1213" height="912" alt="{08427FD0-652A-4796-8786-C33D280EEA8B}" src="https://github.com/user-attachments/assets/3d3e52fd-99c7-429a-9c2e-cc8522c3b367" />
1. Seguridad y Gestión de Roles
El sistema inicia con una ventana de **Login** validada contra base de datos, dirigiendo al usuario a su interfaz correspondiente:

* **👨‍💼 Perfil Gerente (Admin):**
    * **Visión Total:** Acceso irrestricto a todos los módulos.
    * **Toma de Decisiones:** Único rol con acceso al *Dashboard Financiero* y al *Chatbot con IA* para estrategias de negocio.
    * **Control de Stock:** Capacidad para auditar y modificar el inventario.

* **💁‍♂️ Perfil Mesero (Operativo):**
    * **Interfaz Focalizada:** Acceso exclusivo al módulo de *Pedidos*.
    * **Seguridad:** Bloqueo de funciones críticas (Finanzas/Inventario) para evitar errores o manipulaciones no autorizadas.
    * **UX Ágil:** Diseño simplificado para máxima velocidad en la toma de órdenes.
<img width="1273" height="715" alt="{414411C8-818D-45AD-B6D8-5AF83B8FFE9D}" src="https://github.com/user-attachments/assets/ee9526e8-a516-43df-a6d6-7eb9b9d06192" />
<img width="1265" height="945" alt="{E6D4EBE9-E421-424D-9AFA-CD87F3979684}" src="https://github.com/user-attachments/assets/275bf0a2-4d93-43d5-819e-3ad9ef9ecbff" />
### 1. 🍔 Módulo de Pedidos (Punto de Venta)
Una interfaz visual e intuitiva para la toma de pedidos.
* **Menú Visual:** Tarjetas de productos con imágenes y control de cantidad (+/-).
* **Neuromarketing con IA:** Un widget inteligente analiza el menú y sugiere una "Promo Flash" con frases persuasivas generadas por IA para impulsar la venta de productos específicos.
* **Carrito en Tiempo Real:** Cálculo automático de totales y visualización detallada del ticket.
<img width="1912" height="1019" alt="{BD04505F-9A6D-4272-9B55-F5E1E889AD69}" src="https://github.com/user-attachments/assets/939f5f90-ab14-4ec0-9fe6-d41e415afa92" />
<img width="1852" height="1015" alt="{28696FC5-067A-403E-8288-FCDA2FA62928}" src="https://github.com/user-attachments/assets/84600212-fc90-498d-8363-88cc94140874" />
* ### 2. 📦 Gestión de Inventario Inteligente
Control total sobre los insumos del restaurante.
* **CRUD Completo:** Crear, leer y actualizar stock de insumos.
* **Búsqueda y Filtrado:** Barra de búsqueda en tiempo real.
* **Auditoría de Stock con IA:**
    * Detecta niveles críticos basándose en benchmarks gastronómicos (ej. diferencia entre Kilos y Unidades).
    * Genera alertas de "Pánico" si un insumo vital (como la carne o el pan) está por agotarse.
    * Compara productos nuevos con estándares de la industria automáticamente.
<img width="1520" height="867" alt="{E2DEB44F-C057-4728-911E-BB1127B2DEED}" src="https://github.com/user-attachments/assets/3b54969c-6984-4ddd-8914-c5a9497d67ef" />
<img width="1920" height="590" alt="{89DF2C36-524A-44F5-8753-967A1391FD37}" src="https://github.com/user-attachments/assets/8a4bf79a-a72b-4f07-b0c9-0a999940db92" />
<img width="1856" height="924" alt="{33962313-BBD4-44FF-9F17-C2E20C9A3BAA}" src="https://github.com/user-attachments/assets/5aa0e0d9-542d-4d8e-b2bc-bd0b44822b8d" />
<img width="1920" height="1002" alt="{1BB9B261-9F10-482A-A4D4-5909874DB352}" src="https://github.com/user-attachments/assets/e6288a51-9487-407d-a892-c0fbfae41ff0" />
## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica (GUI):** Tkinter (con estilos `ttk` personalizados).
* **Base de Datos:** Google Cloud Firestore (NoSQL).
* **Inteligencia Artificial:** Google Generative AI (`gemini-2.0-flash`).
* **Gráficos:** Matplotlib.
* **Manejo de Imágenes:** Pillow (PIL).
* **Arquitectura:** MVVM (Separación lógica entre UI, Lógica de Negocio y Datos).

---

## ⚙️ Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/restaurante-ai.git](https://github.com/tu-usuario/restaurante-ai.git)
    cd restaurante-ai
    ```

2.  **Crear entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Asegúrate de incluir: `google-generativeai`, `firebase-admin`, `matplotlib`, `pillow`)*

4.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` o configura en tu sistema:
    * `GEMINI_API_KEY`: Tu API Key de Google AI Studio.
    * `GOOGLE_APPLICATION_CREDENTIALS`: Ruta a tu archivo JSON de Firebase.

5.  **Ejecutar la aplicación:**
    ```bash
    python main.py
    ```
<img width="1266" height="419" alt="{290ED901-31BE-49CB-8A4F-4B5D21A70ACE}" src="https://github.com/user-attachments/assets/42bff0da-ed91-49bd-96e2-86f55b41975d" />
<img width="1920" height="891" alt="{EF9F7F1A-A0D3-4B77-AC66-EC200FB43A7B}" src="https://github.com/user-attachments/assets/75bdc024-2f49-4559-bba5-2062a69769bb" />
### 3. 📈 Dashboard Financiero (Analytics)
Un centro de control para la salud económica del negocio.
* **KPIs en Tiempo Real:** Tarjetas métricas para Ingresos Brutos, Ganancia Neta, Total de Pedidos y Ticket Promedio.
* **Visualización de Datos:**
    * Gráfico de Área (Matplotlib) para tendencias de ventas.
    * Gráfico de Dona para la distribución de productos más vendidos.
* **Chatbot Financiero (CFO Virtual):** Un chat integrado donde puedes preguntar a la IA sobre tus datos (ej: *"¿Cómo puedo mejorar el ticket promedio hoy?"*) y recibir respuestas basadas en tus transacciones reales.
* **Insights Automáticos:** La IA analiza proactivamente las tendencias y muestra consejos o alertas en un widget dedicado.

---
<img width="1901" height="680" alt="{0848ABE6-8D54-4169-AB9F-7F23D1AEE264}" src="https://github.com/user-attachments/assets/3263e0f2-d37f-4c3c-ac28-84c6c90065e9" />
## 🧠 Integración con IA (Prompts Destacados)

El sistema utiliza **Gemini 2.0 Flash** por su velocidad y bajo costo. Algunos de los roles que asume la IA son:

* **Expert en Neuromarketing:** *"Elige el plato que genere más deseo impulsivo y crea una frase sensorial..."*
* **Jefe de Logística:** *"Identifica el insumo MÁS crítico... ten cuidado con las UNIDADES (Kg vs Unid)..."*
* **Gerente Comercial:** *"Dame una estrategia de guerrilla marketing para duplicar estas ventas HOY."*
