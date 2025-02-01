# Importando as bibliotecas necessárias
from dash import html, dcc, Input, Output, State
from dashapp import app, server, database, bcrypt
from dashapp.models import Usuario
from flask_login import login_required, login_user, logout_user, current_user
from graf import WheelOfLife
from flask import render_template, url_for, redirect, request
from dashapp.forms import FormLogin, FormCriarConta
import os
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import joblib

# Cria uma instância da classe WheelOfLife
wheel = WheelOfLife()

# Atualiza o gráfico
fig = wheel.atualizar_grafico()

# Definindo a coluna esquerda
left_column = html.Div(
    id="left-column",
    className="four columns",
    children=[
        html.H5(children="Ferramenta de AutoConhecimento"),  # Título do aplicativo
        html.Div(
            children="""Uma ferramenta para te ajudar a se conhecer melhor e a ter uma vida mais equilibrada."""
        ),
    ],  # Descrição do aplicativo    ]
)

right_column = html.Div(
    id="right-column",
    className="eight columns",
    children=[
        html.Div(
            children=[
                html.Hr(),
                html.H5("Roda da Vida e Autocuidado"),
                html.Hr(),
                dcc.Graph(id="Roda da Vida e Autocuidado", figure=fig),
            ],
        ),
        html.Div(
            id="pilares-melhorar",
            children=[],
        ),
    ],
)

# Layout do Dashboard Principal
layout_dashboard = html.Div(
    id="app-container",
    children=[
        # Coluna esquerda
        left_column,
        # Coluna direita
        right_column,
    ],
)

# Definindo o layout do aplicativo
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    # Banner
    html.Div(
        id="banner",
        children=[
            html.Img(src=app.get_asset_url("fotos_site/logo.png")),
            # html.H1("Dashapp"),
            html.Div(id="navbar"),
        ],
        className="banner",
    ),
    html.Div(id="conteudo_pagina"),
])

layout_powerbi = html.Div([
    html.Iframe(
        src="https://app.powerbi.com/view?r=eyJrIjoiNzQ5NDViOWItMDk3NS00OGEzLTk5NjQtMmQ4OGFmODRkYjY3IiwidCI6Ijk4ZDM1NmYyLWQzMmEtNDc0Ni04ZmNkLTJhNzM5ZDZlMWE5NSJ9",
        width="100%",
        height="970",
    ),
])


# pathname
@app.callback(Output("conteudo_pagina", "children"), Input("url", "pathname"))
def carregar_pagina(pathname):
    if pathname == "/dash/":
        if current_user.is_authenticated:
            return layout_dashboard
        else:
            return dcc.Link(
                "Usuário não autenticado, faça login aqui", "/login", refresh=True
            )
    elif pathname == "/dash/powerbi/":
        return layout_powerbi


@app.callback(Output("navbar", "children"), Input("url", "pathname"))
def exibir_navbar(pathname):
    if pathname != "/logout":
        if current_user.is_authenticated:
            if pathname == "/dash/":
                return html.Div([
                    dcc.Link(
                        "Logout", "/logout", className="button-link", refresh=True
                    ),
                    dcc.Link("Home", "/", className="button-link", refresh=True),
                ])
            else:
                return html.Div([
                    dcc.Link("Dashboard", "/dash/", className="button-link"),
                    dcc.Link(
                        "Logout", "/logout", className="button-link", refresh=True
                    ),
                    # dcc.Link("Nova Tela", "/nova_tela", className="button-link", refresh=True)
                ])
        else:
            return html.Div([
                dcc.Link("Login", "/login", className="button-link", refresh=True)
            ])


@app.callback(
    Output("homepage_url", "pathname"),
    Input("botao-criarconta", "n_clicks"),
    [State("email", "value"), State("senha", "value")],
)
def criar_conta(n_clicks, email, senha):
    if n_clicks:
        # vou criar a conta
        # verificar se já existe um usuário com essa conta
        usuario = Usuario.query.filter_by(email=email).first()  # finalizar
        if usuario:
            return "/login"
        else:
            # criar o usuário
            senha_criptografada = bcrypt.generate_password_hash(senha).decode("utf-8")
            usuario = Usuario(email=email, senha=senha_criptografada)  # 123456
            database.session.add(usuario)
            database.session.commit()
            login_user(usuario)
            return "/dash/"


