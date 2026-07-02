import os
import pandas as pd
import trait

def campos():
    return ['TIPO', 
              'CODIGO', 
              'APELLIDOS Y NOMBRES', 
              'FACULTAD', 
              'ASIGNATURA', 
              'CATEGORIA', 
              'DEDICACION', 
              'RESOLUCION', 
              'FECHA DE RESOLUCION', 
              'INICIO DE PERIODO', 
              'FIN DE PERIODO']

def procesar_datos(ruta, archivo, hoja):
    input_path = os.path.join(ruta, archivo)
    output_dir = os.path.join(ruta, 'output')
    os.makedirs(output_dir, exist_ok=True)

    archivo_excel = 'reporte.xlsx'
    output_path = os.path.join(output_dir, 'reporte.xlsx')

    columnas = campos()

    df = pd.read_excel(input_path, sheet_name=hoja, dtype={'CODIGO': str}, usecols=columnas)


    # VERIFICA CALIDAD DE CAMPOS (CAMPOS PERMITIDOS)
    if not trait.verifica_integridad_campos(df):
        print("Error: Faltan campos requeridos.")
        return False
    
    # VERIFICA CALIDAD DE DATOS
    if not trait.verifica_integridad_datos(df):
        print("Error: Faltan valores en campos [TIPO, CODIGO, INICIO DE PERIODO o FIN DE PERIODO]")
        return

    # CONSISTENCIA TIPO
    if not trait.verifica_tipo(df):
        print("Error: Hay valores no permitidos en la columna 'TIPO'")
        return







    ###############################################################
    ########## T O D O 
    ###############################################################

    # CALCULA DURACION
    # Convertir a datetime con manejo de errores
    df['INICIO'] = pd.to_datetime(df['INICIO DE PERIODO'], errors='coerce') - pd.to_timedelta(1, unit='d')
    df['FIN'] = pd.to_datetime(df['FIN DE PERIODO'], errors='coerce')
    
    # Verificar y reportar fechas inválidas
    invalid_inicio = df['INICIO'].isna().sum()
    invalid_fin = df['FIN'].isna().sum()
    if invalid_inicio > 0 or invalid_fin > 0:
        print(f"Advertencia: {invalid_inicio} fechas de INICIO inválidas, {invalid_fin} fechas de FIN inválidas")
        print("Revisa los registros.")
        # Imprime los registros con invalid_inicio o invalid_fin para revisión
        if invalid_inicio > 0:
            print("Registros con fechas de INICIO inválidas:")
            print(df[df['INICIO'].isna()])
        if invalid_fin > 0:
            print("Registros con fechas de FIN inválidas:")
            print(df[df['FIN'].isna()])
        # cancelar proceso si hay fechas inválidas
        return
    


    df[['AÑOS', 'MESES', 'DIAS']] = df.apply(calcular_duracion, axis=1)

    df.to_excel(os.path.join(output_dir, archivo_excel), sheet_name='df', index=False)

    df_FILTRADO =subprocesos.renuncias_ceses(output_path, df)
    print("Proceso de renuncias y ceses completado.")

    df_FILTRADO =subprocesos.promociones(output_path, df_FILTRADO)
    print("Proceso de promociones completado.")

    df_FILTRADO =subprocesos.licencias(output_path, df, df_FILTRADO)
    print("Proceso de licencias completado.")

    # Reordenar filas para la salida final
    df_FILTRADO.sort_values(by=['CODIGO', 'INICIO'], inplace=True)

    # Eliminar columnas INICIO y FIN
    df_FILTRADO.drop(columns=['INICIO', 'FIN'], inplace=True)

    # print(df_FILTRADO.head())

    # output_path = os.path.join(output_dir, 'reporte.xlsx')
    # df_FILTRADO.to_excel(output_path, sheet_name='salida', index=False)
    # Grabar nueva hoja en el mismo archivo Excel con los datos procesados
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
        df_FILTRADO.to_excel(writer, sheet_name='df_FILTRADO', index=False)

    return df_FILTRADO