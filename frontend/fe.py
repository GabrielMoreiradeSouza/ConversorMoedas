import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Conversor de Moedas", page_icon="💱")

st.title(" Conversor de Moedas - Tempo Real + Gráficos de Valorização")

# --------------------------
# CONVERSOR DE MOEDAS
# --------------------------
moedas = {
    "Real (BRL)": "BRL",
    "Dólar (USD)": "USD",
    "Euro (EUR)": "EUR",
    "Libra (GBP)": "GBP"
}

moeda_origem_nome = st.selectbox("Selecione a moeda de origem:", list(moedas.keys()))
moeda_origem = moedas[moeda_origem_nome]

valor = st.number_input(f"Digite o valor em {moeda_origem_nome}:", min_value=0.0, format="%.2f", value=1.0)

moedas_destino = [codigo for codigo in moedas.values() if codigo != moeda_origem]
pares = []

for destino in moedas_destino:
    if moeda_origem == "BRL":
        pares.append(f"{destino}-BRL")
    elif destino == "BRL":
        pares.append(f"{moeda_origem}-BRL")
    else:
        pares.append(f"{moeda_origem}-{destino}")

try:
    url = f"https://economia.awesomeapi.com.br/json/last/{','.join(pares)}"
    response = requests.get(url)
    data = response.json()

    def pegar_cotacao(de, para):
        if de == "BRL":
            par = f"{para}BRL"
            return 1 / float(data[par]['bid'])
        elif para == "BRL":
            par = f"{de}BRL"
            return float(data[par]['bid'])
        else:
            par = f"{de}{para}"
            return float(data[par]['bid'])

    st.markdown("###  Conversão em Tempo Real:")

    col1, col2, col3 = st.columns(3)
    resultados = []

    for i, destino in enumerate(moedas_destino):
        cotacao = pegar_cotacao(moeda_origem, destino)
        valor_convertido = valor * cotacao
        simbolo = {
            "BRL": "R$",
            "USD": "$",
            "EUR": "€",
            "GBP": "£"
        }.get(destino, "")

        col = [col1, col2, col3][i]
        col.metric(
            f"{destino}",
            f"{simbolo} {valor_convertido:,.2f}",
            f"1 {moeda_origem} = {cotacao:.4f} {destino}"
        )

except Exception as e:
    st.warning(f"Erro ao buscar cotações: {e}")

# --------------------------
# GRÁFICOS DE VALORIZAÇÃO - UMA PARA CADA MOEDA FRENTE AO USD
# --------------------------
st.markdown("###  Histórico de Valorização das Moedas (Últimos 7 dias em relação ao Dólar USD)")

for nome, codigo in moedas.items():
    if codigo != "USD":  # Não faz sentido gráfico de USD → USD
        st.markdown(f"#### {nome}")

        par = f"{codigo}-USD"

        try:
            history_url = f"https://economia.awesomeapi.com.br/json/daily/{par}/7"
            hist_response = requests.get(history_url)
            hist_data = hist_response.json()

            datas = []
            valores = []

            for item in reversed(hist_data):
                data_pt = pd.to_datetime(item['timestamp'], unit='s').strftime('%d/%m')
                datas.append(data_pt)
                valores.append(float(item['bid']))

            df = pd.DataFrame({
                "Data": datas,
                "Cotação": valores
            })

            fig = px.line(
                df,
                x="Data",
                y="Cotação",
                markers=True,
                title=f"Valorização de {codigo} frente ao USD",
                labels={"Cotação": f"Valor de 1 {codigo} em USD", "Data": "Data"},
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.warning(f"Erro ao carregar o gráfico para {codigo} → USD: {e}")
