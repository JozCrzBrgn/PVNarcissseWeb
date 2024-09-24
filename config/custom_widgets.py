import streamlit as st
import plotly.graph_objects as go

def meta(valor_meta, diferencia_meta):
    return st.metric(
        label="Meta",
        value=f"$ {valor_meta:,.0f}",
        delta=diferencia_meta,
        label_visibility="collapsed",
    )

def grafico_barras(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Fecha'],
        y=df['Ventas'],
        text=df['Ventas'],
        marker_color='#3cd8b9',
    ))
    # Ajustar el diseño del gráfico
    fig.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Ventas',
        xaxis_tickformat='%d-%m',
        margin=dict(t=20, b=0, l=40, r=10),
        height=250,
    )
    # Mostrar el gráfico en Streamlit
    return st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def grafico_velocimetro(ventas_actuales, ventas_objetivo):
    if ventas_actuales >= ventas_objetivo:
        color = "green"
    elif ventas_actuales >= ventas_objetivo/2:
        color = "orange"
    else:
        color = "red"
    fig1 = go.Figure(
        go.Indicator(
            value=ventas_actuales,
            mode="gauge+number",
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 20}, 'prefix': '$'},
            #title={'text': "Indicador de ventas", 'font': {'size': 24}},   
            gauge={
                'axis': {'range': [0, ventas_objetivo*1.5], 'tickwidth': 1},
                'bar': {'color': color}
                }
            ))
    # Ajustar los márgenes para reducir el espacio vacío
    fig1.update_layout(margin=dict(t=0, b=100, l=50, r=50))
    # Mostrar el gráfico en Streamlit
    return st.plotly_chart(fig1, use_container_width=False, config={'displayModeBar': False})