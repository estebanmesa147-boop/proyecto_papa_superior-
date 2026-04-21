#Celda 1 — Librerías

import pandas as pd

#Celda 2 — Rutas
RAW = r"C:\Users\anaso\OneDrive\Desktop\Analisis de Datos 2026\proyecto_papa_superior_corabastos\data\raw"
PROCESSED = r"C:\Users\anaso\OneDrive\Desktop\Analisis de Datos 2026\proyecto_papa_superior_corabastos\data\processed"

#Celda 3 — Carga de datos crudos

df_abast_raw = pd.read_csv(
    f"{RAW}\\ABASTECIMIENTO_PAPA_2013_2025.csv",
    encoding='latin1'
)

df_precios_raw = pd.read_excel(
    f"{RAW}\\Base_Precios_historica_13_2026.xlsx",
    sheet_name='Base Papa'
)

print("Abastecimiento:", df_abast_raw.shape)
print("Precios:", df_precios_raw.shape)

#Celda 4 — Limpiar abastecimiento

df_abast = df_abast_raw.copy()

# Corregir columna con encoding roto
df_abast.columns = [
    'Central', 'fecha', 'Cod_Depto', 'Cod_Mun',
    'Departamento', 'Municipio', 'variedad',
    'semana', 'Año', 'CantKg', 'mes', 'Toneladas'
]

# Corregir inconsistencia en mes (julio → Julio)
df_abast['mes'] = df_abast['mes'].str.capitalize()

# Convertir fecha a datetime
df_abast['fecha'] = pd.to_datetime(df_abast['fecha'], format='%d/%m/%Y')

print("✅ Abastecimiento limpio")
print(df_abast.dtypes)

#Celda 5 — Filtrar abastecimiento

df_abast_filtrado = df_abast[
    (df_abast['Central'] == 'Corabastos') &
    (df_abast['variedad'] == 'Superior') &
    (df_abast['Año'].between(2019, 2025))
].copy()

print("Filas después del filtro:", df_abast_filtrado.shape[0])
print("Años:", sorted(df_abast_filtrado['Año'].unique()))

#Celda 6 — Limpiar precios  

df_precios = df_precios_raw.copy()

# Capitalizar mes
df_precios['mes'] = df_precios['mes'].str.capitalize()

# Filtrar Bogotá + Superior + 2019-2025
df_precios_filtrado = df_precios[
    (df_precios['ciudad'] == 'Bogotá D.C.') &
    (df_precios['variedad'] == 'Superior') &
    (df_precios['year'].between(2019, 2025))
].copy()

# Quedarse solo con columnas útiles
df_precios_filtrado = df_precios_filtrado[[
    'year', 'mes', 'semana', 'fecha3', 'precio'
]].rename(columns={'year': 'Año', 'fecha3': 'fecha'})

print("✅ Precios limpios")
print("Filas después del filtro:", df_precios_filtrado.shape[0])
print("Años:", sorted(df_precios_filtrado['Año'].unique()))

## Celda 7 — Agregar a nivel mensual

# Abastecimiento — suma de toneladas por mes
abast_mensual = df_abast_filtrado.groupby(
    ['Año', 'mes'], as_index=False
)['Toneladas'].sum()

# Precios — promedio por mes
precios_mensual = df_precios_filtrado.groupby(
    ['Año', 'mes'], as_index=False
)['precio'].mean().rename(columns={'precio': 'precio_promedio'})

print("Abastecimiento mensual:", abast_mensual.shape)
print("Precios mensual:", precios_mensual.shape)

#Celda 8 — Crear dataset maestro

meses_orden = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

df_maestro = pd.merge(abast_mensual, precios_mensual, on=['Año', 'mes'], how='inner')
df_maestro['mes'] = pd.Categorical(df_maestro['mes'], categories=meses_orden, ordered=True)
df_maestro = df_maestro.sort_values(['Año', 'mes']).reset_index(drop=True)

print("✅ Dataset maestro creado")
print("Shape:", df_maestro.shape)
print()
print(df_maestro.head(12))

## Celda 9 — Guardar archivos procesados

df_maestro.to_csv(
    f"{PROCESSED}\\papa_superior_corabastos_2019_2025.csv",
    index=False
)

df_maestro.to_parquet(
    f"{PROCESSED}\\papa_superior_corabastos_2019_2025.parquet",
    index=False
)

print("✅ Archivos guardados en /data/processed/")