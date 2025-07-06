import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(layout='wide')


@st.cache_data
def carregar_dados():
    df = pd.read_excel('agendamento de consultas atualizado.xlsx')
    df['ano_mes'] = df['Data'].dt.to_period('M')
    return df


df = carregar_dados()

horario = df['hora_numeric'].value_counts().reset_index()
horario['hora_numeric'] = horario['hora_numeric'].astype('int')
horario['count'] = horario['count'].astype(int)

lista_profissional = ['Todos']
for v in df['Profissional'].unique():
    lista_profissional.append(v)

with st.sidebar:
    st.title('REDE SANTA SAÚDE💊')
    st.subheader('Agendamento de consultas🗒️')
    seletor = st.selectbox('Filtre por profissional',
                           lista_profissional)
    option = option_menu(
        menu_title='Menu',
        options=['Análise geral', 'Análise temporal']
    )
if option == 'Análise geral':
    if seletor == 'Todos':
        co1, co2, co3 = st.columns(3)
        with co1:
            st.metric(f'Horário de pico:',
                      f'{horario['hora_numeric'][0]}:00', delta=int(horario['count'][0]))
        with co2:
            st.metric(f'Horário de pico:',
                      f'{horario['hora_numeric'][1]}:00', delta=int(horario['count'][1]))

        with co3:
            st.metric(f'Horário de pico:',
                      f'{horario['hora_numeric'][2]}:00', delta=int(horario['count'][2]))

        co1, co2 = st.columns(2)
        with co1:
            st.subheader('Número de consultas agendadas por profissional')

            dataset = df['Profissional'].value_counts().reset_index()
            dataset.rename(columns={'count': 'Número'}, inplace=True)
            dataset.set_index('Profissional', inplace=True)
            st.dataframe(dataset)

        with co2:
            st.subheader('Número de consultas por serviço')

            dataset = df['Serviço'].value_counts().reset_index()
            dataset.rename(columns={'count': 'Número'}, inplace=True)
            dataset.set_index('Serviço', inplace=True)
            st.dataframe(dataset)

        st.divider()

        st.subheader('Percentual de comparecimento')

        grupo = df.groupby('Status').size().reset_index()
        grupo['porcentagem'] = grupo[0].div(grupo[0].sum(), axis=0)*100
        grupo['porcentagem'] = [f'{p:.1f}%' for p in grupo['porcentagem']]

        fig = px.pie(grupo, values=0, hover_data=[
            'porcentagem'], height=500, names='Status')
        st.plotly_chart(fig)

        st.divider()

        st.subheader('Número de Serviços agendados por profissional')

        serviço_por_profissional = df.groupby(
            ['Profissional'])['Serviço'].value_counts().sort_values(ascending=False).reset_index()

        serviço_por_profissional.rename(
            columns={'count': 'Número'}, inplace=True)
        serviço_por_profissional.set_index('Profissional', inplace=True)
        st.dataframe(serviço_por_profissional)

    if seletor != 'Todos':
        dados = df[df['Profissional'] == seletor]

        # Recalcular horários de pico para o profissional selecionado
        horario_filtrado = dados['hora_numeric'].value_counts().reset_index()
        horario_filtrado['hora_numeric'] = horario_filtrado['hora_numeric'].astype(
            'int')
        horario_filtrado['count'] = horario_filtrado['count'].astype(int)

        # Mostrar apenas o horário de pico principal
        if len(horario_filtrado) > 0:
            st.metric(f'Horário de pico - {seletor}:',
                      f'{horario_filtrado['hora_numeric'][0]}:00',
                      delta=int(horario_filtrado['count'][0]))

        co1, co2 = st.columns(2)
        with co1:
            st.subheader(f'Consultas de {seletor}')

            dataset = dados['Serviço'].value_counts().reset_index()
            dataset.rename(columns={'count': 'Número'}, inplace=True)
            dataset.set_index('Serviço', inplace=True)
            st.dataframe(dataset)

        with co2:
            st.subheader(f'Status das consultas - {seletor}')

            dataset = dados['Status'].value_counts().reset_index()
            dataset.rename(columns={'count': 'Número'}, inplace=True)
            dataset.set_index('Status', inplace=True)
            st.dataframe(dataset)

        st.divider()

        st.subheader(f'Percentual de comparecimento - {seletor}')

        grupo = dados.groupby('Status').size().reset_index()
        grupo['porcentagem'] = grupo[0].div(grupo[0].sum(), axis=0)*100
        grupo['porcentagem'] = [f'{p:.1f}%' for p in grupo['porcentagem']]

        fig = px.pie(grupo, values=0, hover_data=[
            'porcentagem'], height=500, names='Status')
        st.plotly_chart(fig)

        st.divider()

        st.subheader(f'Resumo - {seletor}')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de consultas", len(dados))
        with col2:
            st.metric("Serviços diferentes", dados['Serviço'].nunique())
        with col3:
            comparecimento = dados[dados['Status'] ==
                                   'Compareceu'].shape[0] / len(dados) * 100
            st.metric("Taxa de comparecimento", f"{comparecimento:.1f}%")

