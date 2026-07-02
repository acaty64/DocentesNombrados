import pandas as pd
import sys

# from procesos import calcular_duracion

def status(archivo_excel, df):
    if df.empty:
        print("El DataFrame está vacío. No se pueden procesar los datos.")
        return False
    else:
        print(f"El DataFrame contiene {len(df)} registros. Listo para procesar.")
        # Encontrar todos los registros que tengan INICIO DE PERIODO menor a hoy y FIN DE PERIODO mayor o igual a hoy
        hoy = pd.to_datetime('today').normalize()
        df['INICIO DE PERIODO'] = pd.to_datetime(df['INICIO DE PERIODO'], errors='coerce')
        df['FIN DE PERIODO'] = pd.to_datetime(df['FIN DE PERIODO'], errors='coerce')
        df_filtrado = df[(df['INICIO DE PERIODO'] < hoy) & (df['FIN DE PERIODO'] >= hoy)]   
        print(f"Registros con INICIO DE PERIODO menor a hoy y FIN DE PERIODO mayor o igual a hoy: {len(df_filtrado)}")  

        # Agregar en df nueva columna STATUS con el valor ACTIVO para los registros con el mismo CODIGO que cumplan la condición anterior y INACTIVO para los demás
        for each in df.index:
            codigo = df.loc[each, 'CODIGO']
            if codigo in df_filtrado['CODIGO'].values:
                df.loc[each, 'STATUS'] = 'ACTIVO'
            else:
                df.loc[each, 'STATUS'] = 'INACTIVO'
        df.to_excel(archivo_excel, sheet_name='STATUS', index=False)

        # Grabar nueva hoja en el mismo archivo Excel con los datos procesados
        return True



def renuncias_ceses(archivo_excel, df):

    # Eliminar registros con TIPO = REN, CES, REA, NRA, LIC, CDE
    df_FILTRADO = df[~df['TIPO'].isin(['REN', 'CES', 'REA', 'NRA', 'LIC', 'CDE'])].copy()

    # Filtra registros con TIPO = REN , CES, NRA 
    df_REN_CES = df[df['TIPO'].isin(['REN', 'CES', 'NRA'])].copy()

    # Por cada registro con TIPO = REN, CES o NRA, identificar registros con el mismo CODIGO del df_FILTRADO, preservando el número de registro original
    matched_rows = []
    for _, registro in df_REN_CES.iterrows():
        # Identificar registros con el mismo CODIGO del df_FILTRADO, preservando el número de registro original
        codigo_filtrado = df_FILTRADO.loc[df_FILTRADO['CODIGO'] == registro['CODIGO']].reset_index().rename(columns={'index': 'NUM_REGISTRO'})
        # Identificar el registro con el mismo CODIGO cuya fecha de fin del registro REN o CES
        # esté entre la fecha de inicio y la fecha de fin de algún registro en codigo_filtrado
        registros_con_fecha = codigo_filtrado[
            (codigo_filtrado['INICIO'] <= registro['FIN']) &
            (codigo_filtrado['FIN'] >= registro['FIN'])
        ]
        if not registros_con_fecha.empty:
            registros_con_fecha = registros_con_fecha.copy()
            registros_con_fecha['TIPO_REN_CES'] = registro['TIPO']
            registros_con_fecha['FIN_REN_CES'] = registro['FIN']
            registros_con_fecha['INICIO_REN_CES'] = registro['INICIO']
            registros_con_fecha['AÑOS'] = registro['AÑOS']
            registros_con_fecha['MESES'] = registro['MESES']
            registros_con_fecha['DIAS'] = registro['DIAS']
            matched_rows.append(registros_con_fecha)

    if matched_rows:
        df_matched = pd.concat(matched_rows, ignore_index=True)
        # print("Registros REN/CES con coincidencias en df_FILTRADO:")
        # print(df_matched[['NUM_REGISTRO', 'CODIGO', 'TIPO_REN_CES', 'FIN_REN_CES', 'INICIO', 'FIN']])
        
        # Verificar que la FECHA_INICIO del registro REN/CES sea igual a la FECHA_INICIO del registro coincidente en df_FILTRADO
        for _, row in df_matched.iterrows():
            if row['INICIO'] != row['INICIO_REN_CES']:
                print(f"Advertencia: La fecha de inicio del registro REN/CES (CODIGO={row['CODIGO']}) no coincide con la fecha de inicio del registro en df_FILTRADO.")
                return

        # Reemplazar en df_FILTRADO el valor de TIPO, FIN_DE_PERIODO, AÑOS, MESES y DIAS por el valor de TIPO_REN_CES y FIN_REN_CES para los registros que coincidan
        for _, row in df_matched.iterrows():
            num_reg = row['NUM_REGISTRO']
            if num_reg in df_FILTRADO.index:
                df_FILTRADO.loc[num_reg, 'TIPO'] = row['TIPO_REN_CES']
                df_FILTRADO.loc[num_reg, 'FIN DE PERIODO'] = row['FIN_REN_CES']
                df_FILTRADO.loc[num_reg, 'AÑOS'] = row['AÑOS']
                df_FILTRADO.loc[num_reg, 'MESES'] = row['MESES']
                df_FILTRADO.loc[num_reg, 'DIAS'] = row['DIAS']
        print("Se actualizaron los registros en df_FILTRADO.")

    else:
        print("No se encontraron coincidencias REN/CES en df_FILTRADO.")

    # Grabar nueva hoja en el mismo archivo Excel con los datos procesados
    with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='a') as writer:
        df_FILTRADO.to_excel(writer, sheet_name='REN_CES', index=False)

    return df_FILTRADO


