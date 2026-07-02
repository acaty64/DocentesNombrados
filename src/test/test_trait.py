import os
import sys
import pandas as pd
from dateutil.relativedelta import relativedelta
import src.trait as trait
import pytest

def test_agrega_fechas_calculo():
    # Crear un DataFrame de prueba
    data = {
        'CODIGO': [1, 2, 3],
        'INICIO DE PERIODO': [
            pd.Timestamp('2020-01-01'), 
            pd.Timestamp('2021-06-15'), 
            pd.Timestamp('2022-03-10')
        ],
        'FIN DE PERIODO': [
            pd.Timestamp('2020-12-31'), 
            pd.Timestamp('2022-07-14'), 
            pd.Timestamp('2023-04-11')
        ]
    }
    df = pd.DataFrame(data)
    df = trait.agrega_fechas_calculo(df)

    assert df.iloc[0]['INICIO DE CALCULO'] == pd.Timestamp('2020-01-01')
    assert df.iloc[0]['FIN DE CALCULO'] == pd.Timestamp('2020-12-31')
    assert df.iloc[1]['INICIO DE CALCULO'] == pd.Timestamp('2021-06-15')
    assert df.iloc[1]['FIN DE CALCULO'] == pd.Timestamp('2022-07-14')
    assert df.iloc[2]['INICIO DE CALCULO'] == pd.Timestamp('2022-03-10')
    assert df.iloc[2]['FIN DE CALCULO'] == pd.Timestamp('2023-04-11')   

def test_calcular_duracion():
    # Crear un DataFrame de prueba
    data = {
        'CODIGO': [1, 2, 3, 4],
        'INICIO DE CALCULO': [   
            pd.Timestamp('2020-01-01'), 
            pd.Timestamp('2021-06-15'), 
            pd.Timestamp('2022-03-10'),
            pd.Timestamp('2023-04-11')
        ],
        'FIN DE CALCULO': [
            pd.Timestamp('2020-12-31'), 
            pd.Timestamp('2022-07-14'), 
            pd.Timestamp('2023-04-11'), 
            pd.Timestamp('2024-02-05')
        ]
    }
    df = pd.DataFrame(data)
    df[['AÑOS', 'MESES', 'DIAS']] = df.apply(trait.calcular_duracion, axis=1)

    assert df.iloc[0]['AÑOS'] == 1
    assert df.iloc[0]['MESES'] == 0
    assert df.iloc[0]['DIAS'] == 0
    assert df.iloc[1]['AÑOS'] == 1
    assert df.iloc[1]['MESES'] == 1
    assert df.iloc[1]['DIAS'] == 0
    assert df.iloc[2]['AÑOS'] == 1
    assert df.iloc[2]['MESES'] == 1
    assert df.iloc[2]['DIAS'] == 2
    assert df.iloc[3]['AÑOS'] == 0
    assert df.iloc[3]['MESES'] == 9
    assert df.iloc[3]['DIAS'] == 26

def test_agregar_promociones():
    # Crear un DataFrame de prueba con datos de tipo ING y RAT
    data_1 = [
        {
            'TIPO': 'ING',
            'CODIGO': 1,
            'RESOLUCION': 'Resolucion de Concurso de Catedra',
            'CATEGORIA': 'Auxiliar',
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2023-12-31 00:00:00'),
        },
        {
            'TIPO': 'RAT',
            'CODIGO': 1,
            'RESOLUCION': 'Resolucion de Ratificacion',
            'CATEGORIA': 'Auxiliar',
            'INICIO DE PERIODO': pd.Timestamp('2024-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2026-12-31 00:00:00'),
        }
    ]
    # Crea un Dataframe de prueba con datos tipo PRO
    data_2 = [
        {
            'TIPO': 'PRO',
            'CODIGO': 1,
            'RESOLUCION': 'Resolucion de Promocion',
            'CATEGORIA': 'Asociado',
            'INICIO DE PERIODO': pd.Timestamp('2024-02-15 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2024-06-30 00:00:00'),
        }
    ]
    df_1 = pd.DataFrame(data_1)
    df_2 = pd.DataFrame(data_2)

    df = trait.agregar_promociones(df_1, df_2)

    assert df.iloc[1]['FIN DE CALCULO'] == pd.Timestamp('2024-02-14 00:00:00')
    assert df.iloc[2][df_2.columns].to_dict() == df_2.iloc[0].to_dict()