@app.callback(
    Output("login_url", "pathname"),
    Input("botao-login", "n_clicks"),
    [State("email", "value"), State("senha", "value")],
)
def criar_conta(n_clicks, email, senha):
    if n_clicks:
        # vou criar a conta
        # verificar se já existe um usuário com essa conta
        usuario = Usuario.query.filter_by(email=email).first()  # finalizar
        if not usuario:
            return "/dash//"
        else:
            # criar o usuário
            if bcrypt.check_password_hash(usuario.senha.encode("utf-8"), senha):
                login_user(usuario)
                return "/dash/"
            else:
                return "/erro"


lista_pilares = wheel.lista_de_pilares()
lista_respostas = wheel.lista_de_respostas()
meses = wheel.lista_de_meses()
pilares = wheel.pilares
mes_referencia = wheel.mes_referencia
df = wheel.df
df1 = wheel.df1

# adicionando as colunas que faltam para isso faremos perguntas sobre esses pilares Psicologico e Pessoal
pilares_auto = {
    "Psicologico": "Em uma escala de 0 a 10, qual é o seu nível de satisfação com sua saúde psicológica e bem-estar?",
    "Pessoal": "Em uma escala de 0 a 10, qual é o seu nível de satisfação com sua saúde pessoal e autocuidado?",
}

# colocando vários sliders para cada pilar da Roda da Vida
for pilar in lista_pilares:
    left_column.children.append(
        html.Div(
            children=[
                html.Br(),
                html.Label(pilares[pilar]),  # Rótulo para o controle deslizante
                dcc.Slider(
                    min=0,
                    max=10,
                    marks={
                        i: f"Valor {i}" if i == 1 else str(i) for i in range(1, 11)
                    },  # Marcas para o controle deslizante
                    value=df.loc[
                        pilar, mes_referencia
                    ],  # Valor inicial do controle deslizante
                    id=pilar,
                ),
            ]
        )
    )  # Estilo para os componentes interativos

for pilar in pilares_auto.keys():
    left_column.children.append(
        html.Div(
            children=[
                html.Br(),
                html.Label(pilares_auto[pilar]),  # Rótulo para o controle deslizante
                dcc.Slider(
                    min=0,
                    max=10,
                    marks={
                        i: f"Valor {i}" if i == 1 else str(i) for i in range(1, 11)
                    },  # Marcas para o controle deslizante
                    value=df1.loc[
                        pilar, mes_referencia
                    ],  # Valor inicial do controle deslizante
                    id=pilar,
                ),
            ]
        )
    )  # Estilo para os componentes interativos


# fazendo funções para atualizar o gráfico e o dataframe
@app.callback(
    Output("Roda da Vida e Autocuidado", "figure"),
    Input("Profissional", "value"),
    Input("Financeiro", "value"),
    Input("Intelectual", "value"),
    Input("Servir", "value"),
    Input("Saude", "value"),
    Input("Social", "value"),
    Input("Parentes", "value"),
    Input("Espiritual", "value"),
    Input("Emocional", "value"),
    Input("Psicologico", "value"),
    Input("Pessoal", "value"),
)
def update_figure(
    profissional,
    financeiro,
    intelectual,
    servir,
    saude,
    social,
    parentes,
    espiritual,
    emocional,
    psicolologico,
    pessoal,
):
    # Cria uma instância da classe WheelOfLife
    wheel = WheelOfLife()
    # atualizando o dataframe
    wheel.atualizar_dataframe("Profissional", profissional)
    wheel.atualizar_dataframe("Financeiro", financeiro)
    wheel.atualizar_dataframe("Intelectual", intelectual)
    wheel.atualizar_dataframe("Servir", servir)
    wheel.atualizar_dataframe("Saude", saude)
    wheel.atualizar_dataframe("Social", social)
    wheel.atualizar_dataframe("Parentes", parentes)
    wheel.atualizar_dataframe("Espiritual", espiritual)
    wheel.atualizar_dataframe("Emocional", emocional)
    wheel.atualizar_dataframe("Espiritual", espiritual)
    # atualizando o dataframe da roda do autocuidado
    wheel.atualizar_dataframe2("Profissional", profissional)
    wheel.atualizar_dataframe2("Saude", saude)
    wheel.atualizar_dataframe2("Emocional", emocional)
    wheel.atualizar_dataframe2("Psicologico", psicolologico)
    wheel.atualizar_dataframe2("Pessoal", pessoal)
    wheel.atualizar_dataframe2("Espiritual", espiritual)
    # atualizando o gráfico
    fig = wheel.atualizar_grafico()
    return fig


