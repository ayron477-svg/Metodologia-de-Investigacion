import pandas as pd

# ------------------------------------------------------------
#                       Funciones 
# ------------------------------------------------------------

def tabla_de_frecuencias(datos):
    total = len(datos.columns) - 1
    tabla_frecuencia = pd.DataFrame({
    "Área": datos["Areas"],
    "Frecuencia": (datos.drop(columns=["Areas"]) == "x").sum(axis=1)
    })
    tabla_frecuencia["Porcentaje"] = (tabla_frecuencia["Frecuencia"] / total * 100).round(2)
    tabla_frecuencia = tabla_frecuencia.sort_values(by='Frecuencia', ascending=False) #ordenarla mayor a menor
    
    return tabla_frecuencia


def tabla_comparativa(tablaOfertas, tablaUniversidades):
    tablaComparativa = tablaOfertas.merge(
        tablaUniversidades,
        on="Área",
        how="outer",
        suffixes=("_Ofertas", "_Universidades") # aclaración de ofertas y universidades
    )
    tablaComparativa = tablaComparativa.sort_values( by="Frecuencia_Ofertas",ascending=False) #ordenar según ofertas de mayor a menor

    return tablaComparativa


def indice_de_correlacion(universidades, tablaOfertas):
    unis = universidades.copy()

    matriz = (
        unis.set_index('Areas')
          .eq('x')
          .astype(int)
    )
    frecuencias = tablaOfertas.set_index('Área')['Frecuencia']

    # 
    matriz = matriz.loc[frecuencias.index]
    indices = matriz.mul(frecuencias, axis=0).sum(axis=0) / frecuencias.sum()
    indices = indices.sort_values(ascending=False)

    return indices

# ------------------------------------------------------------
#                       Ejecución 
# ------------------------------------------------------------

#leer csv
ofertas = pd.read_csv("tablas - Ofertas.csv")
universidades = pd.read_csv("tablas - Universidades.csv")

#generar tablas
tablaOfertas = tabla_de_frecuencias(ofertas)
tablaUniversidades = tabla_de_frecuencias(universidades)
tablaComparativa = tabla_comparativa(tablaOfertas,tablaUniversidades)
indiceCorrelacion = indice_de_correlacion(universidades,tablaOfertas)

print(tablaComparativa)
print(indiceCorrelacion)