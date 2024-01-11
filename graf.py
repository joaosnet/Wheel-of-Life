import datetime
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
class WheelOfLife:
    def __init__(self):
        self.pilares = {
            "Profissional": "Qual é o seu nível de satisfação com sua vida profissional atualmente?",
            "Financeiro": "Qual é o seu nível de satisfação com sua situação financeira atualmente?",
            "Intelectual": "Qual é o seu nível de satisfação com seu crescimento intelectual e aprendizado contínuo?",
            "Servir": "Qual é o seu nível de satisfação com a contribuição que você faz para servir os outros e tornar o mundo um lugar melhor?",
            "Saude": "Qual é o seu nível de satisfação com sua saúde física e bem-estar?",
            "Social": "Qual é o seu nível de satisfação com suas relações sociais e vida social?",
            "Parentes": "Qual é o seu nível de satisfação com seus relacionamentos familiares e com seus parentes?",
            "Espiritual": "Qual é o seu nível de satisfação com sua conexão espiritual e sentido de propósito?",
            "Emocional": "Qual é o seu nível de satisfação com sua saúde emocional e capacidade de lidar com as adversidades da vida?"
        }
        self.lista_pilares = ["Profissional", "Financeiro", "Intelectual", "Servir", "Saude", "Social", "Parentes", "Espiritual", "Emocional"]
        self.lista_respostas = []
        self.meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembo", "Dezembro"]
        self.mes_referencia = self.meses[datetime.datetime.now().month - 1]
        self.df = pd.read_csv('instance/dados.csv', sep=';', index_col=0, encoding='utf-8')
        self.df1 = pd.read_csv('instance/dados2.csv', sep=';', index_col=0, encoding='utf-8')

        # Verifica se o mês atual já está no dataframe, caso não esteja, cria uma nova coluna
        if self.mes_referencia not in self.df.columns:
            self.df[self.mes_referencia] = 0
            self.df.to_csv('instance/dados.csv', sep=';', encoding='utf-8')

        if self.mes_referencia not in self.df1.columns:
            self.df1[self.mes_referencia] = 0
            self.df1.to_csv('instance/dados2.csv', sep=';', encoding='utf-8')
        
    
    def atualizar_dataframe(self, categoria, novo_valor):
        self.df.loc[self.df.index == categoria, self.mes_referencia] = novo_valor
        self.df.to_csv('instance/dados.csv', sep=';', encoding='utf-8')
    
    def atualizar_dataframe2(self, categoria, novo_valor):
        self.df1.loc[self.df1.index == categoria, self.mes_referencia] = novo_valor
        self.df1.to_csv('instance/dados2.csv', sep=';', encoding='utf-8')
    
    def atualizar_grafico(self):
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Roda da Vida", "Roda do Autocuidado"), specs=[[{'type': 'polar'}]*2])
        for name in self.df:
            fig.add_trace(go.Scatterpolar(r=self.df[name], 
                                          theta=self.df.index, 
                                          fill='toself', 
                                          name=name,
                                          line_shape="spline"), row=1, col=1)
        
        for name in self.df1:
            fig.add_trace(go.Scatterpolar(r=self.df1[name], 
                                          theta=self.df1.index, 
                                          fill='toself', 
                                          name=name,
                                          line_shape="spline"), row=1, col=2)
            
        
        
        # colocando mais espaço entre os subplot_titles e os gráficos
        fig.update_layout(margin=dict(t=50, b=50, l=50, r=50)) 
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10])), polar2=dict(radialaxis=dict(range=[0, 10])))
        # Mostrando apenas traco do mês atual como foco inicial
        meses_sem_referencia = self.meses.copy()
        meses_sem_referencia.remove(self.mes_referencia)
        for mes in meses_sem_referencia:
            fig.update_traces(visible='legendonly', selector=dict(name=mes))
        return fig
    
    ## Para cada um dos valores iniciais, é criado um objeto para retornar
    def lista_de_pilares(self):
        return self.lista_pilares
    
    def lista_de_respostas(self):
        return self.lista_respostas
    
    def lista_de_meses(self):
        return self.meses
    
    def pilares(self):
        return self.pilares
    
    def mes_referencia(self):
        return self.mes_referencia
    
    def df(self):
        return self.df
    
    def df1(self):
        return self.df1
