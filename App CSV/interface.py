#interface - feita por Eryk #
import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime

# função pra limpar o arquivo #
def limpar(lista):
    for i in range(len(lista)):
        lista[i] = lista[i].strip('"')

def values(coluna):
    global registros
    global colunas
    memoria = []
    indice = colunas.index(coluna)
    for registro in registros:
        informacao = registro
        limpar(informacao)
        if informacao[indice] not in memoria:
            memoria.append(informacao[indice])
    return memoria

# funções pra cada opção #
def listar_candidatos():
    municipio_codigo = entry_municipio.get()
    cargo_codigo = entry_cargo.get()
    # lógica pra listar candidatos por município e cargo #
    candidatos = [registro for registro in registros if registro[colunas.index('SG_UE')] == municipio_codigo and registro[colunas.index('CD_CARGO')] == cargo_codigo]
    if candidatos:
        resultado = "\n".join([f"{candidato[colunas.index('NM_CANDIDATO')]} ({candidato[colunas.index('NR_CANDIDATO')]}) - {candidato[colunas.index('SG_PARTIDO')]}" for candidato in candidatos])
    else:
        resultado = "Nenhum candidato encontrado para o município e cargo informados."
    resultado_label.config(text=resultado)

def exibir_informacoes():
    candidato_codigo = entry_candidato.get()
    # lógica pra exibir informações do candidato pelo código - Felipe #
    candidato = next((registro for registro in registros if registro[colunas.index('SQ_CANDIDATO')] == candidato_codigo), None)
    if candidato:
        resultado = f"Nome: {candidato[colunas.index('NM_CANDIDATO')]}\nNome na urna: {candidato[colunas.index('NM_URNA_CANDIDATO')]}\nNúmero: {candidato[colunas.index('NR_CANDIDATO')]}\nPartido: {candidato[colunas.index('SG_PARTIDO')]}"
    else:
        resultado = "Candidato não encontrado."
    resultado_label.config(text=resultado)

def calcular_idade(data_nascimento):
    hoje = datetime.today()
    nascimento = datetime.strptime(data_nascimento, '%d/%m/%Y')
    idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    return idade