def promociones(archivo_excel, df_FILTRADO):
    # Selecciona registros excepto TIPO = PRO
    df_no_PRO = df_FILTRADO[df_FILTRADO['TIPO'] != 'PRO'].copy()  

    # Selecciona registros con TIPO = PRO
    df_PRO = df_FILTRADO[df_FILTRADO['TIPO'] == 'PRO'].copy()

    print(f"Cantidad de registros con TIPO PRO: {len(df_PRO)}")

    with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='a') as writer:
        df_no_PRO.to_excel(writer, sheet_name='PRO', index=False)
    return df_no_PRO

    # Busca registros en df_no_PRO con el mismo CODIGO y fecha de inicio mayor o igual a la fecha de inicio del registro PRO y fecha de fin menor o igual a la fecha de inicio del registro PRO
    for _, registro in df_PRO.iterrows():
        codigo_filtrado = df_FILTRADO.loc[df_FILTRADO['CODIGO'] == registro['CODIGO']].reset_index().rename(columns={'index': 'NUM_REGISTRO'})
        registros_con_fecha = codigo_filtrado[
            (codigo_filtrado['INICIO'] >= registro['INICIO']) &
            (codigo_filtrado['FIN'] < registro['INICIO'])
        ]
        if not registros_con_fecha.empty:
            # Reemplaza en df_no_PRO el valor de FIN DE PERIODO por el valor de FIN DE PERIODO del registro PRO para los registros que coincidan
            for _, row in registros_con_fecha.iterrows():
                num_reg = row['NUM_REGISTRO']
                if num_reg in df_no_PRO.index:
                    df_no_PRO.loc[num_reg, 'FIN DE PERIODO'] = registro['FIN DE PERIODO']
                    print(f"Se actualizó el FIN DE PERIODO del registro con CODIGO={registro['CODIGO']} en df_no_PRO.")
        else:
            # Agrega registro en df_no_PRO con la informacion del registro de df_PRO
            nuevo_registro = registro.copy()
            df_no_PRO = pd.concat([df_no_PRO, pd.DataFrame([nuevo_registro])], ignore_index=True)
            print(f"No se encontraron coincidencias PRO para CODIGO={registro['CODIGO']} en df_no_PRO. Se agregó el registro PRO a df_no_PRO.")

    # Grabar nueva hoja en el mismo archivo Excel con los datos procesados
    with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='a') as writer:
        df_no_PRO.to_excel(writer, sheet_name='PRO', index=False)
    return df_no_PRO


def licencias(archivo_excel, df, df_FILTRADO):
    ############ Agrega registros LIC con AÑOS, MESES y DIAS calculados negativos ############
    df_LIC = df[df['TIPO'] == 'LIC'].copy()
    if not df_LIC.empty:
        df_LIC[['AÑOS', 'MESES', 'DIAS']] = -df_LIC[['AÑOS', 'MESES', 'DIAS']]
        df_FILTRADO = pd.concat([df_FILTRADO, df_LIC], ignore_index=True)

    print("Se agregaron los registros LIC a df_FILTRADO.")
    # df_check = df_FILTRADO[df_FILTRADO['TIPO'] == 'LIC']
    # print(df_check.head(5))
    
    # Grabar nueva hoja en el mismo archivo Excel con los datos procesados
    with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='a') as writer:
        df_FILTRADO.to_excel(writer, sheet_name='LIC', index=False)

    return df_FILTRADO