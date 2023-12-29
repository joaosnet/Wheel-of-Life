# Importando as bibliotecas necessárias
import plotly.graph_objects as go
import pandas as pd
from dash import html, dcc, Input, Output, State
from plotly.subplots import make_subplots
import datetime
import numpy as np
from dashapp import app, server, database, bcrypt
from dashapp.models import Usuario
from flask_login import login_user, logout_user, current_user

# %%
# fazendo um dicionario com os pilares e as perguntas
pilares = {"Profissional": "Qual é o seu nível de satisfação com sua vida profissional atualmente?",
        "Financeiro": "Qual é o seu nível de satisfação com sua situação financeira atualmente?",
        "Intelectual": "Qual é o seu nível de satisfação com seu crescimento intelectual e aprendizado contínuo?",
        "Servir": "Qual é o seu nível de satisfação com a contribuição que você faz para servir os outros e tornar o mundo um lugar melhor?",
        "Saude": "Qual é o seu nível de satisfação com sua saúde física e bem-estar?",
        "Social": "Qual é o seu nível de satisfação com suas relações sociais e vida social?",
        "Parentes": "Qual é o seu nível de satisfação com seus relacionamentos familiares e com seus parentes?",
        "Espiritual": "Qual é o seu nível de satisfação com sua conexão espiritual e sentido de propósito?",
        "Emocional": "Qual é o seu nível de satisfação com sua saúde emocional e capacidade de lidar com as adversidades da vida?"}

# criando uma lista com os pilares
lista_pilares = ["Profissional", "Financeiro", "Intelectual", "Servir", "Saude", "Social", "Parentes", "Espiritual", "Emocional"]

# criando uma lista com as respostas
lista_respostas = []

# %%

mes_atual = datetime.datetime.now().month   # mes atual
meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembo", "Dezembro"]
mes_referencia = str(meses[mes_atual-1])   # mes de referencia

# %% [markdown]
# ### Armazenar as informações em um arquivo em excel que servira como base de dados

# %%
# create a new dataframe with the answers
df0 = pd.DataFrame(lista_respostas, index=lista_pilares, columns=[f'{mes_referencia}'])

# display the dataframe
# display(df0)

# %%
# adicionando df0 ao df
# lendo os dados
df = pd.read_csv('instance/dados.csv', sep=';', index_col=0, encoding='utf-8')


#verificando se ja existe a coluna do mes atual
if mes_referencia not in df.columns:
    # modifique apenas os valores da coluna
    df[mes_referencia] = df0
    df.to_csv('instance/dados.csv', sep=';', encoding='utf-8')
# else:
#     # adicionando os dados do mes atual ao df
#     df = df.join(df0)

# display(df)

# %% [markdown]
# ### Importando os dados para Roda do Autocuidado 

# %%
# Agora faremos um dataframe separado para Roda do Autocuidado que tem os seguintes pilares 'Saúde', 'Psicológico', 'Emocional', 'Pessoal', 'Profissional', 'Espiritual', para isso pegarei algumas informacoes que ja existem no df para o df1
df1 = pd.read_csv('instance/dados2.csv', sep=';', index_col=0, encoding='utf-8')
# adicionando as colunas que faltam para isso faremos perguntas sobre esses pilares Psicologico e Pessoal
pilares_auto = {"Psicologico": "Em uma escala de 0 a 10, qual é o seu nível de satisfação com sua saúde psicológica e bem-estar?",
                "Pessoal": "Em uma escala de 0 a 10, qual é o seu nível de satisfação com sua saúde pessoal e autocuidado?"}
lista_respostas_auto = []
qtde_linhas = len(pilares_auto)
#adicionando as linhas que faltam
if mes_referencia not in df1.columns:
    df1[mes_referencia] = df[mes_referencia]
    df1.to_csv('instance/dados2.csv', sep=';', encoding='utf-8')

# Crie uma função que atualize o DataFrame com novos valores
def atualizar_dataframe(categoria, novo_valor):
    # importando as variaveis globais
    global df
    
    # atualizando o dataframes
    df.loc[df.index == categoria, mes_referencia] = novo_valor
    
    # salvando as modificacoes no arquivo csv
    df.to_csv('instance/dados.csv', sep=';', encoding='utf-8')
    

