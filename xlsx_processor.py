import os
import tempfile
import requests
import shutil
import pandas as pd


def convert_xls_to_xlsx(xls_content):
    """
    Convierte contenido XLS a formato XLSX preservando toda la información.

    Args:
        xls_content (bytes): Contenido del archivo XLS en bytes

    Returns:
        bytes: Contenido del archivo convertido a XLSX
    """
    import io

    # Leer el XLS desde bytes
    xls_buffer = io.BytesIO(xls_content)

    # Leer todas las hojas del archivo XLS
    xls_file = pd.ExcelFile(xls_buffer, engine="xlrd")

    # Crear buffer para el XLSX de salida
    xlsx_buffer = io.BytesIO()

    # Escribir todas las hojas al nuevo archivo XLSX
    with pd.ExcelWriter(xlsx_buffer, engine="openpyxl", mode="w") as writer:
        for sheet_name in xls_file.sheet_names:
            # Leer cada hoja preservando tipos de datos
            df = pd.read_excel(xls_file, sheet_name=sheet_name, header=None)

            # Escribir al nuevo archivo
            df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

    # Obtener el contenido del XLSX
    xlsx_buffer.seek(0)
    return xlsx_buffer.read()


def xlsx_url_to_temp_file(xlsx_url):
    """
    Descarga un archivo Excel (XLSX o XLS) desde una URL y lo guarda como XLSX en un archivo temporal.
    Si el archivo es XLS, lo convierte a XLSX antes de guardarlo.

    Args:
        xlsx_url (str): URL del archivo Excel (.xlsx o .xls)

    Returns:
        tuple: (ruta_archivo_temporal, directorio_temporal)
    """
    # Descargar el archivo
    response = requests.get(xlsx_url)
    response.raise_for_status()

    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp(prefix="xlsx_temp_")

    # Extraer nombre base del archivo
    filename = xlsx_url.split("/")[-1] if "/" in xlsx_url else "temp_file"

    # Determinar si necesita conversión
    is_xls = False
    if filename.lower().endswith(".xls") and not filename.lower().endswith(".xlsx"):
        is_xls = True
    else:
        # Intentar detectar por content-type si no es claro por la extensión
        content_type = response.headers.get("content-type", "").lower()
        if "application/vnd.ms-excel" in content_type:
            is_xls = True

    # Procesar el contenido
    if is_xls:
        # Convertir XLS a XLSX
        content = convert_xls_to_xlsx(response.content)
        # Asegurar que el nombre termine en .xlsx
        if filename.lower().endswith(".xls"):
            filename = filename[:-4] + ".xlsx"
        else:
            filename = filename + ".xlsx"
    else:
        # Ya es XLSX, usar directamente
        content = response.content
        # Asegurar extensión .xlsx
        if not filename.lower().endswith(".xlsx"):
            filename = filename + ".xlsx"

    # Crear ruta completa
    temp_file_path = os.path.join(temp_dir, filename)

    # Guardar el archivo
    with open(temp_file_path, "wb") as f:
        f.write(content)

    return temp_file_path, temp_dir


def cleanup_temp_files(temp_dir):
    """
    Elimina un directorio temporal y todo su contenido.

    Args:
        temp_dir (str): Ruta del directorio temporal a eliminar

    Returns:
        bool: True si se eliminó correctamente, False si hubo error
    """
    try:
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"Error al eliminar directorio temporal: {e}")
        return False


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplos de URLs - ambos se guardarán como XLSX
    url_xlsx = "https://www.cmu.edu/blackboard/files/evaluate/tests-example.xls"

    try:
        # Descargar y obtener rutas
        temp_file, temp_dir = xlsx_url_to_temp_file(url_xlsx)
        print(f"✅ Archivo temporal creado: {temp_file}")
        print(f"📁 Directorio temporal: {temp_dir}")

        # El archivo siempre será XLSX, incluso si la fuente era XLS
        print(f"📄 Formato final: XLSX")

        # Aquí puedes hacer lo que necesites con el archivo
        # Por ejemplo: procesarlo, leerlo, enviarlo a otro servicio, etc.

        # Limpiar archivos temporales cuando termines
        if cleanup_temp_files(temp_dir):
            print("🧹 Archivos temporales eliminados")

    except Exception as e:
        print(f"❌ Error: {e}")
