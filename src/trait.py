import pandas as pd
from dateutil.relativedelta import relativedelta

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

def calcular_duracion(row):
    try:
        # Verificar si hay valores NaT o None
        INICIO = pd.to_datetime(row['INICIO DE PERIODO'], errors='coerce') - pd.to_timedelta(1, unit='D')
        FIN = pd.to_datetime(row['FIN DE PERIODO'], errors='coerce')

        delta = relativedelta(FIN, INICIO)
        return pd.Series({
            'AÑOS': delta.years,
            'MESES': delta.months,
            'DIAS': delta.days
        })
    except Exception as e:
        print(f"Error procesando duracion: {e}, FIN={row['FIN DE PERIODO']}, INICIO={row['INICIO DE PERIODO']}")
        return pd.Series({
            'AÑOS': None,
            'MESES': None,
            'DIAS': None
        })

def agregar_promociones(df_1, df_2):
    df_FILTRADO = df_1.copy()
    df_PRO = df_2

    nuevos_promocion = []

    # Por cada registro con TIPO = PRO, identificar registros con el mismo CODIGO del df_FILTRADO
    for _, registro in df_PRO.iterrows():
        codigo_filtrado = df_FILTRADO.loc[df_FILTRADO['CODIGO'] == registro['CODIGO']].reset_index().rename(columns={'index': 'NUM_REGISTRO'})

        registros_con_fecha = codigo_filtrado[
            (codigo_filtrado['INICIO DE PERIODO'] <= registro['INICIO DE PERIODO']) &
            (codigo_filtrado['FIN DE PERIODO'] >= registro['INICIO DE PERIODO'])
        ]
        if not registros_con_fecha.empty:
            for _, matched in registros_con_fecha.iterrows():
                num_reg = matched['NUM_REGISTRO']
                if num_reg in df_FILTRADO.index:
                    df_FILTRADO.loc[num_reg, 'TIPO2'] = registro['TIPO']
                    df_FILTRADO.loc[num_reg, 'FIN DE PERIODO'] = pd.to_datetime(registro['INICIO DE PERIODO'], errors='coerce') - pd.to_timedelta(1, unit='D')
                    nuevos_promocion.append(registro.to_dict())

    if nuevos_promocion:
        df_PROMO = pd.DataFrame(nuevos_promocion)
        df_FILTRADO = pd.concat([df_FILTRADO, df_PROMO], ignore_index=True, sort=False)
    else:
        print("No se encontraron coincidencias PRO en df_FILTRADO.")
        return False

    return df_FILTRADO

def cambio_fin_de_periodo(df_1, df_2):

    # Eliminar registros con TIPO = REN, CES, REA, NRA, LIC, CDE
    # df_FILTRADO = df[~df['TIPO'].isin(['REN', 'CES', 'REA', 'NRA', 'LIC', 'CDE'])].copy()

    # Filtra registros con TIPO = REN , CES, NRA 
    # df_REN_CES = df[df['TIPO'].isin(['REN', 'CES', 'NRA'])].copy()

    df_FILTRADO = df_1
    df_REN_CES = df_2

    # Por cada registro con TIPO = REN, CES o NRA, identificar registros con el mismo CODIGO del df_FILTRADO, preservando el número de registro original
    matched_rows = []
    for _, registro in df_REN_CES.iterrows():
        # Identificar registros con el mismo CODIGO del df_FILTRADO, preservando el número de registro original
        codigo_filtrado = df_FILTRADO.loc[df_FILTRADO['CODIGO'] == registro['CODIGO']].reset_index().rename(columns={'index': 'NUM_REGISTRO'})
        # Identificar el registro con el mismo CODIGO cuya fecha de fin del registro REN o CES
        # esté entre la fecha de inicio y la fecha de fin de algún registro en codigo_filtrado
        registros_con_fecha = codigo_filtrado[
            (codigo_filtrado['INICIO DE PERIODO'] <= registro['FIN DE PERIODO']) &
            (codigo_filtrado['FIN DE PERIODO'] >= registro['FIN DE PERIODO'])
        ]
        if not registros_con_fecha.empty:
            registros_con_fecha = registros_con_fecha.copy()
            registros_con_fecha['TIPO_REN_CES'] = registro['TIPO']
            registros_con_fecha['FIN_REN_CES'] = registro['FIN DE PERIODO']
            registros_con_fecha['INICIO_REN_CES'] = registro['INICIO DE PERIODO']
            matched_rows.append(registros_con_fecha)

    if matched_rows:
        df_matched = pd.concat(matched_rows, ignore_index=True)
        # print("Registros REN/CES con coincidencias en df_FILTRADO:")
        # print(df_matched[['NUM_REGISTRO', 'CODIGO', 'TIPO_REN_CES', 'FIN_REN_CES', 'INICIO', 'FIN']])
        
        # Verificar que la FECHA_INICIO del registro REN/CES sea igual a la FECHA_INICIO del registro coincidente en df_FILTRADO
        for _, row in df_matched.iterrows():
            if row['INICIO DE PERIODO'] != row['INICIO_REN_CES']:
                print(f"Advertencia: La fecha de inicio del registro REN/CES (CODIGO={row['CODIGO']}) no coincide con la fecha de inicio del registro en df_FILTRADO.")
                return

        # Reemplazar en df_FILTRADO el valor de TIPO, FIN_DE_PERIODO por el valor de TIPO_REN_CES y FIN_REN_CES para los registros que coincidan
        for _, row in df_matched.iterrows():
            num_reg = row['NUM_REGISTRO']
            if num_reg in df_FILTRADO.index:
                df_FILTRADO.loc[num_reg, 'TIPO2'] = row['TIPO_REN_CES']
                df_FILTRADO.loc[num_reg, 'FIN DE PERIODO'] = row['FIN_REN_CES']
        # print("Se actualizaron los registros en df_FILTRADO.")
    else:
        print(f"No se encontraron coincidencias REN/CES en df_FILTRADO. CODIGO={row['CODIGO']}")
        return False
    
    return df_FILTRADO