def atualizar_dataframe2(categoria, novo_valor):
    global df1

    df1.loc[df1.index == categoria, mes_referencia] = novo_valor

    df1.to_csv('instance/dados2.csv', sep=';', encoding='utf-8')

# %% [markdown]
# ### Mostrando os Graficos

# %%
fig = make_subplots(rows=1, cols=2, subplot_titles=("Roda da Vida", "Roda do Autocuidado"), specs=[[{'type': 'polar'}]*2])

# plotando cada grafico de radar que esta dentro do dataframe com um loop
for name in df:
    fig.add_trace(go.Scatterpolar(r = df[name], 
                                  theta = df.index, 
                                  fill = 'toself', 
                                  name = name,
                                  line_shape="spline"), row=1, col=1) # r = raio, theta = angulo, name = nome da legenda


# plotando cada grafico de radar que esta dentro do dataframe com um loop
for name in df1:
    fig.add_trace(go.Scatterpolar(r = df1[name], 
                                  theta = df1.index, 
                                  fill = 'toself', 
                                  name = name,
                                  line_shape="spline"), row=1, col=2) # r = raio, theta = angulo, name = nome da legenda, line_shape = tipo de linha, fill = preencher o grafico
# atualizando o layout do gráfico
fig.update_layout(height=700) 
fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10])), polar2=dict(radialaxis=dict(range=[0, 10])))

# criando função para atualizar o gráfico
def atualizar_grafico():
    # importando as variáveis globais
    global df
    global df1
    
    # atualizando o gráfico
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Roda da Vida", "Roda do Autocuidado"), specs=[[{'type': 'polar'}]*2])
    
    # plotando cada gráfico de radar que está dentro do dataframe com um loop
    for name in df:
        fig.add_trace(go.Scatterpolar(r=df[name], 
                                      theta=df.index, 
                                      fill='toself', 
                                      name=name,
                                      line_shape="spline"), row=1, col=1) # r = raio, theta = ângulo, name = nome da legenda
    
    # plotando cada gráfico de radar que está dentro do dataframe com um loop
    for name in df1:
        fig.add_trace(go.Scatterpolar(r=df1[name], 
                                      theta=df1.index, 
                                      fill='toself', 
                                      name=name,
                                      line_shape="spline"), row=1, col=2) # r = raio, theta = ângulo, name = nome da legenda, line_shape = tipo de linha, fill = preencher o gráfico    

    # atualizando o layout do gráfico
    fig.update_layout(height=500) 
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10])), polar2=dict(radialaxis=dict(range=[0, 10])))
    return fig

# Execute este aplicativo com `python app.py` e
# visite http://127.0.0.1:8050/ em seu navegador.

# layout_dashboard = html.Div([
#     html.H2(children='Ferramenta de AutoConhecimento'), # Título do aplicativo

#     html.Div(children='''
#         Uma ferramenta para te ajudar a se conhecer melhor e a ter uma vida mais equilibrada.
#     '''), # Descrição do aplicativo

#     dcc.Graph(
#         id='Roda da Vida e Autocuidado',
#         figure=fig
#     ), # Gráfico a ser exibido no aplicativo
#     html.Br(),
#     html.H2(children='Em uma escala de 1 a 10') # Título do aplicativo
# ]) # Estilo para o layout do aplicativo e o formato do texto

# Definindo a coluna esquerda
left_column = html.Div(
    id="left-column",
    className="four columns",
    children=[
        html.H5(children='Ferramenta de AutoConhecimento'), # Título do aplicativo
        html.Div(children='''Uma ferramenta para te ajudar a se conhecer melhor e a ter uma vida mais equilibrada.''')
        ] # Descrição do aplicativo    ]
)

