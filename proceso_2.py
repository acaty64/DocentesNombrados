import pandas as pd
import sys


def proceso_2(archivo_excel):

    df = pd.read_excel(archivo_excel, sheet_name='salida')
    # print("Datos cargados desde el archivo Excel:")
    # print(df.head(5))

    # Por cada codigo,
    df_codigos = df['CODIGO'].unique()
    matched_rows = []
    for _, registro in df_codigos.iterrows():
        # Identificar registros con el mismo CODIGO del df_FILTRADO, preservando el número de registro original
        codigo_filtrado = df.loc[df['CODIGO'] == registro['CODIGO']].reset_index().rename(columns={'index': 'NUM_REGISTRO'})





    # Grabar nueva hoja en el mismo archivo Excel con los datos procesados
    with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='Nueva_Hoja', index=False)



def main():
    if len(sys.argv) != 2:
        print('Uso: python proceso_2.py <ruta_al_archivo_excel>')
        sys.exit(1)

    archivo_excel = sys.argv[1]
    proceso_2(archivo_excel)


if __name__ == "__main__":
    main()

