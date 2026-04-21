##Celda 1 — Librerías

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

sns.set_theme(style='whitegrid')
plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.family'] = 'sans-serif'

## Celda 2 — Cargar datos

PROCESSED = r"C:\Users\anaso\OneDrive\Desktop\Analisis de Datos 2026\proyecto_papa_superior_corabastos\data\processed"
RAW = r"C:\Users\anaso\OneDrive\Desktop\Analisis de Datos 2026\proyecto_papa_superior_corabastos\data\raw"

meses_orden = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
               'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

# Dataset mensual (ya limpio de Fase 1)
df_mensual = pd.read_parquet(f"{PROCESSED}\\papa_superior_corabastos_2019_2025.parquet")
df_mensual['mes'] = pd.Categorical(df_mensual['mes'], categories=meses_orden, ordered=True)
df_mensual = df_mensual.sort_values(['Año','mes']).reset_index(drop=True)

# Dataset semanal (construido desde raw)
df_abast_raw = pd.read_csv(f"{RAW}\\ABASTECIMIENTO_PAPA_2013_2025.csv", encoding='latin1')
df_abast_raw.columns = ['Central','fecha','Cod_Depto','Cod_Mun','Departamento',
                        'Municipio','variedad','semana','Año','CantKg','mes','Toneladas']
df_abast_raw['mes'] = df_abast_raw['mes'].str.capitalize()

df_precios_raw = pd.read_excel(f"{RAW}\\Base_Precios_historica_13_2026.xlsx", sheet_name='Base Papa')
df_precios_raw['mes'] = df_precios_raw['mes'].str.capitalize()

abast_semanal = df_abast_raw[
    (df_abast_raw['Central'] == 'Corabastos') &
    (df_abast_raw['variedad'] == 'Superior') &
    (df_abast_raw['Año'].between(2019, 2025))
].groupby(['Año','mes','semana'], as_index=False)['Toneladas'].sum()

precios_semanal = df_precios_raw[
    (df_precios_raw['ciudad'] == 'Bogotá D.C.') &
    (df_precios_raw['variedad'] == 'Superior') &
    (df_precios_raw['year'].between(2019, 2025))
][['year','mes','semana','precio']].rename(columns={'year':'Año'})

df_semanal = pd.merge(abast_semanal, precios_semanal, on=['Año','mes','semana'], how='inner')

print("Mensual:", df_mensual.shape)
print("Semanal:", df_semanal.shape)

##Celda 3 — Calcular correlaciones

# Correlaciones mensuales
pearson_m, p_pearson_m   = stats.pearsonr(df_mensual['Toneladas'], df_mensual['precio_promedio'])
spearman_m, p_spearman_m = stats.spearmanr(df_mensual['Toneladas'], df_mensual['precio_promedio'])

# Correlaciones semanales
pearson_s, p_pearson_s   = stats.pearsonr(df_semanal['Toneladas'], df_semanal['precio'])
spearman_s, p_spearman_s = stats.spearmanr(df_semanal['Toneladas'], df_semanal['precio'])

# Rezago 1 mes — ¿el abastecimiento de este mes afecta el precio del mes siguiente?
df_mensual['precio_lag1'] = df_mensual['precio_promedio'].shift(1)
df_lag = df_mensual.dropna(subset=['precio_lag1'])
pearson_lag, p_lag = stats.pearsonr(df_lag['Toneladas'], df_lag['precio_lag1'])

resumen_corr = pd.DataFrame({
    'Nivel'       : ['Mensual', 'Semanal', 'Rezago 1 mes'],
    'Pearson r'   : [round(pearson_m,4), round(pearson_s,4), round(pearson_lag,4)],
    'Pearson p'   : [round(p_pearson_m,4), round(p_pearson_s,4), round(p_lag,4)],
    'Spearman r'  : [round(spearman_m,4), round(spearman_s,4), '-'],
    'Spearman p'  : [round(p_spearman_m,4), round(p_spearman_s,4), '-'],
    'Significativo': ['Sí (Spearman)','Sí (Spearman)','No']
})

print(resumen_corr.to_string(index=False))

## Celda 4 — Scatter mensual con línea de tendencia

fig, ax = plt.subplots(figsize=(9, 6))

# Puntos coloreados por año
años = sorted(df_mensual['Año'].unique())
colores = sns.color_palette('tab10', len(años))

for año, color in zip(años, colores):
    sub = df_mensual[df_mensual['Año'] == año]
    ax.scatter(sub['Toneladas'], sub['precio_promedio'],
               label=str(año), color=color, s=60, alpha=0.85)

# Línea de tendencia general
m, b, *_ = stats.linregress(df_mensual['Toneladas'], df_mensual['precio_promedio'])
x_range = pd.Series([df_mensual['Toneladas'].min(), df_mensual['Toneladas'].max()])
ax.plot(x_range, m * x_range + b, color='black', linewidth=1.5,
        linestyle='--', label=f'Tendencia (r={pearson_m:.2f})')

ax.set_title('Correlación mensual: Precio vs Abastecimiento\nPapa Superior — Corabastos (2019–2025)',
             fontsize=13, fontweight='bold')
ax.set_xlabel('Toneladas abastecidas (mensual)')
ax.set_ylabel('Precio promedio ($/kg)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.legend(title='Año', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()
plt.savefig(f"{PROCESSED}\\grafico_scatter_mensual.png", bbox_inches='tight')
plt.show()

## Celda 5 — Scatter semanal

fig, ax = plt.subplots(figsize=(9, 6))

for año, color in zip(años, colores):
    sub = df_semanal[df_semanal['Año'] == año]
    ax.scatter(sub['Toneladas'], sub['precio'],
               label=str(año), color=color, s=40, alpha=0.7)

m2, b2, *_ = stats.linregress(df_semanal['Toneladas'], df_semanal['precio'])
x_range2 = pd.Series([df_semanal['Toneladas'].min(), df_semanal['Toneladas'].max()])
ax.plot(x_range2, m2 * x_range2 + b2, color='black', linewidth=1.5,
        linestyle='--', label=f'Tendencia (r={pearson_s:.2f})')

ax.set_title('Correlación semanal: Precio vs Abastecimiento\nPapa Superior — Corabastos (2019–2025)',
             fontsize=13, fontweight='bold')
ax.set_xlabel('Toneladas abastecidas (semanal)')
ax.set_ylabel('Precio ($/kg)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.legend(title='Año', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()
plt.savefig(f"{PROCESSED}\\grafico_scatter_semanal.png", bbox_inches='tight')
plt.show()

## Celda 6 — Guardar tabla de correlaciones

resumen_corr.to_csv(f"{PROCESSED}\\resumen_correlaciones.csv", index=False)
print("✅ Tabla de correlaciones guardada")