# Layout do Dashboard Principal
layout_dashboard = html.Div(
    id="app-container",
    children=[
        # Coluna esquerda
        left_column,
        # Coluna direita
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                html.Div(
                    children=[
                        html.B("Roda da Vida e Autocuidado"),
                        html.Hr(),
                        dcc.Graph(id="Roda da Vida e Autocuidado", figure=fig),
                    ],
                ),
            ],
        ),
    ],
)

layout_homepage = html.Div([
    dcc.Location(id="homepage_url", refresh=True),
    html.H2("Criar conta"),
    html.Div([
        dcc.Input(id="email", type="email", placeholder="Seu e-mail"),
        dcc.Input(id="senha", type="password", placeholder="Sua senha"),
        html.Button("Criar conta", id="botao-criarconta"),
        dcc.Link("Já tem uma conta? Faça seu login aqui", "/login")
    ], className="form-column")
])

layout_login = html.Div([
    dcc.Location(id="login_url", refresh=True),
    html.H2("Faça seu Login"),
    html.Div([
        dcc.Input(id="email", type="email", placeholder="Seu e-mail"),
        dcc.Input(id="senha", type="password", placeholder="Sua senha"),
        html.Button("Faça Login", id="botao-login"),
        dcc.Link("Não tem uma conta? Crie aqui", "/")
    ], className="form-column")
])

layout_erro = html.Div([
    dcc.Location(id="erro_url", refresh=True),
    html.H2("Erro de Acesso"),
    html.Div([
        dcc.Link("Clique aqui para criar uma conta", "/"),
        dcc.Link("Clique aqui para fazer login", "/login")
    ], className="form-column")
])

# Definindo o layout do aplicativo
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    # Banner
    html.Div(id="banner", children=[
        html.Img(src=app.get_asset_url("logo.png")),
        # html.H1("Dashapp"),
        html.Div(id="navbar"),
    ], className="banner"),
    html.Div(id="conteudo_pagina")
])

# pathname
@app.callback(Output("conteudo_pagina", "children"), Input("url", "pathname"))
def carregar_pagina(pathname):
    if pathname == "/":
        return layout_homepage
    elif pathname == "/dashboard":
        if current_user.is_authenticated:
            return layout_dashboard
        else:
            return dcc.Link("Usuário não autenticado, faça login aqui", "/login")
    elif pathname == "/login":
        return layout_login
    elif pathname == "/erro":
        return layout_erro
    elif pathname == "/logout":
        if current_user.is_authenticated:
            logout_user()
        return layout_login
    
@app.callback(Output("navbar", "children"), Input("url", "pathname"))
def exibir_navbar(pathname):
    if pathname != "/logout":
        if current_user.is_authenticated:
            if pathname == "/dashboard":
                return html.Div([
                    dcc.Link("Logout", "/logout", className="button-link"),
                    dcc.Link("Nova Tela", "/nova_tela", className="button-link", refresh=True)
                ])
            else:
                return html.Div([
                    dcc.Link("Dashboard", "/dashboard", className="button-link"),
                    dcc.Link("Logout", "/logout", className="button-link"),
                    # dcc.Link("Nova Tela", "/nova_tela", className="button-link", refresh=True)
                ])
        else:
            return html.Div([
                dcc.Link("Login", "/login", className="button-link")
            ])
    
@app.callback(Output("homepage_url", "pathname"), Input("botao-criarconta", "n_clicks"), 
              [State("email", "value"), State("senha", "value")])
def criar_conta(n_clicks, email, senha):
    if n_clicks:
        # vou criar a conta
        # verificar se já existe um usuário com essa conta
        usuario = Usuario.query.filter_by(email=email).first() # finalizar
        if usuario:
            return "/login"
        else:
            # criar o usuário
            senha_criptografada = bcrypt.generate_password_hash(senha).decode("utf-8")
            usuario = Usuario(email=email, senha=senha_criptografada) # 123456
            database.session.add(usuario)
            database.session.commit()
            login_user(usuario)
            return "/dashboard"
        
@app.callback(Output("login_url", "pathname"), Input("botao-login", "n_clicks"), 
              [State("email", "value"), State("senha", "value")])