def acumulacion(df):
    resultado = df.groupby('CODIGO')[['AÑOS', 'MESES', 'DIAS']].sum().reset_index()

    # Normaliza los días a meses cuando haya 30 o más días
    resultado['MESES'] = resultado['MESES'] + (resultado['DIAS'] // 30)
    resultado['DIAS'] = resultado['DIAS'] % 30

    # Normaliza los meses a años cuando haya 12 o más meses
    resultado['AÑOS'] = resultado['AÑOS'] + (resultado['MESES'] // 12)
    resultado['MESES'] = resultado['MESES'] % 12

    return resultado

def verifica_integridad_campos(df):
    # campos_requeridos = [
    #     'TIPO',
    #     'CODIGO',
    #     'APELLIDOS Y NOMBRES',
    #     'FACULTAD',
    #     'ASIGNATURA',
    #     'CATEGORIA',
    #     'DEDICACION',
    #     'RESOLUCION',
    #     'FECHA DE RESOLUCION',
    #     'INICIO DE PERIODO',
    #     'FIN DE PERIODO',
    # ]
    campos_requeridos = campos()

    columnas = set(df.columns)
    resultado = pd.DataFrame({
        'CAMPO': campos_requeridos,
        'STATUS': [campo in columnas for campo in campos_requeridos]
    })

    for _, registro in resultado.iterrows():
        if registro.STATUS == False:
            return False
    return True

def verifica_tipo(df):
    valores_array = df['TIPO'].unique()
    for valor in valores_array:
        TIPOS_PERMITIDOS = [
            'ING',  # INGRESO
            'RAT',  # RATIFICACION
            'REA',  # REASIGNACION
            'PRO',  # PROMOCION
            'CES',  # CESE
            'REN',  # RENUNCIA
            'NRA',  # NO RATIFICADO
            'CDE',  # CAMBIO DE DEDICACION
            'LIC'   # LICENCIA
        ]
        if valor not in TIPOS_PERMITIDOS:
            return False
    return True

def verifica_integridad_datos(df):
    campos_obligatorios = [
        'TIPO',
        'CODIGO',
        'INICIO DE PERIODO',
        'FIN DE PERIODO',
    ]

    for campo in campos_obligatorios:
        if campo not in df.columns:
            print(f"Falta la columna {campo}.")
            return False

        valores = df[campo]
        vacios = valores.isna() | valores.astype(str).str.strip().eq('') | valores.eq(0)
        if vacios.any():
            print(f"Hay registros sin {campo}.")
            return False

    return True

def registro_por_docente(df):
    # Valores unicos de CODIGO
    # Valor menor de INICIO DE PERIODO
    # Valor mayor de FIN DE PERIODO
    # Suma de AÑOS, MESES, DIAS
    resultado = df.groupby('CODIGO').agg({
        'APELLIDOS Y NOMBRES': 'first', 
        'FACULTAD': 'last', 
        'ASIGNATURA': 'last', 
        'CATEGORIA': 'last', 
        'DEDICACION': 'last', 
        'INICIO DE PERIODO': 'min',
        'FIN DE PERIODO': 'max',
        'AÑOS': 'sum',
        'MESES': 'sum',
        'DIAS': 'sum',
        'TIPO2': 'first'
    }).reset_index()

    # Eliminar TIPO2 si no tiene valores
    if 'TIPO2' in resultado.columns:
        resultado = resultado.where(pd.notna(resultado), None)
    
    # Normaliza los días a meses cuando haya 30 o más días
    resultado['MESES'] = resultado['MESES'] + (resultado['DIAS'] // 30)
    resultado['DIAS'] = resultado['DIAS'] % 30

    # Normaliza los meses a años cuando haya 12 o más meses
    resultado['AÑOS'] = resultado['AÑOS'] + (resultado['MESES'] // 12)
    resultado['MESES'] = resultado['MESES'] % 12

    return resultado