def test_cambio_fin_de_calculo():
    # Crear un DataFrame de prueba con datos de tipo ING y RAT
    data_1 = [
        {
            'TIPO': 'ING',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2023-12-31 00:00:00'),
            'INICIO DE CALCULO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE CALCULO': pd.Timestamp('2023-12-31 00:00:00'),
        },
        {
            'TIPO': 'RAT',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2024-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2026-12-31 00:00:00'),
            'INICIO DE CALCULO': pd.Timestamp('2024-01-01 00:00:00'),
            'FIN DE CALCULO': pd.Timestamp('2026-12-31 00:00:00'),
        }
    ]
    # Crea un Dataframe de prueba con datos tipo REN
    data_2 = [
        {
            'TIPO': 'REN',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2024-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2024-06-30 00:00:00'),
            'INICIO DE CALCULO': pd.Timestamp('2024-01-01 00:00:00'),
            'FIN DE CALCULO': pd.Timestamp('2024-06-30 00:00:00'),
        }
    ]
    df_1 = pd.DataFrame(data_1)
    df_2 = pd.DataFrame(data_2)

    df = trait.cambio_fin_de_calculo(df_1, df_2)

    assert df.iloc[1]['FIN DE CALCULO'] == pd.Timestamp('2024-06-30 00:00:00')
    assert df.iloc[1]['TIPO'] == "RAT"
    assert df.iloc[1]['TIPO2'] == "REN"

def test_acumulacion():
    data = [
        {
            'TIPO': 'ING',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-12-31 00:00:00'),
            'AÑOS': 3,
            'MESES': 0,
            'DIAS': 0
        },
        {
            'TIPO': 'RAT',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2023-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2025-12-31 00:00:00'),
            'AÑOS': 3,
            'MESES': 0,
            'DIAS': 0
        },
        {
            'TIPO': 'ING',
            'CODIGO': 2,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-11-15 00:00:00'),
            'AÑOS': 2,
            'MESES': 11,
            'DIAS': 15
        },
        {
            'TIPO': 'REN',
            'CODIGO': 2,
            'INICIO DE PERIODO': pd.Timestamp('2022-11-16 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2024-06-30 00:00:00'),
            'AÑOS': 1,
            'MESES': 6,
            'DIAS': 15
        },
    ]

    df_1 = pd.DataFrame(data)

    df = trait.acumulacion(df_1)

    assert df.iloc[0]['CODIGO'] == 1
    assert df.iloc[0]['AÑOS'] == 6
    assert df.iloc[0]['MESES'] == 0
    assert df.iloc[0]['DIAS'] == 0

    assert df.iloc[1]['CODIGO'] == 2
    assert df.iloc[1]['AÑOS'] == 4
    assert df.iloc[1]['MESES'] == 6
    assert df.iloc[1]['DIAS'] == 0

def test_verifica_integridad_campos():
    # Verifica la integridad de los campos (que esten todos los campos necesarios)
    data = [
        {
            'TIPO': 'ING',
            'CODIGO': 1,
            'APELLIDOS Y NOMBRES': 'SMITH, JOHN',
            'FACULTAD': 'FCEC',
            'ASIGNATURA': 'BASIC COURSE',
            'CATEGORIA': 'AUXILIAR',
            'DEDICACION': 'A tiempo completo',
            'RESOLUCION': 'N° 001 UCSS-2020/AG/R',
            'FECHA DE RESOLUCION': pd.Timestamp('2020-01-01 00:00:00'),
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-12-31 00:00:00'),
        },
    ]
    df_1 = pd.DataFrame(data)

    resultado = trait.verifica_integridad_campos(df_1)

    assert resultado == True

    del data[0]['TIPO']

    df_1 = pd.DataFrame(data)

    resultado = trait.verifica_integridad_campos(df_1)

    assert resultado == False

