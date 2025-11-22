import pandas as pd
import sys

def check_excel_file(filepath):
    try:
        # Leer todas las hojas del archivo Excel
        excel_file = pd.ExcelFile(filepath)
        print(f"\nArchivo: {filepath}")
        print("Hojas disponibles:", excel_file.sheet_names)
        
        # Revisar cada hoja
        for sheet_name in excel_file.sheet_names:
            print(f"\nHoja: {sheet_name}")
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            
            # Mostrar las primeras filas y columnas
            print("Primeras filas:")
            print(df.head())
            
            # Buscar columnas que podrían contener el código de piña
            code_columns = [col for col in df.columns if any(term in str(col).lower() for term in ['codigo', 'sample', 'id'])]
            if code_columns:
                print("\nColumnas que podrían contener códigos:", code_columns)
                for col in code_columns:
                    print(f"Valores únicos en '{col}':", df[col].unique())
    
    except Exception as e:
        print(f"Error al leer el archivo {filepath}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_to_check = sys.argv[1]
        check_excel_file(file_to_check)
    else:
        print("Por favor, proporcione la ruta al archivo Excel como argumento.")
        print("Ejemplo: python check_excel.py ruta/al/archivo.xlsx")