# Mostrando os pilares que preciso melhorar, os que estão bons e os que estão ótimos na coluna direita
@app.callback(
    Output("pilares-melhorar", "children"),
    Input("Profissional", "value"),
    Input("Financeiro", "value"),
    Input("Intelectual", "value"),
    Input("Servir", "value"),
    Input("Saude", "value"),
    Input("Social", "value"),
    Input("Parentes", "value"),
    Input("Espiritual", "value"),
    Input("Emocional", "value"),
    Input("Psicologico", "value"),
    Input("Pessoal", "value"),
)
def update_right_column(
    profissional,
    financeiro,
    intelectual,
    servir,
    saude,
    social,
    parentes,
    espiritual,
    emocional,
    psicolologico,
    pessoal,
):
    # Cria uma instância da classe WheelOfLife
    wheel = WheelOfLife()
    df = wheel.df
    df[mes_referencia] = (
        df[mes_referencia].replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
    )
    df.sort_values(by=[mes_referencia], inplace=True, ascending=True)
    # encontrando a linha com o menor valor e atribuindo a prioridade como alta
    # dizendo quais o pilares que tenho que melhorar
    pilares_melhorar = []
    for i in range(0, 3):
        pilares_melhorar.append(df.index[i])
    # dizendo quais o pilares que estão bons
    pilares_bons = []
    for i in range(3, 6):
        pilares_bons.append(df.index[i])
    # dizendo quais o pilares que estão ótimos
    pilares_otimos = []
    for i in range(6, 9):
        pilares_otimos.append(df.index[i])

    # print(f'Pilares que preciso melhorar: {pilares_melhorar}')
    # print(f'Pilares que estão bons: {pilares_bons}')
    # print(f'Pilares que estão ótimos: {pilares_otimos}')

    # adicionando os pilares que preciso melhorar na coluna direita do dashboard
    return html.Div(
        [
            html.Hr(),
            html.H5("Pilares que posso melhorar são:"),
            html.P(", ".join(pilar for pilar in pilares_melhorar)),
            html.H5(f"Pilares que estão bons são:"),
            html.P(", ".join(pilares_bons)),
            html.H5(f"Pilares que estão ótimos são:"),
            html.P(", ".join(pilares_otimos)),
        ],
        # className="four columns"
    )


@server.route("/")
def homepage():
    return render_template("index.html")


# @server.route("/1")
# def homepage1():
#     return render_template('homepage1.html')


@server.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(
            usuario.senha.encode("utf-8"), form_login.senha.data
        ):
            login_user(usuario, remember=True)
            return redirect("/dash/")  # Redireciona para o dashboard
    return render_template("homepage.html", form=form_login)


@server.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data).decode(
            "utf-8"
        )
        usuario = Usuario(
            username=form_criarconta.username.data,
            email=form_criarconta.email.data,
            senha=senha,
        )
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect("/dash/")  # Redireciona para o dashboard
    return render_template("criarconta.html", form=form_criarconta)