def criar_conta(n_clicks, email, senha):
    if n_clicks:
        # vou criar a conta
        # verificar se já existe um usuário com essa conta
        usuario = Usuario.query.filter_by(email=email).first() # finalizar
        if not usuario:
            return "/"
        else:
            # criar o usuário
            if bcrypt.check_password_hash(usuario.senha.encode("utf-8"), senha):
                login_user(usuario)
                return "/dashboard"
            else:
                return "/erro"
            

# colocando vários sliders para cada pilar da Roda da Vida
for pilar in lista_pilares:
    left_column.children.append(html.Div(children=[
        html.Br(),
        html.Label(pilares[pilar]), # Rótulo para o controle deslizante
        dcc.Slider(
            min=0,
            max=10,
            marks={i: f'Valor {i}' if i == 1 else str(i) for i in range(1, 11)}, # Marcas para o controle deslizante
            value=df.loc[pilar, mes_referencia], # Valor inicial do controle deslizante
            id=pilar
        ),
    ], style={'padding': 10, 'flex': 10, "text-align": "left"})) # Estilo para os componentes interativos

for pilar in pilares_auto.keys():
    left_column.children.append(html.Div(children=[
        html.Br(),
        html.Label(pilares_auto[pilar]), # Rótulo para o controle deslizante
        dcc.Slider(
            min=0,
            max=10,
            marks={i: f'Valor {i}' if i == 1 else str(i) for i in range(1, 11)}, # Marcas para o controle deslizante
            value=df1.loc[pilar, mes_referencia], # Valor inicial do controle deslizante
            id=pilar
        ),
    ], style={'padding': 10, 'flex': 10, "text-align": "left"})) # Estilo para os componentes interativos    



# fazendo funções para atualizar o gráfico e o dataframe
@app.callback(
    Output('Roda da Vida e Autocuidado', 'figure'),
    Input('Profissional', 'value'),
    Input('Financeiro', 'value'),
    Input('Intelectual', 'value'),
    Input('Servir', 'value'),
    Input('Saude', 'value'),
    Input('Social', 'value'),
    Input('Parentes', 'value'),
    Input('Espiritual', 'value'),
    Input('Emocional', 'value'),
    Input('Psicologico', 'value'),
    Input('Pessoal', 'value')
)
def update_figure(profissional, financeiro, intelectual, servir, saude, social, parentes, espiritual, emocional, psicolologico, pessoal):
    # atualizando o dataframe
    atualizar_dataframe('Profissional', profissional)
    atualizar_dataframe('Financeiro', financeiro)
    atualizar_dataframe('Intelectual', intelectual)
    atualizar_dataframe('Servir', servir)
    atualizar_dataframe('Saude', saude)
    atualizar_dataframe('Social', social)
    atualizar_dataframe('Parentes', parentes)
    atualizar_dataframe('Espiritual', espiritual)
    atualizar_dataframe('Emocional', emocional)
    atualizar_dataframe2('Psicologico', psicolologico)
    atualizar_dataframe2('Pessoal', pessoal)
    # atualizando o gráfico
    fig = atualizar_grafico()
    return fig

# df[mes_referencia] = df[mes_referencia].replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
# df.sort_values(by=[mes_referencia], inplace=True, ascending=True)
# # encontrando a linha com o menor valor e atribuindo a prioridade como alta
# # dizendo quais o pilares que tenho que melhorar
# pilares_melhorar = []
# for i in range(0, 3):
#     pilares_melhorar.append(df.index[i])
# # dizendo quais o pilares que estão bons
# pilares_bons = []
# for i in range(3, 6):
#     pilares_bons.append(df.index[i])
# # dizendo quais o pilares que estão ótimos
# pilares_otimos = []
# for i in range(6, 9):
#     pilares_otimos.append(df.index[i])
    
# print(f'Pilares que preciso melhorar: {pilares_melhorar}')
# print(f'Pilares que estão bons: {pilares_bons}')
# print(f'Pilares que estão ótimos: {pilares_otimos}')

@server.route("/nova_tela")
def nova_tela():
    return "Você está na página criada pelo Flask"
