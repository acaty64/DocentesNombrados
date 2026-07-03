import os
import sys
import pandas as pd
# import procesos
# import proceso_2
import src.trait as trait

def main(ruta, archivo, hoja):
    input_path = os.path.join(ruta, archivo)
    output_dir = os.path.join(ruta, 'output')
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_excel(input_path, sheet_name=hoja, dtype={'CODIGO': str}, usecols=trait.campos())

    if trait.verifica_integridad_campos(df) == False:
        print("Error, revisar las columnas.")
        return "Error, revisar las columnas."
    
    if trait.verifica_integridad_datos(df) == False:
        return "Error, revisar los datos, hay fechas en blanco."

    if trait.verifica_tipo(df) == False:
        print("Error, revisar la columna TIPO, hay información errada.")
        return False

    df = trait.agrega_fechas_calculo(df)

    # Filtra registros con TIPO = PRO y CDE, ordenado por CODIGO y por INICIO DE PERIODO
    df_PRO = df[df['TIPO'].isin(['PRO', 'CDE'])].copy()
    df_PRO = df_PRO.sort_values(by=['CODIGO', 'INICIO DE PERIODO'])
    # print("Registros con TIPO = PRO y CDE:")
    # print(df_PRO)

    # Eliminar registros con TIPO = REN, CES, REA, NRA, LIC, CDE, PRO
    df_FILTRADO = df[~df['TIPO'].isin(['REN', 'CES', 'REA', 'NRA', 'LIC', 'CDE', 'PRO'])].copy()

    df_1 = trait.agregar_pro_cde(df_FILTRADO, df_PRO)
    if df_1.empty:
        return "Error, revisar registros TIPO: PRO."

    df_FILTRADO = df_1

    # Eliminar registros con TIPO = REN, CES, REA, NRA, LIC, CDE
    # df_FILTRADO = df[~df['TIPO'].isin(['REN', 'CES', 'REA', 'NRA', 'LIC', 'CDE', 'PRO'])].copy()

    # Filtra registros con TIPO = REN , CES, NRA 
    df_REN_CES = df[df['TIPO'].isin(['REN', 'CES', 'NRA'])].copy()

    df_1 = trait.cambio_fin_de_calculo(df_FILTRADO, df_REN_CES)
    if df_1.empty:
        return "Error, revisar registros TIPO: REN, CES, NRA."

    # Calcula duración de cada registro
    df_1[['AÑOS', 'MESES', 'DIAS']] = df_1.apply(trait.calcular_duracion, axis=1)

    output_path = os.path.join(output_dir, 'reporte.xlsx')
    df_1.to_excel(output_path, sheet_name='salida', index=False)

    df_2 = trait.registro_por_docente(df_1)

    df = trait.agrega_status(df_2)

    # Grabar nueva hoja en el mismo archivo Excel con los datos procesados
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='por docente', index=False)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Uso: python main.py <ruta> <archivo> <hoja de datos>')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
