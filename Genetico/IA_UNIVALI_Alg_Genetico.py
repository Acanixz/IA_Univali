# Trabalho IA
# Algoritmo Genético
# Alunos: Hérick Vitor Vieira Bittencourt e Luiz Augusto Inthurn
# Ciência da Computação UNIVALI

import os
import pandas as pd
import numpy as np
import random
import re

# Carrega dados de preços
# Suporta formato longo com colunas ['Data', 'Código', 'Fechamento']
# ou formato largo (datas × códigos)
def carregar_dados(caminho):
    df = pd.read_excel(caminho)
    # Coluna de data
    data_col = next((c for c in df.columns if c.lower() in ['data', 'date']), df.columns[0])
    df[data_col] = pd.to_datetime(df[data_col])
    # Colunas de código e fechamento
    cod_col = next((c for c in df.columns if c.lower() in ['código', 'codigo']), None)
    fech_col = next((c for c in df.columns if c.lower() in ['fechamento', 'price', 'preço', 'preco']), None)

    if cod_col and fech_col:
        # Formato longo
        longo = df[[data_col, cod_col, fech_col]].dropna()
        longo.columns = ['Data', 'Código', 'Fechamento']
        # Filtra códigos com 5 caracteres alfanuméricos
        longo = longo[longo['Código'].astype(str).str.match(r'^[A-Za-z0-9]{5}$')].copy()
        longo['Fechamento'] = pd.to_numeric(longo['Fechamento'], errors='coerce')
        longo.dropna(subset=['Fechamento'], inplace=True)
        longo.set_index('Data', inplace=True)
        precos = longo.pivot_table(values='Fechamento', index=longo.index, columns='Código')
    else:
        # Formato largo
        df.set_index(data_col, inplace=True)
        df.index = pd.to_datetime(df.index)
        valid_cols = [col for col in df.columns if isinstance(col, str) and re.match(r'^[A-Za-z0-9]{5}$', col)]
        precos = df[valid_cols].apply(pd.to_numeric, errors='coerce')

    # Remove ativos com dados faltantes ou não positivos
    precos = precos.dropna(axis=1)
    precos = precos.loc[:, (precos > 0).all()]
    if precos.shape[0] < 2 or precos.shape[1] == 0:
        raise ValueError("Dados insuficientes: é preciso ao menos 2 datas e 1 ativo válido.")
    return precos

# Função fitness: simula operações dia a dia
def avaliar_individuo(dna, precos, capital_inicial=1000.0, n_potes=10):
    n_dias = precos.shape[0] - 1
    capital = capital_inicial
    # dna: vetor de tamanho n_dias * n_potes com índices de ativos
    dna = dna.reshape((n_dias, n_potes))
    historico = []  # guarda alocação e capital por ciclo
    for dia in range(n_dias):
        precos_dia = precos.iloc[dia].values
        precos_prox = precos.iloc[dia+1].values
        parte = capital / n_potes
        total_venda = 0.0
        aloc_dia = []
        
        # Simulação do indivíduo p/ o dia com o pote escolhido
        for pote in range(n_potes):
            idx = dna[dia, pote] # Ação escolhida
            cod = precos.columns[idx]
            fechamento_compra = precos_dia[idx]
            fechamento_venda = precos_prox[idx]
            ações = parte / fechamento_compra # Porção do pote / Valor de fechamento = Qtd. ações
            valor_venda = ações * fechamento_venda # Capital após venda das ações
            total_venda += valor_venda
            aloc_dia.append((pote+1, cod, fechamento_compra, fechamento_venda, valor_venda))
        capital = total_venda
        historico.append({'dia': precos.index[dia], 'capital': capital, 'alocação': aloc_dia})
    return capital, historico

# Componentes do AG

def inicializar_população(tam_pop, tam_dna, n_ativos):
    return [np.random.randint(0, n_ativos, tam_dna) for _ in range(tam_pop)]

