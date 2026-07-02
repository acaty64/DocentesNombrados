import os
import sys
import pandas as pd
from dateutil.relativedelta import relativedelta
import procesos

def test_duracion():
    # Crear un DataFrame de prueba
    data = {
        'CODIGO': [1, 2, 3, 4],
        'INICIO': [pd.Timestamp('2020-01-01'), 
                   pd.Timestamp('2021-06-15'), 
                   pd.Timestamp('2022-03-10'),
                   pd.Timestamp('2023-04-11')],
        'FIN': [pd.Timestamp('2021-01-01'), 
                pd.Timestamp('2022-07-15'), 
                pd.Timestamp('2023-04-11'), 
                pd.Timestamp('2024-02-05')]
    }
    df = pd.DataFrame(data)

    # Aplicar la función calcular_duracion a cada fila del DataFrame
    duracion_df = df.apply(procesos.calcular_duracion, axis=1)

    assert duracion_df.iloc[0]['AÑOS'] == 1
    assert duracion_df.iloc[0]['MESES'] == 0
    assert duracion_df.iloc[0]['DIAS'] == 0
    assert duracion_df.iloc[1]['AÑOS'] == 1
    assert duracion_df.iloc[1]['MESES'] == 1
    assert duracion_df.iloc[1]['DIAS'] == 0
    assert duracion_df.iloc[2]['AÑOS'] == 1
    assert duracion_df.iloc[2]['MESES'] == 1
    assert duracion_df.iloc[2]['DIAS'] == 1
    assert duracion_df.iloc[3]['AÑOS'] == 0
    assert duracion_df.iloc[3]['MESES'] == 9
    assert duracion_df.iloc[3]['DIAS'] == 25
    
def test_cambio_fin_de_periodo():
    # Crear un DataFrame de prueba
    data_1 = [
        {
            'TIPO': 'ING',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2023-12-31 00:00:00'),
            'INICIO': pd.Timestamp('2020-01-01'),
            'FIN': pd.Timestamp('2022-12-31')
        },
        {
            'TIPO': 'RAT',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2024-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2026-12-31 00:00:00'),
            'INICIO': pd.Timestamp('2024-01-01'),
            'FIN': pd.Timestamp('2026-12-31')
        }
    ]
    data_2 = [
        {
            'TIPO': 'REN',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2024-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2024-06-30 00:00:00'),
            'INICIO': pd.Timestamp('2024-01-01'),
            'FIN': pd.Timestamp('2024-06-30')
        }
    ]
    df_1 = pd.DataFrame(data_1)
    df_2 = pd.DataFrame(data_2)

    df_1 = procesos.cambio_fin_de_periodo(df_1, df_2)


def test_total(ruta, archivo, hoja):
    print("test.py", ruta, archivo, hoja)

    output_dir = os.path.join(ruta, 'output')
    os.makedirs(output_dir, exist_ok=True)

    df = procesos.procesar_datos(ruta, archivo, hoja)

    if df is not None:
        print("Duración calculada correctamente:")
        if {'CODIGO', 'INICIO', 'FIN', 'AÑOS', 'MESES', 'DIAS'}.issubset(df.columns):
            print(df[['CODIGO', 'INICIO', 'FIN', 'AÑOS', 'MESES', 'DIAS']])
        else:
            print(df.head())
        df.to_excel(os.path.join(output_dir, 'reporte_test.xlsx'), index=False)
        print ("Archivo de prueba guardado en:", os.path.join(output_dir, 'reporte_test.xlsx'))
        # Imprime la fecha y hora del archivo de prueba guardado
        print("Archivo de prueba guardado el:", pd.Timestamp.now())

    else:
        print("No se pudo calcular la duración.")
        return None

    #assert df is not None, "Desde test_2.py: La función test_total no devolvió un valor válido."
    return len(df)