# backend.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app) # Habilita CORS para permitir solicitudes desde el frontend

# Construir la ruta absoluta al archivo Excel
# __file__ es la ruta al script actual (backend.py)
# os.path.dirname() obtiene el directorio de ese script
# os.path.join() une el directorio con el nombre del archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE_PATH = os.path.join(BASE_DIR, 'Calculador Solar - web 06-24_con ayuda - modificaciones 2025_5.xlsx')

# --- NUEVA RUTA: Para obtener la lista de electrodomésticos y sus consumos ---
@app.route('/api/electrodomesticos', methods=['GET'])
def get_electrodomesticos_consumos():
    try:
        print(f"DEBUG: Solicitud a /api/electrodomesticos. Leyendo de HOJA 'Tablas' desde: {EXCEL_FILE_PATH}")
        # ¡¡¡IMPORTANTE!!! Reemplaza 'Tablas' con el nombre exacto de tu hoja si es diferente.
        df_tablas = pd.read_excel(EXCEL_FILE_PATH, sheet_name='Tablas', engine='openpyxl', decimal=',')
        print("DEBUG: Hoja 'Tablas' leída para electrodomésticos.")

        col_nombre_idx = 0  # Columna A
        col_consumo_idx = 1 # Columna B
        fila_inicio_idx = 110 # Fila 111 en Excel (111 - 1)
        fila_fin_idx = 173  # Fila 174 en Excel (174 - 1)

        electrodomesticos_lista = []
        max_filas_df = df_tablas.shape[0]

        for r_idx in range(fila_inicio_idx, fila_fin_idx + 1):
            if r_idx >= max_filas_df:
                print(f"WARN: Fila {r_idx+1} fuera de límites (hoja 'Tablas' tiene {max_filas_df} filas). Lectura detenida.")
                break
            if col_nombre_idx >= df_tablas.shape[1] or col_consumo_idx >= df_tablas.shape[1]:
                print(f"WARN: Columna para nombre/consumo fuera de límites (hoja 'Tablas' tiene {df_tablas.shape[1]} columnas).")
                break

            nombre = df_tablas.iloc[r_idx, col_nombre_idx]
            consumo_kwh = df_tablas.iloc[r_idx, col_consumo_idx]

            if pd.isna(nombre) or str(nombre).strip() == "":
                print(f"DEBUG: Fila {r_idx+1} omitida por nombre NaN o vacío.")
                continue

            consumo_kwh_float = 0.0
            if pd.isna(consumo_kwh):
                print(f"DEBUG: Consumo NaN para '{nombre}' en fila {r_idx+1}, usando 0.")
            else:
                try:
                    consumo_kwh_float = float(consumo_kwh)
                except ValueError:
                    print(f"WARN: No se pudo convertir consumo '{consumo_kwh}' a float para '{nombre}'. Usando 0.")

            electrodomesticos_lista.append({
                "name": str(nombre),
                "consumo_diario_kwh": consumo_kwh_float
            })

        print(f"DEBUG: Total electrodomésticos leídos de 'Tablas' A{fila_inicio_idx+1}:B{fila_fin_idx+1}: {len(electrodomesticos_lista)}")
        categorias_respuesta = {"Electrodomésticos Disponibles": electrodomesticos_lista}

        return jsonify({"categorias": categorias_respuesta})

    except FileNotFoundError:
        print(f"ERROR en /api/electrodomesticos: Archivo Excel no encontrado: {EXCEL_FILE_PATH}")
        return jsonify({"error": "Archivo Excel no encontrado."}), 404
    except KeyError as e:
        print(f"ERROR en /api/electrodomesticos: Hoja 'Tablas' no encontrada?: {e}")
        return jsonify({"error": f"Error de clave (¿nombre de hoja?): {e}"}), 500
    except IndexError as e:
        print(f"ERROR en /api/electrodomesticos: Rango celdas fuera de límites: {e}")
        return jsonify({"error": f"Rango celdas fuera de límites: {e}"}), 500
    except Exception as e:
        import traceback
        print(f"ERROR GENERAL en /api/electrodomesticos: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

# --- Ruta para generar informe (EXISTENTE) ---
@app.route('/api/generar_informe', methods=['POST'])
def generar_informe():
    user_data = request.json
    print("DEBUG: Datos recibidos del frontend para informe:", user_data)

    if not user_data:
        return jsonify({"error": "No se recibieron datos"}), 400

    try:
        # --- LECTURA DEL INFORME DEL USUARIO BÁSICO ---
        # Lee el rango específico B5:D48 de la hoja 'Resultados'
        df_informe_basico = pd.read_excel(
            EXCEL_FILE_PATH,
            sheet_name='Resultados',
            engine='openpyxl',
            decimal=',',
            header=None,  # No hay fila de encabezado en el rango que leemos
            usecols="B:D",
            skiprows=4,  # Omitir las primeras 4 filas para empezar en B5
            nrows=44     # Leer 44 filas (de la 5 a la 48 inclusive)
        )

        # Renombrar columnas para facilidad de uso
        df_informe_basico.columns = ['descripcion', 'valor', 'unidad']

        # Convertir el DataFrame a una lista de diccionarios
        # y manejar los valores NaN (Not a Number) que pandas puede generar
        informe_basico_lista = []
        for index, row in df_informe_basico.iterrows():
            # Omitir filas donde la descripción esté vacía
            if pd.isna(row['descripcion']) or str(row['descripcion']).strip() == "":
                continue

            informe_basico_lista.append({
                'descripcion': str(row['descripcion']),
                # Reemplazar NaN con string vacío o 0, según prefieras
                'valor': str(row['valor']) if not pd.isna(row['valor']) else '',
                'unidad': str(row['unidad']) if not pd.isna(row['unidad']) else ''
            })

        print(f"DEBUG: {len(informe_basico_lista)} filas de informe básico leídas de Resultados B5:D48.")

        # --- PREPARACIÓN DE LA RESPUESTA FINAL ---
        # El objeto de respuesta ahora contendrá el informe básico y otros datos necesarios
        informe_final = {
            # Datos que ya tenías (puedes mantenerlos o eliminarlos si no son necesarios)
            "consumo_anual": user_data.get('totalAnnualConsumption', 0),
            "moneda": user_data.get('selectedCurrency', 'Pesos argentinos'),

            # El nuevo informe detallado del Excel
            "reporte_basico": informe_basico_lista
        }

        print(f"DEBUG: informe_final a punto de ser enviado: {informe_final}")
        return jsonify(informe_final)

    except FileNotFoundError:
        print(f"ERROR CRITICO: Archivo Excel NO ENCONTRADO: {EXCEL_FILE_PATH}")
        return jsonify({"error": "Archivo Excel no encontrado."}), 500
    except KeyError as e:
        print(f"Error de KeyError en backend (nombre de hoja?): {e}")
        return jsonify({"error": f"Error al leer hoja Excel: {e}. Asegúrese de que las hojas 'Resultados' y 'Area de trabajo' existan y las columnas sean correctas."}), 500
    except Exception as e:
        import traceback
        print(f"ERROR GENERAL en backend (generar_informe): {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Error interno del servidor al generar informe: {str(e)}"}), 500

# Opcional: Rutas para servir los archivos estáticos de tu frontend
@app.route('/')
def serve_calculador_html():
    return send_from_directory('.', 'calculador.html')

@app.route('/<path:path>')
def serve_static_files(path):
    # Asegúrate de que los archivos estén en la misma carpeta que 'backend.py'
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True)