def test_verifica_tipo_True():
    data = [
        {
            'TIPO': 'ING',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-12-31 00:00:00'),
            'AÑOS': 3,
            'MESES': 0,
            'DIAS': 0
        },
        {
            'TIPO': 'RAT',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2023-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2025-12-31 00:00:00'),
            'AÑOS': 3,
            'MESES': 0,
            'DIAS': 0
        },
        {
            'TIPO': 'REA',
            'CODIGO': 2,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-11-15 00:00:00'),
            'AÑOS': 2,
            'MESES': 11,
            'DIAS': 15
        },
        {
            'TIPO': 'PRO',
            'CODIGO': 2,
            'INICIO DE PERIODO': pd.Timestamp('2022-11-16 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2024-06-30 00:00:00'),
            'AÑOS': 1,
            'MESES': 6,
            'DIAS': 15
        },
        {
            'TIPO': 'CES',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-12-31 00:00:00'),
            'AÑOS': 3,
            'MESES': 0,
            'DIAS': 0
        },
        {
            'TIPO': 'REN',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2023-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2025-12-31 00:00:00'),
            'AÑOS': 3,
            'MESES': 0,
            'DIAS': 0
        },
        {
            'TIPO': 'NRA',
            'CODIGO': 2,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-11-15 00:00:00'),
            'AÑOS': 2,
            'MESES': 11,
            'DIAS': 15
        },
        {
            'TIPO': 'CDE',
            'CODIGO': 2,
            'INICIO DE PERIODO': pd.Timestamp('2022-11-16 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2024-06-30 00:00:00'),
            'AÑOS': 1,
            'MESES': 6,
            'DIAS': 15
        },
        {
            'TIPO': 'LIC',
            'CODIGO': 2,
            'INICIO DE PERIODO': pd.Timestamp('2022-11-16 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2024-06-30 00:00:00'),
            'AÑOS': 1,
            'MESES': 6,
            'DIAS': 15
        },
    ]

    df_1 = pd.DataFrame(data)
    respuesta = trait.verifica_tipo(df_1) 

    assert respuesta == True

def test_verifica_tipo_False():
    data = [
        {
            'TIPO': 'ing',
            'CODIGO': 1,
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-12-31 00:00:00'),
            'AÑOS': 3,
            'MESES': 0,
            'DIAS': 0
        },
    ]

    df_1 = pd.DataFrame(data)
    respuesta = trait.verifica_tipo(df_1) 

    assert respuesta == False

def test_verifica_integridad_datos():
    data = [
        {
            'TIPO': 'ING',
            'CODIGO': 1,
            'APELLIDOS Y NOMBRES': 'SMITH, JOHN',
            'FACULTAD': 'FCEC',
            'ASIGNATURA': 'BASIC COURSE',
            'CATEGORIA': 'AUXILIAR',
            'DEDICACION': 'A tiempo completo',
            'RESOLUCION': 'N° 001 UCSS-2020/AG/R',
            'FECHA DE RESOLUCION': pd.Timestamp('2020-01-01 00:00:00'),
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2022-12-31 00:00:00'),
        },
    ]
    df_1 = pd.DataFrame(data)

    resultado = trait.verifica_integridad_datos(df_1)

    assert resultado == True

    ## TIPO = False
    data1 = data
    data1[0]['TIPO'] = ""

    df_1 = pd.DataFrame(data1)
    resultado = trait.verifica_integridad_datos(df_1)

    assert resultado == False

    ## CODIGO = False
    data1 = data
    data1[0]['CODIGO'] = 0

    df_1 = pd.DataFrame(data1)
    resultado = trait.verifica_integridad_datos(df_1)

    assert resultado == False

    ## INICIO DE PERIODO = False
    data1 = data
    data1[0]['INICIO DE PERIODO'] = ""

    df_1 = pd.DataFrame(data1)
    resultado = trait.verifica_integridad_datos(df_1)

    assert resultado == False

    ## FIN DE PERIODO = False
    data1 = data
    data1[0]['FIN DE PERIODO'] = ""

    df_1 = pd.DataFrame(data1)
    resultado = trait.verifica_integridad_datos(df_1)

    assert resultado == False

