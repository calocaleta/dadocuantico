"""
Dado Cuántico Interactivo
-------------------------
Este programa implementa un "Dado Cuántico" interactivo como una herramienta educativa
para la visualización y comprensión de conceptos básicos de computación cuántica.

El sistema utiliza la biblioteca Qiskit para construir un circuito cuántico de 3 qubits,
preparados inicialmente en un estado de superposición mediante puertas Hadamard.
La medición del circuito colapsa el sistema a uno de los estados posibles (0 a 7),
pero solo consideramos los resultados 0 a 5 (para simular un dado de 6 caras).

La interfaz gráfica está implementada en Tkinter y visualiza las caras del dado en estado
de superposición (mediante imágenes semitransparentes vibrando aleatoriamente) y
colapsa gráficamente al estado seleccionado al presionar el botón de medición.

Puede usarse como base para proyectos de investigación y desarrollo en tecnologías cuánticas.


Autor: Ing. Carlos Alfonso Garcia Gonzales
CIP 199025 – Ingeniero Informático
Lima - Perú
"""

import tkinter as tk
from PIL import Image, ImageTk
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import os
import random

# Inicializa el simulador cuántico (usamos el backend clásico qasm_simulator)
sim = Aer.get_backend('qasm_simulator')

# Configura la ventana principal de la interfaz gráfica
root = tk.Tk()
root.title("Dado Cuántico")
root.geometry("400x400")
root.resizable(False, False)

# Carga las imágenes de las 6 caras del dado desde el directorio actual
img_dir = os.path.dirname(__file__)
faces = [
    Image.open(os.path.join(img_dir, f'dado{i}.png')).convert('RGBA')
    for i in range(1, 7)
]
# Redimensiona todas las imágenes a un tamaño uniforme
size = (200, 200)
faces = [f.resize(size, Image.Resampling.LANCZOS) for f in faces]

def create_transparent_faces():
    """
    Genera una versión semitransparente de cada cara del dado para
    representar gráficamente la superposición cuántica.
    """
    transparent_faces = []
    for face in faces:
        transparent = face.copy()
        alpha = transparent.split()[3]
        # Reduce la opacidad al 30% (simboliza la incertidumbre)
        alpha = alpha.point(lambda p: int(p * 0.3))
        transparent.putalpha(alpha)
        transparent_faces.append(transparent)
    return transparent_faces

# Prepara las imágenes iniciales en estado de superposición (transparente)
transparent_faces = create_transparent_faces()

# Crea el canvas principal donde se mostrarán las imágenes
canvas = tk.Canvas(root, width=400, height=350, bg='white')
canvas.place(x=0, y=0)

# Inicializa todas las imágenes del dado como invisibles al principio
invisible = Image.new('RGBA', faces[0].size, (0, 0, 0, 0))
invisible_tk = ImageTk.PhotoImage(invisible)
image_items = []
positions = []
image_refs = []

# Coloca las imágenes invisibles en el centro del canvas
for _ in transparent_faces:
    item = canvas.create_image(200, 175, image=invisible_tk)
    image_items.append(item)
    positions.append([200, 175])
    image_refs.append(invisible_tk)

# Estado inicial: sin vibración ni circuito cuántico creado
vibrating = False
compiled_circuit = None

def animate():
    """
    Función que actualiza continuamente la posición de las imágenes
    para simular vibración aleatoria en estado de superposición.
    """
    if not vibrating:
        return
    for i, (x, y) in enumerate(positions):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        positions[i][0] += dx
        positions[i][1] += dy
        # Limita el rango de movimiento cerca del centro
        positions[i][0] = min(max(positions[i][0], 190), 210)
        positions[i][1] = min(max(positions[i][1], 165), 185)
        canvas.coords(image_items[i], positions[i][0], positions[i][1])
    root.after(50, animate)

def lanzamiento_cuantico():
    """
    Prepara el circuito cuántico y activa la visualización en superposición.
    El circuito aplica puertas Hadamard a 3 qubits, creando superposición uniforme.
    Luego prepara las imágenes transparentes y activa la animación de vibración.
    """
    global vibrating, compiled_circuit
    vibrating = True

    # Construye el circuito cuántico de 3 qubits con Hadamard + medición
    qc = QuantumCircuit(3, 3)
    qc.h([0, 1, 2])
    qc.measure([0, 1, 2], [0, 1, 2])
    compiled_circuit = transpile(qc, sim)
    print("Circuito cuántico preparado (superposición activa)")

    # Muestra las imágenes transparentes para representar la superposición
    new_transparent_faces = create_transparent_faces()
    new_tk_images = [ImageTk.PhotoImage(img) for img in new_transparent_faces]
    for i in range(6):
        canvas.itemconfig(image_items[i], image=new_tk_images[i])
        image_refs[i] = new_tk_images[i]
        positions[i][0] = 200
        positions[i][1] = 175
        canvas.coords(image_items[i], positions[i][0], positions[i][1])

    # Inicia la animación
    animate()

def tirar_dado():
    """
    Ejecuta la medición del circuito cuántico (colapso del estado).
    El resultado se usa para seleccionar y mostrar una única imagen del dado.
    Las demás imágenes se eliminan visualmente, simbolizando la pérdida de superposición.
    """
    global vibrating
    if compiled_circuit is None:
        print("Circuito no preparado. Presiona 'Lanzamiento Cuántico' primero.")
        return

    vibrating = False

    # Ejecuta la simulación cuántica hasta obtener un número válido (0-5)
    while True:
        job = sim.run(compiled_circuit, shots=1)
        result = job.result()
        bit_string = list(result.get_counts().keys())[0]
        number = int(bit_string, 2)
        if number < 6:
            break

    ganador = number
    print(f"Resultado colapsado: {ganador + 1}")

    # Muestra la imagen correspondiente al número colapsado
    final_img = ImageTk.PhotoImage(faces[ganador])
    canvas.itemconfig(image_items[ganador], image=final_img)
    image_refs[ganador] = final_img

    # Oculta las demás imágenes
    invisible_tk = ImageTk.PhotoImage(Image.new('RGBA', faces[0].size, (0, 0, 0, 0)))
    for i in range(6):
        if i != ganador:
            canvas.itemconfig(image_items[i], image=invisible_tk)
            image_refs[i] = invisible_tk

# Botón para colapsar (medir el circuito cuántico)
boton = tk.Button(root, text="🎲 Colapsar", command=tirar_dado, font=("Arial", 12))
boton.place(x=50, y=360)

# Botón para iniciar la superposición cuántica
boton_lanzamiento = tk.Button(root, text="🔄 Lanzamiento Cuántico", command=lanzamiento_cuantico, font=("Arial", 12))
boton_lanzamiento.place(x=150, y=360)

# Inicia el loop principal de la interfaz
root.mainloop()