@server.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@server.route("/previsao", methods=["GET", "POST"])
def previsao():
    from pprint import pprint as pp

    dicionario = {}
    if request.method == "POST":
        # Obtém os dados do formulário
        data = request.form

        # verifica se todos os campos foram preenchidos
        # x_numericos = {'latitude': 0, 'longitude': 0, 'accommodates': 0, 'bathrooms': 0, 'bedrooms': 0, 'beds': 0, 'extra_people': 0,
        #        'minimum_nights': 0, 'ano': 0, 'mes': 0, 'n_amenities': 0, 'host_listings_count': 0}

        # x_tf = {'host_is_superhost': 0, 'instant_bookable': 0}

        # x_listas = {'property_type': ['Apartment', 'Bed and breakfast', 'Condominium', 'Guest suite', 'Guesthouse', 'Hostel', 'House', 'Loft', 'Outros', 'Serviced apartment'],
        #             'room_type': ['Entire home/apt', 'Hotel room', 'Private room', 'Shared room'],
        #             'cancellation_policy': ['flexible', 'moderate', 'strict', 'strict_14_with_grace_period']
        #             }
        # for item in x_listas:  # Para cada item nas listas de x_listas
        #     for valor in x_listas[item]:  # Para cada valor no item atual
        #         dicionario[f'{item}_{valor}'] = 0  # Adiciona uma chave-valor ao dicionário

        # for item in x_numericos:  # Para cada item nos valores numéricos
        #     if item == 'latitude' or item == 'longitude':  # Se o item for latitude ou longitude
        #         valor = st.number_input(f'{item}', step=0.00001, value=0.0, format="%.5f")  # Lê um número de entrada do usuário
        #     elif item == 'extra_people':  # Se o item for extra_people
        #         valor = st.number_input(f'{item}', step=0.01, value=0.0)  # Lê um número de entrada do usuário
        #     else:
        #         valor = st.number_input(f'{item}', step=1, value=0)  # Lê um número de entrada do usuário
        #     x_numericos[item] = valor  # Atualiza o valor no dicionário x_numericos

        # for item in x_tf:  # Para cada item nos valores booleanos
        #     valor = st.selectbox(f'{item}', ('Sim', 'Não'))  # Lê uma opção de seleção do usuário
        #     if valor == "Sim":  # Se o valor for "Sim"
        #         x_tf[item] = 1  # Atualiza o valor no dicionário x_tf para 1
        #     else:
        #         x_tf[item] = 0  # Atualiza o valor no dicionário x_tf para 0

        # for item in x_listas:  # Para cada item nas listas de x_listas
        #     valor = st.selectbox(f'{item}', x_listas[item])  # Lê uma opção de seleção do usuário
        #     dicionario[f'{item}_{valor}'] = 1  # Atualiza o valor no dicionário dicionario para 1

        # Atualiza o dicionário com os valores do formulário
        for key, value in data.items():
            try:
                dicionario[key] = float(value)
            except ValueError:
                dicionario[key] = value

        # Atualiza o dicionário com os valores do formulário
        # dicionario.update({key: float(value) for key, value in data.items()})

        # Cria um DataFrame a partir do dicionário
        valores_x = pd.DataFrame(dicionario, index=[0])

        # Carrega o modelo de aprendizado de máquina pré-treinado
        modelo = joblib.load(
            r"C:\Users\joaod\Documents\GitHub\Data-Science-Project\modelo.joblib"
        )

        # Faz a previsão do valor da propriedade com base nos valores de entrada fornecidos pelo usuário
        try:
            valor_predito = modelo.predict(valores_x)[
                0
            ]  # Faz a previsão do valor da propriedade
            return render_template(
                "previsao.html",
                valor_predito=f"O valor previsto da propriedade é R$ {valor_predito:.2f}",
            )  # Exibe o valor previsto com duas casas decimais
        except Exception as e:
            return render_template(
                "previsao.html",
                error=f"Ocorreu um erro ao prever o valor da propriedade: {e}",
            )  # Exibe uma mensagem de erro se ocorrer algum problema
    else:
        return render_template("previsao.html")