def gerar_estatisticas_html():
    municipio_codigo = entry_municipio.get()
    candidatos = [registro for registro in registros if registro[colunas.index('SG_UE')] == municipio_codigo]
    
    if candidatos:
        # qtd de candidatos por cargo #
        cargos = {}
        for candidato in candidatos:
            cargo = candidato[colunas.index('CD_CARGO')]
            if cargo not in cargos:
                cargos[cargo] = 0
            cargos[cargo] += 1
        
        # partidos com candidatos ao cargo de prefeito #
        partidos_prefeito = set()
        for candidato in candidatos:
            if candidato[colunas.index('CD_CARGO')] == '11':  # código do cargo de prefeito #(clodoaldo nao apague)
                partidos_prefeito.add(candidato[colunas.index('SG_PARTIDO')])
        
        # qtd de candidatos por faixa etária #
        faixas_etarias = {'Até 21 anos': 0, 'Entre 22 anos e 40 anos': 0, 'Entre 41 anos e 60 anos': 0, 'Acima de 60 anos': 0}
        for candidato in candidatos:
            idade = calcular_idade(candidato[colunas.index('DT_NASCIMENTO')])
            if idade <= 21:
                faixas_etarias['Até 21 anos'] += 1
            elif 22 <= idade <= 40:
                faixas_etarias['Entre 22 anos e 40 anos'] += 1
            elif 41 <= idade <= 60:
                faixas_etarias['Entre 41 anos e 60 anos'] += 1
            else:
                faixas_etarias['Acima de 60 anos'] += 1
        
        # % de candidatos por cargo, considerando o grau de instrução, gênero e estado civil #
        estatisticas = {}
        for candidato in candidatos:
            cargo = candidato[colunas.index('CD_CARGO')]
            if cargo not in estatisticas:
                estatisticas[cargo] = {'Grau de instrução': {}, 'Gênero': {}, 'Estado civil': {}}
            
            grau_instrucao = candidato[colunas.index('DS_GRAU_INSTRUCAO')]
            genero = candidato[colunas.index('DS_GENERO')]
            estado_civil = candidato[colunas.index('DS_ESTADO_CIVIL')]
            
            if grau_instrucao not in estatisticas[cargo]['Grau de instrução']:
                estatisticas[cargo]['Grau de instrução'][grau_instrucao] = 0
            estatisticas[cargo]['Grau de instrução'][grau_instrucao] += 1
            
            if genero not in estatisticas[cargo]['Gênero']:
                estatisticas[cargo]['Gênero'][genero] = 0
            estatisticas[cargo]['Gênero'][genero] += 1
            
            if estado_civil not in estatisticas[cargo]['Estado civil']:
                estatisticas[cargo]['Estado civil'][estado_civil] = 0
            estatisticas[cargo]['Estado civil'][estado_civil] += 1
        
        #html - Heloisa #
        html_content = "<html><head><title>Estatísticas dos candidatos</title></head><body>"
        html_content += f"<h1>- Estatísticas dos candidatos do município {municipio_codigo} -</h1>"
        
        html_content += "<h2>Quantidade de candidatos por cargo:</h2><ul>"
        for cargo, quantidade in cargos.items():
            html_content += f"<li>{cargo}: {quantidade}</li>"
        html_content += "</ul>"
        
        html_content += "<h2>Partidos com candidatos ao cargo de prefeito:</h2><ul>"
        for partido in partidos_prefeito:
            html_content += f"<li>{partido}</li>"
        html_content += "</ul>"
        
        html_content += "<h2>Quantidade de candidatos por faixa etária:</h2><ul>"
        for faixa, quantidade in faixas_etarias.items():
            html_content += f"<li>{faixa}: {quantidade}</li>"
        html_content += "</ul>"
        
        html_content += "<h2>Percentual de candidatos por cargo:</h2>"
        for cargo, dados in estatisticas.items():
            html_content += f"<h3>{cargo}</h3>"
            for categoria, valores in dados.items():
                html_content += f"<h4>{categoria}</h4><ul>"
                total = sum(valores.values())
                for valor, quantidade in valores.items():
                    percentual = (quantidade / total) * 100
                    html_content += f"<li>{valor}: {percentual:.2f}%</li>"
                html_content += "</ul>"
        
        html_content += "</body></html>"
        
        with open("estatisticas_candidatos.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        resultado_label.config(text="Página HTML com estatísticas gerada com sucesso!")
    else:
        resultado_label.config(text="Nenhum candidato encontrado para o município informado.")

# programa principal - Feito por Clodoaldo #
with open('consulta_cand_2024_PB.csv', 'r') as arq:
    reader = csv.reader(arq, delimiter=';')
    planilha = list(reader)

# titulo das colunas #
colunas = planilha[0]

# registros da planilha #
registros = planilha[1:]

# configuração da janela principal #
root = tk.Tk()
root.title("Sistema de candidatos")

# listar candidatos pelo município e cargo #
frame_listar = ttk.LabelFrame(root, text="Listar candidatos")
frame_listar.pack(padx=10, pady=10, fill="x")

label_municipio = ttk.Label(frame_listar, text="Informe o código do município:")
label_municipio.pack(pady=5)
entry_municipio = ttk.Entry(frame_listar)
entry_municipio.pack(pady=5)

label_cargo = ttk.Label(frame_listar, text="Informe o código do cargo:")
label_cargo.pack(pady=5)
entry_cargo = ttk.Entry(frame_listar)
entry_cargo.pack(pady=5)

btn_listar = ttk.Button(frame_listar, text="Listar candidatos", command=listar_candidatos)
btn_listar.pack(pady=5)

# mstrar informações do candidato #
frame_exibir = ttk.LabelFrame(root, text="Exibir informações do candidato")
frame_exibir.pack(padx=10, pady=10, fill="x")

label_candidato = ttk.Label(frame_exibir, text="Informe o código do candidato:")
label_candidato.pack(pady=5)
entry_candidato = ttk.Entry(frame_exibir)
entry_candidato.pack(pady=5)

btn_exibir = ttk.Button(frame_exibir, text="Exibir informações", command=exibir_informacoes)
btn_exibir.pack(pady=5)

# gerar o HTML com as estatísticas #
frame_html = ttk.LabelFrame(root, text="Gerar HTML com estatísticas")
frame_html.pack(padx=10, pady=10, fill="x")

btn_html = ttk.Button(frame_html, text="Gerar HTML", command=gerar_estatisticas_html)
btn_html.pack(pady=5)

# mostrar os resultados #
resultado_label = ttk.Label(root, text="")
resultado_label.pack(pady=10)

# execução da interface #
root.mainloop()
