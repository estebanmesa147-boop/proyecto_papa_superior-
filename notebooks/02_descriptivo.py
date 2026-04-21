##Celda 1 — Librerías
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# Estilo general de las gráficas
sns.set_theme(style='whitegrid')
plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.family'] = 'sans-serif'

##Celda 2 — Cargar dataset maestro
PROCESSED = r"C:\Users\anaso\OneDrive\Desktop\Analisis de Datos 2026\proyecto_papa_superior_corabastos\data\processed"

meses_orden = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
               'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

df = pd.read_parquet(f"{PROCESSED}\\papa_superior_corabastos_2019_2025.parquet")
df['mes'] = pd.Categorical(df['mes'], categories=meses_orden, ordered=True)
df = df.sort_values(['Año', 'mes']).reset_index(drop=True)

print(df.shape)
df.head()

##Celda 3 — Estadísticas básicas
resumen = df.groupby('Año').agg(
    precio_min    = ('precio_promedio', 'min'),
    precio_max    = ('precio_promedio', 'max'),
    precio_medio  = ('precio_promedio', 'mean'),
    precio_std    = ('precio_promedio', 'std'),
    toneladas_total = ('Toneladas', 'sum'),
    toneladas_media = ('Toneladas', 'mean')
).round(2)

print(resumen.to_string())

##Celda 4 — Evolución anual del precio promedio
precio_anual = df.groupby('Año')['precio_promedio'].mean().reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(precio_anual['Año'], precio_anual['precio_promedio'],
        marker='o', linewidth=2.5, color='#E07B39', markersize=8)

# Etiquetas de valor en cada punto
for _, row in precio_anual.iterrows():
    ax.annotate(f"${row['precio_promedio']:,.0f}",
                xy=(row['Año'], row['precio_promedio']),
                xytext=(0, 12), textcoords='offset points',
                ha='center', fontsize=9)

ax.set_title('Precio promedio anual — Papa Superior Corabastos (2019–2025)', fontsize=13, fontweight='bold')
ax.set_xlabel('Año')
ax.set_ylabel('Precio promedio ($/kg)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.set_xticks(precio_anual['Año'])
plt.tight_layout()
plt.savefig(f"{PROCESSED}\\grafico_precio_anual.png", bbox_inches='tight')
plt.show()

##Celda 5 — Evolución anual del abastecimiento
abast_anual = df.groupby('Año')['Toneladas'].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(abast_anual['Año'], abast_anual['Toneladas'],
              color='#4C9BE8', width=0.6, edgecolor='white')

# Etiquetas encima de cada barra
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 1500,
            f"{bar.get_height():,.0f} t",
            ha='center', fontsize=9)

ax.set_title('Abastecimiento total anual — Papa Superior Corabastos (2019–2025)', fontsize=13, fontweight='bold')
ax.set_xlabel('Año')
ax.set_ylabel('Toneladas')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax.set_xticks(abast_anual['Año'])
plt.tight_layout()
plt.savefig(f"{PROCESSED}\\grafico_abastecimiento_anual.png", bbox_inches='tight')
plt.show()

##Celda 6 — Precio y abastecimiento en una sola vista (doble eje)
pythonfig, ax1 = plt.subplots(figsize=(12, 5))

# Eje izquierdo — precio
color_precio = '#E07B39'
ax1.plot(precio_anual['Año'], precio_anual['precio_promedio'],
         marker='o', color=color_precio, linewidth=2.5, label='Precio promedio')
ax1.set_ylabel('Precio promedio ($/kg)', color=color_precio)
ax1.tick_params(axis='y', labelcolor=color_precio)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

# Eje derecho — abastecimiento
ax2 = ax1.twinx()
color_abast = '#4C9BE8'
ax2.bar(abast_anual['Año'], abast_anual['Toneladas'],
        color=color_abast, alpha=0.4, width=0.6, label='Toneladas')
ax2.set_ylabel('Toneladas', color=color_abast)
ax2.tick_params(axis='y', labelcolor=color_abast)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

ax1.set_title('Precio vs Abastecimiento anual — Papa Superior Corabastos (2019–2025)',
              fontsize=13, fontweight='bold')
ax1.set_xlabel('Año')
ax1.set_xticks(precio_anual['Año'])

# Leyenda combinada
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
plt.savefig(f"{PROCESSED}\\grafico_precio_vs_abastecimiento.png", bbox_inches='tight')
plt.show()

##Celda 7 — Heatmap precio por año y mes
pivot_precio = df.pivot_table(
    index='Año', columns='mes', values='precio_promedio'
)

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(pivot_precio, annot=True, fmt='.0f', cmap='YlOrRd',
            linewidths=0.5, ax=ax,
            cbar_kws={'label': '$/kg'})

ax.set_title('Heatmap de precio promedio mensual — Papa Superior Corabastos (2019–2025)',
             fontsize=13, fontweight='bold')
ax.set_xlabel('Mes')
ax.set_ylabel('Año')
plt.tight_layout()
plt.savefig(f"{PROCESSED}\\grafico_heatmap_precio.png", bbox_inches='tight')
plt.show()

## Celda 8 — Guardar tabla resumen para Power BI

resumen.to_csv(f"{PROCESSED}\\resumen_anual.csv")
print("✅ Tabla resumen guardada")