if option == 'Análise temporal':
    if seletor == 'Todos':

        st.subheader(
            'Total de agendamento de consultas por hora ao longo dos meses')

        df['ano_mes'] = df['ano_mes'].astype(str)

        hora = st.multiselect('Escolha a hora para a análise',
                              df['hora_numeric'].unique(),
                              default=df['hora_numeric'].unique()[0])
        dados = df[df['hora_numeric'].isin(hora)]

        horarios = dados.groupby('ano_mes')[
            'hora_numeric'].value_counts().reset_index()

        fig = px.line(horarios, x='ano_mes', y='count', color='hora_numeric',
                      labels={
                          'ano_mes': 'Mês',
                          'count': 'Número de Consultas',
                          'hora_numeric': 'Horário'
                      })

        st.plotly_chart(fig)

        st.divider()

        st.subheader(
            'Total de agendamento de consultas por serviço ao longo dos meses')

        df['ano_mes'] = df['ano_mes'].astype(str)

        serviço = st.multiselect('Escolha o serviço para a análise',
                                 df['Serviço'].unique(),
                                 default=df['Serviço'].unique()[0])
        dados = df[df['Serviço'].isin(serviço)]

        servicos = dados.groupby('ano_mes')[
            'Serviço'].value_counts().reset_index()

        fig = px.line(servicos, x='ano_mes', y='count', color='Serviço',
                      labels={
                          'ano_mes': 'Mês',
                          'count': 'Número de Consultas',
                      })

        st.plotly_chart(fig)

        st.divider()

        st.subheader(
            'Total de agendamento de serviços por profissional ao longo do tempo')

        df['ano_mes'] = df['ano_mes'].astype(str)

        profissional = st.multiselect('Escolha o profissional para a análise',
                                      df['Profissional'].unique(),
                                      default=df['Profissional'].unique()[0])
        dados = df[df['Profissional'].isin(profissional)]

        servicos = dados.groupby('ano_mes')[
            'Profissional'].value_counts().reset_index()

        fig = px.line(servicos, x='ano_mes', y='count', color='Profissional',
                      labels={
                          'ano_mes': 'Mês',
                          'count': 'Número de Consultas',
                      })

        st.plotly_chart(fig)
    if seletor != 'Todos':

        dados = df[df['Profissional'] == seletor]

        st.subheader(f'Análise Temporal - {seletor}')

        # Converter ano_mes para string
        dados['ano_mes'] = dados['ano_mes'].astype(str)

        # Análise 1: Consultas por horário ao longo do tempo
        st.subheader(f'Agendamentos por hora ao longo dos meses - {seletor}')

        hora = st.multiselect('Escolha a hora de análise',
                              dados['hora_numeric'].unique(),
                              default=dados['hora_numeric'].unique()[0])
        dados_hora = dados[dados['hora_numeric'].isin(hora)]

        horarios = dados_hora.groupby(
            'ano_mes')['hora_numeric'].value_counts().reset_index()

        fig = px.line(horarios, x='ano_mes', y='count', color='hora_numeric',
                      title=f'Consultas por Horário - {seletor}',
                      labels={
                          'ano_mes': 'Mês',
                          'count': 'Número de Consultas',
                          'hora_numeric': 'Horário'
                      })

        # Personalizar legenda
        fig.for_each_trace(lambda t: t.update(name=f"{t.name}:00h"))
        fig.update_layout(
            legend=dict(
                title="Horário",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Análise 2: Serviços ao longo do tempo
        st.subheader(f'Serviços agendados ao longo dos meses - {seletor}')

        servico = st.multiselect('Escolha o serviço de análise',
                                 dados['Serviço'].unique(),
                                 default=dados['Serviço'].unique()[0])
        dados_servico = dados[dados['Serviço'].isin(servico)]

        servicos = dados_servico.groupby(
            'ano_mes')['Serviço'].value_counts().reset_index()

        fig = px.line(servicos, x='ano_mes', y='count', color='Serviço',
                      title=f'Serviços ao Longo do Tempo - {seletor}',
                      labels={
                          'ano_mes': 'Mês',
                          'count': 'Número de Consultas',
                          'Serviço': 'Serviço'
                      })

        st.plotly_chart(fig, use_container_width=True)