def test_registro_por_docente():
    # Crear un DataFrame de prueba con datos de dos docentes ING, RAT y REN
    data = [
        {
            'TIPO': 'ING',
            'CODIGO': 1,
            'APELLIDOS Y NOMBRES': 'DOE, JOHN',
            'ASIGNATURA': 'COURSE 1',
            'CATEGORIA': 'ROOKIE',
            'DEDICACION': 'PART TIME',
            'FACULTAD': 'FCEC',
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2021-12-31 00:00:00'),
            'INICIO DE CALCULO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE CALCULO': pd.Timestamp('2021-12-31 00:00:00'),  
            'AÑOS': 2,
            'MESES': 0,
            'DIAS': 0,
        },
        {
            'TIPO': 'RAT',
            'CODIGO': 1,
            'APELLIDOS Y NOMBRES': 'DOE, JOHN',
            'ASIGNATURA': 'COURSE 1',
            'CATEGORIA': 'MASTER',
            'DEDICACION': 'FULL TIME',
            'FACULTAD': 'FCEC',
            'INICIO DE PERIODO': pd.Timestamp('2022-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2023-12-31 00:00:00'),
            'INICIO DE CALCULO': pd.Timestamp('2022-01-01 00:00:00'),
            'FIN DE CALCULO': pd.Timestamp('2023-12-31 00:00:00'),
            'AÑOS': 2,
            'MESES': 0,
            'DIAS': 0,
        },
        {
            'TIPO': 'ING',
            'CODIGO': 2,
            'APELLIDOS Y NOMBRES': 'DOE, JANE',
            'ASIGNATURA': 'COURSE 2',
            'CATEGORIA': 'ROOKIE',
            'DEDICACION': 'FULL TIME',
            'FACULTAD': 'FCEH',
            'INICIO DE PERIODO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2021-12-31 00:00:00'),
            'INICIO DE CALCULO': pd.Timestamp('2020-01-01 00:00:00'),
            'FIN DE CALCULO': pd.Timestamp('2021-12-31 00:00:00'),
            'TIPO2': 'REN',
            'AÑOS': 2,
            'MESES': 0,
            'DIAS': 0,
        },
        {
            'TIPO': 'RAT',
            'CODIGO': 2,
            'APELLIDOS Y NOMBRES': 'DOE, JANE',
            'ASIGNATURA': 'COURSE 2',
            'CATEGORIA': 'ROOKIE',
            'DEDICACION': 'PART TIME',
            'FACULTAD': 'FCEH',
            'INICIO DE PERIODO': pd.Timestamp('2023-01-01 00:00:00'),
            'FIN DE PERIODO': pd.Timestamp('2024-12-31 00:00:00'),
            'INICIO DE CALCULO': pd.Timestamp('2023-01-01 00:00:00'),
            'FIN DE CALCULO': pd.Timestamp('2024-12-31 00:00:00'),
            'AÑOS': 2,
            'MESES': 0,
            'DIAS': 0,
        }
    ]
    df = pd.DataFrame(data)
    
    df_1 = trait.registro_por_docente(df)

    assert df_1.iloc[0]['CODIGO'] == 1
    assert df_1.iloc[0]['CATEGORIA'] == 'MASTER'
    assert df_1.iloc[0]['DEDICACION'] == 'FULL TIME'
    assert df_1.iloc[0]['INICIO DE PERIODO'] == pd.Timestamp('2020-01-01 00:00:00')
    assert df_1.iloc[0]['FIN DE PERIODO'] == pd.Timestamp('2023-12-31 00:00:00')
    assert df_1.iloc[0]['INICIO DE CALCULO'] == pd.Timestamp('2020-01-01 00:00:00')
    assert df_1.iloc[0]['FIN DE CALCULO'] == pd.Timestamp('2023-12-31 00:00:00')
    assert df_1.iloc[0]['AÑOS'] == 4
    assert df_1.iloc[0]['MESES'] == 0
    assert df_1.iloc[0]['DIAS'] == 0
    
    assert df_1.iloc[1]['CODIGO'] == 2
    assert df_1.iloc[1]['CATEGORIA'] == 'ROOKIE'
    assert df_1.iloc[1]['DEDICACION'] == 'PART TIME'
    assert df_1.iloc[1]['INICIO DE PERIODO'] == pd.Timestamp('2020-01-01 00:00:00')
    assert df_1.iloc[1]['FIN DE PERIODO'] == pd.Timestamp('2024-12-31 00:00:00')
    assert df_1.iloc[1]['INICIO DE CALCULO'] == pd.Timestamp('2020-01-01 00:00:00')
    assert df_1.iloc[1]['FIN DE CALCULO'] == pd.Timestamp('2024-12-31 00:00:00')
    assert df_1.iloc[1]['AÑOS'] == 4
    assert df_1.iloc[1]['MESES'] == 0
    assert df_1.iloc[1]['DIAS'] == 0
    assert df_1.iloc[1]['TIPO2'] == "REN"    


