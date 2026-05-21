import pandas as pd


def limpiar_ranking_vendedores(file):

    # Leer archivo sin encabezado
    df = pd.read_excel(file, header=None)

    # Buscar fila donde empieza el encabezado real
    fila_header = None

    for i, row in df.iterrows():

        valores = row.astype(str).tolist()

        if "Vendedor" in valores:
            fila_header = i
            break

    if fila_header is None:
        raise Exception("No se encontró encabezado válido")

    # Leer nuevamente usando encabezado correcto
    df = pd.read_excel(file, header=fila_header)

    # Eliminar filas vacías
    df = df.dropna(how="all")

    # Eliminar filas de totales
    df = df[
        ~df.iloc[:, 0]
        .astype(str)
        .str.contains("Total|TOTAL|Totales", na=False)
    ]

    # Limpiar nombres columnas
    df.columns = [
        str(col).strip().replace("\n", " ")
        for col in df.columns
    ]

    # Resetear índice
    df = df.reset_index(drop=True)

    return df
