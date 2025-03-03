from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Configuración de colores y estilos
CONFIGURACION = {
    # Colores de las líneas del triángulo
    'COLOR_LINEA_AB': 'black',  # Rojo
    'COLOR_LINEA_BC': 'black',  # Verde
    'COLOR_LINEA_CA': 'black',  # Azul
    
    # Grosor de las líneas
    'GROSOR_LINEAS': 1.0,
    
    # Color y transparencia del relleno del triángulo
    'COLOR_RELLENO': '#10ebe1',
    'TRANSPARENCIA_RELLENO': 0.8,  # 0 = transparente, 1 = sólido
    
    # Colores del fondo y la cuadrícula
    'COLOR_FONDO': '#FFFDD0',
    'COLOR_GRID': '#CCCCCC',
    'ESTILO_GRID': '--',  # '--' para punteado, '-' para sólido
    
    # Colores y tamaños del texto
    'COLOR_TEXTO': 'black',
    'TAMANO_TEXTO': 10,
    
    # Tamaño de los puntos en los vértices
    'TAMANO_PUNTOS': 5
}

def crear_grafica_base():
    plt.figure(figsize=(12, 12))
    plt.xlim(0, 950)
    plt.ylim(0, 600)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().set_facecolor(CONFIGURACION['COLOR_FONDO'])
    plt.xticks(np.arange(0, 951, 50))
    plt.yticks(np.arange(0, 601, 50))
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True, linestyle=CONFIGURACION['ESTILO_GRID'], color=CONFIGURACION['COLOR_GRID'])
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    if not os.path.exists("static"):
        os.makedirs("static")
    plt.savefig("static/grafica_base.png", bbox_inches='tight', pad_inches=0)
    plt.close()

def dda_line(x1, y1, x2, y2):
    puntos = []
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        puntos.append({"x": x1, "y": y1})
        return puntos

    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x1, y1

    for _ in range(steps + 1):
        puntos.append({"x": round(x), "y": round(y)})
        x += x_inc
        y += y_inc

    return puntos

@app.route('/generar_triangulo', methods=['POST'])
def generar_triangulo():
    datos = request.json
    x1, y1 = datos["x1"], datos["y1"]
    x2, y2 = datos["x2"], datos["y2"]
    x3, y3 = datos["x3"], datos["y3"]
    
    puntos_ab = dda_line(x1, y1, x2, y2)
    puntos_bc = dda_line(x2, y2, x3, y3)
    puntos_ca = dda_line(x3, y3, x1, y1)
    
    def calcular_pendiente(x1, y1, x2, y2):
        return (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else "indefinida"
    
    pendiente_ab = calcular_pendiente(x1, y1, x2, y2)
    pendiente_bc = calcular_pendiente(x2, y2, x3, y3)
    pendiente_ca = calcular_pendiente(x3, y3, x1, y1)
    
    plt.figure(figsize=(12,12))
    plt.xlim(0, 950)
    plt.ylim(0, 600)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().set_facecolor(CONFIGURACION['COLOR_FONDO'])
    plt.xticks(np.arange(0, 951, 50))
    plt.yticks(np.arange(0, 601, 50))
    plt.grid(True, linestyle=CONFIGURACION['ESTILO_GRID'], color=CONFIGURACION['COLOR_GRID'])
    
    vertices = np.array([[x1, y1], [x2, y2], [x3, y3]])
    plt.fill(vertices[:,0], vertices[:,1], 
             CONFIGURACION['COLOR_RELLENO'], 
             alpha=CONFIGURACION['TRANSPARENCIA_RELLENO'])
    
    # Dibujar las líneas del triángulo
    plt.plot([p["x"] for p in puntos_ab], [p["y"] for p in puntos_ab], 
             color=CONFIGURACION['COLOR_LINEA_AB'], 
             linewidth=CONFIGURACION['GROSOR_LINEAS'], 
             label="AB")
    plt.plot([p["x"] for p in puntos_bc], [p["y"] for p in puntos_bc], 
             color=CONFIGURACION['COLOR_LINEA_BC'], 
             linewidth=CONFIGURACION['GROSOR_LINEAS'], 
             label="BC")
    plt.plot([p["x"] for p in puntos_ca], [p["y"] for p in puntos_ca], 
             color=CONFIGURACION['COLOR_LINEA_CA'], 
             linewidth=CONFIGURACION['GROSOR_LINEAS'], 
             label="CA")
    
    # Agregar puntos en los vértices
    plt.scatter([x1, x2, x3], [y1, y2, y3], 
                color='black', 
                s=CONFIGURACION['TAMANO_PUNTOS'])
    
    # Agregar etiquetas de los vértices
    plt.annotate(f'A({x1},{y1})', (x1, y1), 
                textcoords="offset points", 
                xytext=(0,10), 
                ha='center', 
                color=CONFIGURACION['COLOR_TEXTO'], 
                size=CONFIGURACION['TAMANO_TEXTO'])
    plt.annotate(f'B({x2},{y2})', (x2, y2), 
                textcoords="offset points", 
                xytext=(0,10), 
                ha='center', 
                color=CONFIGURACION['COLOR_TEXTO'], 
                size=CONFIGURACION['TAMANO_TEXTO'])
    plt.annotate(f'C({x3},{y3})', (x3, y3), 
                textcoords="offset points", 
                xytext=(0,10), 
                ha='center', 
                color=CONFIGURACION['COLOR_TEXTO'], 
                size=CONFIGURACION['TAMANO_TEXTO'])
    
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    plt.savefig("static/grafica_triangulo.png", bbox_inches='tight', pad_inches=0)
    plt.close()
    
    return jsonify({
        "puntos_ab": puntos_ab,
        "puntos_bc": puntos_bc,
        "puntos_ca": puntos_ca,
        "pendientes": {
            "AB": pendiente_ab,
            "BC": pendiente_bc,
            "CA": pendiente_ca
        }
    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    crear_grafica_base()
    app.run(debug=True)