def seleção_torneio(pop, fits, k=3):
    nova_pop = []
    # Qtd torneios: tam. população
    # 1 - Escolhe aleatóriamente os aspirantes
    # 2 - O vencedor com o maior fitness entra na nova pop.

    # Vencedores podem repetir caso ganhem mais torneios
    for _ in range(len(pop)):
        aspirantes = random.sample(range(len(pop)), k)
        vencedor = max(aspirantes, key=lambda i: fits[i])
        nova_pop.append(pop[vencedor].copy())
    return nova_pop

def cruzamento(p1, p2, p_cx=0.8):
    # Com 80% de chance, realiza cruzamento entre p1 e p2; senão, apenas copia os pais
    if random.random() > p_cx:
        return p1.copy(), p2.copy()
    a, b = sorted(random.sample(range(len(p1)), 2))
    f1 = np.concatenate([p1[:a], p2[a:b], p1[b:]])
    f2 = np.concatenate([p2[:a], p1[a:b], p2[b:]])
    return f1, f2

def mutação(dna, p_mut, n_ativos):
    for i in range(len(dna)):
        if random.random() < p_mut:
            # Escolhe um novo ativo aleatório caso mutação ocorra
            dna[i] = random.randrange(n_ativos)
    return dna

# Loop principal do AG
def algoritmo_genético(precos, tam_pop=50, gerações=100, p_cx=0.8, p_mut=0.01,
                        capital_inicial=1000.0, n_potes=10):
    n_dias = precos.shape[0] - 1
    n_ativos = precos.shape[1]
    # DNA = Numero de dias no Excel * nº Potes
    tam_dna = n_dias * n_potes
    pop = inicializar_população(tam_pop, tam_dna, n_ativos)
    melhor_fit = -np.inf
    melhor_dna = None
    melhor_historico = None

    for g in range(1, gerações+1):
        fits = []
        # Para cada indivíduo por geração, o melhor indivíduo é definido e entra na lista de seleção
        for indiv in pop:
            val, hist = avaliar_individuo(indiv, precos, capital_inicial, n_potes)
            fits.append(val)
            if val > melhor_fit:
                melhor_fit = val
                melhor_dna = indiv.copy()
                melhor_historico = hist
        print(f"Geração {g}: Melhor capital = R$ {melhor_fit:.2f}")

        # Seleção
        sel = seleção_torneio(pop, fits)

        # Reprodução
        nova_pop = []
        for i in range(0, tam_pop, 2):
            # Cruza individuos e gera uma nova mutação (1% chance)
            p1, p2 = sel[i], sel[min(i+1, tam_pop-1)]
            f1, f2 = cruzamento(p1, p2, p_cx)
            nova_pop.append(mutação(f1, p_mut, n_ativos))
            if len(nova_pop) < tam_pop:
                # Segundo individuo é adicionado após mutação caso ainda haja espaço
                nova_pop.append(mutação(f2, p_mut, n_ativos))
        pop = nova_pop

    return melhor_fit, melhor_historico

if __name__ == "__main__":
    print("Carregando arquivo, por favor aguarde..")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    caminho = "cotacoes_b3_202_05.xlsx"
    precos = carregar_dados(caminho)
    print("Preview dos preços:")
    print(precos.head())

    valor_final, historico = algoritmo_genético(precos, tam_pop=1000, gerações=100)
    print(f"\nCapital final: R$ {valor_final:.2f}\n")
    # Exibe histórico de cada ciclo
    for ciclo in historico:
        print(f"Dia: {ciclo['dia'].date()} | Capital: R$ {ciclo['capital']:.2f} | Capital por pote: R${(ciclo['capital']/10):.2f}")
        for pote, codigo, compra, venda, valor in ciclo['alocação']:
            print(f"  Pote {pote}: {codigo} | Compra: {compra:.2f} | Venda: {venda:.2f} | Valor final: R$ {valor:.2f} | Diferença: R$ {valor - (ciclo['capital']/10):.2f}")
        print()
