"""
Projeto A3 – Otimização Logística
Autor: Pedro Pimentel, Guilherme Sampaio, Eduardo Oliveira, Daniel Koshino, Arthur Santos Lima, Allan da Silva Gomes
Data de entrega: 13/06/2025
"""

from collections import defaultdict
from functools import partial
from typing import Dict, List, Tuple, Callable
import os
import tempfile
import copy
import heapq
import random
import time
import tracemalloc
from multiprocessing import Pool, cpu_count

# ========================
#   SIMULAÇÃO DE ENTREGAS
# ========================

class Entrega:
    """
    Representa uma entrega com destino, peso e prazo.

    Atributos:
        destino (str): Nome da cidade de destino.
        peso (int): Peso da carga em quilogramas.
        prazo (int): Prazo máximo para entrega, em horas.
    """
    def __init__(self, destino, peso, prazo):
        self.destino = destino
        self.peso = peso
        self.prazo = prazo

class Caminhao:
    """
    Representa um caminhão disponível para alocação de entregas.

    Atributos:
        id (int): Identificador único do caminhão.
        capacidade (int): Capacidade restante em quilogramas.
        horas_disponiveis (float): Horas de operação disponíveis.
    """
    def __init__(self, id, capacidade, horas_disponiveis):
        self.id = id
        self.capacidade = capacidade
        self.horas_disponiveis = horas_disponiveis

# Lista de cidades de destino possíveis para as entregas
cidades_destino = [
    "Rio de Janeiro", "Porto Alegre", "Salvador", "Manaus", "Curitiba",
    "Natal", "Goiânia", "Fortaleza", "Belo Horizonte", "Vitória"
]

# Centro de distribuição de onde saem os caminhões
centros_distribuicao = ["Belém", "Recife", "Brasília", "São Paulo", "Florianópolis"]

# Dicionário com distâncias (em km) entre cada centro e destino
from_distancias = {
    (c, d): dist for (c, d), dist in {
        ("Belém", "Rio de Janeiro"): 3200, ("Belém", "Porto Alegre"): 4000,
        ("Belém", "Salvador"): 2100, ("Belém", "Manaus"): 2500,
        ("Belém", "Curitiba"): 3800, ("Belém", "Natal"): 1900,
        ("Belém", "Goiânia"): 2000, ("Belém", "Fortaleza"): 1600,
        ("Belém", "Belo Horizonte"): 3000, ("Belém", "Vitória"): 3100,
        ("Recife", "Rio de Janeiro"): 2300, ("Recife", "Porto Alegre"): 3600,
        ("Recife", "Salvador"): 800,  ("Recife", "Manaus"): 4300,
        ("Recife", "Curitiba"): 3400, ("Recife", "Natal"): 300,
        ("Recife", "Goiânia"): 2400, ("Recife", "Fortaleza"): 800,
        ("Recife", "Belo Horizonte"): 2400, ("Recife", "Vitória"): 2200,
        ("Brasília", "Rio de Janeiro"): 1150, ("Brasília", "Porto Alegre"): 2100,
        ("Brasília", "Salvador"): 1500, ("Brasília", "Manaus"): 3900,
        ("Brasília", "Curitiba"): 1400, ("Brasília", "Natal"): 2200,
        ("Brasília", "Goiânia"): 210,  ("Brasília", "Fortaleza"): 2200,
        ("Brasília", "Belo Horizonte"): 740,  ("Brasília", "Vitória"): 1300,
        ("São Paulo", "Rio de Janeiro"): 450,  ("São Paulo", "Porto Alegre"): 1100,
        ("São Paulo", "Salvador"): 2000, ("São Paulo", "Manaus"): 4300,
        ("São Paulo", "Curitiba"): 400,  ("São Paulo", "Natal"): 2900,
        ("São Paulo", "Goiânia"): 900,   ("São Paulo", "Fortaleza"): 3000,
        ("São Paulo", "Belo Horizonte"): 590,  ("São Paulo", "Vitória"): 880,
        ("Florianópolis", "Rio de Janeiro"): 1100, ("Florianópolis", "Porto Alegre"): 470,
        ("Florianópolis", "Salvador"): 2500,       ("Florianópolis", "Manaus"): 4600,
        ("Florianópolis", "Curitiba"): 650,        ("Florianópolis", "Natal"): 3200,
        ("Florianópolis", "Goiânia"): 1800,        ("Florianópolis", "Fortaleza"): 3500,
        ("Florianópolis", "Belo Horizonte"): 1500, ("Florianópolis", "Vitória"): 500
    }.items()
}

# ========================
#   Funções de Geração
# ========================

def gerar_entregas(n):
    """
    Gera uma lista de entregas aleatórias.

    Parâmetros:
        n (int): Quantidade de entregas a gerar.
    Retorna:
        List[Entrega]: Lista de objetos Entrega.
    """

    entregas = []
    for _ in range(n):
        destino = random.choice(cidades_destino)
        peso = random.randint(50, 500)
        prazo = random.randint(12, 72)
        entregas.append(Entrega(destino, peso, prazo))
    return entregas


def gerar_caminhoes(n):
    """
    Gera uma frota de caminhões aleatória.

    Parâmetros:
        n (int): Quantidade de caminhões a gerar.
    Retorna:
        List[Caminhao]: Lista de objetos Caminhao.
    """

    caminhoes = []
    for i in range(n):
        capacidade = random.randint(500, 1500)
        horas = random.randint(10, 50)
        caminhoes.append(Caminhao(i, capacidade, horas))
    return caminhoes


def gerar_lista_adjacencia():
    """
    Constrói um grafo de lista de adjacência a partir das distâncias.

    Retorna:
        Dict[str, List[Tuple[str, int]]]: Grafo mapeando centro -> [(destino, distancia)].
    """
    grafo = defaultdict(list)
    # Agora criamos arestas em ambos os sentidos para permitir rotas entre quaisquer nós
    for (c, d), distancia in from_distancias.items():
        # centro -> destino
        grafo[c].append((d, distancia))
        # destino -> centro
        grafo[d].append((c, distancia))
    return grafo


def gerar_matriz_adjacencia():
    """
    Constrói matriz de adjacência e índices de nós.

    Retorna:
        tuple: (matriz, idx, nodes) onde:
            matriz (List[List[float]]): Distâncias ou inf.
            idx (Dict[str, int]): Mapeamento nó -> índice.
            nodes (List[str]): Lista ordenada de nós (centros + destinos).
    """
    nodes = centros_distribuicao + cidades_destino
    idx = {node: i for i, node in enumerate(nodes)}
    size = len(nodes)
    matriz = [[float('inf')] * size for _ in range(size)]
    for c in centros_distribuicao:
        for d in cidades_destino:
            i, j = idx[c], idx[d]
            matriz[i][j] = from_distancias[(c, d)]
    return matriz, idx, nodes

# ========================
#   Algoritmo de Dijkstra
# ========================

def dijkstra_lista_heap(grafo, origem, destino):
    """
    Calcula menor distância usando heap e grafo de lista de adjacência.

    Parâmetros:
        grafo (dict): Grafo de lista de adjacência.
        origem (str): Nó de partida.
        destino (str): Nó de chegada.
    Retorna:
        float: Distância mínima ou inf se não alcançável.
    """
    heap = [(0, origem)]
    visitados = set()

    while heap:
        dist_atual, no = heapq.heappop(heap)
        if no == destino:
            return dist_atual
        if no in visitados:
            continue
        visitados.add(no)
        for vizinho, peso in grafo.get(no, []):
            if vizinho not in visitados:
                heapq.heappush(heap, (dist_atual + peso, vizinho))
    return float('inf')


def dijkstra_lista_simples(grafo, origem, destino):
    """
    Calcula menor distância usando lista simples (busca linear).

    Parâmetros:
        grafo (dict): Grafo de lista de adjacência.
        origem (str): Nó de partida.
        destino (str): Nó de chegada.
    Retorna:
        float: Distância mínima ou inf.
    """
    fila = [(0, origem)]
    visitados = set()

    while fila:
        dist_atual, no = min(fila, key=lambda x: x[0])
        fila.remove((dist_atual, no))
        if no == destino:
            return dist_atual
        if no in visitados:
            continue
        visitados.add(no)
        for vizinho, peso in grafo.get(no, []):
            if vizinho not in visitados:
                fila.append((dist_atual + peso, vizinho))
    return float('inf')


def dijkstra_matriz_heap(matriz, idx, nodes, origem, destino):
    """
    Calcula menor distância usando heap e matriz de adjacência.

    Parâmetros:
        matriz (list): Matriz de distâncias.
        idx (dict): Mapeamento nó -> índice.
        nodes (list): Lista de nós.
        origem (str): Nó de partida.
        destino (str): Nó de chegada.
    Retorna:
        float: Distância mínima ou inf.
    """
    heap = [(0, origem)]
    visitados = set()

    while heap:
        dist_atual, no = heapq.heappop(heap)
        if no == destino:
            return dist_atual
        if no in visitados:
            continue
        visitados.add(no)
        i = idx[no]
        for j, peso in enumerate(matriz[i]):
            if peso != float('inf'):
                vizinho = nodes[j]
                if vizinho not in visitados:
                    heapq.heappush(heap, (dist_atual + peso, vizinho))
    return float('inf')


def dijkstra_matriz_simples(matriz, idx, nodes, origem, destino):
    """
    Calcula menor distância usando lista simples e matriz de adjacência.

    Parâmetros:
        matriz (list): Matriz de distâncias.
        idx (dict): Mapeamento nó -> índice.
        nodes (list): Lista de nós.
        origem (str): Nó de partida.
        destino (str): Nó de chegada.
    Retorna:
        float: Distância mínima ou inf.
    """
    fila = [(0, origem)]
    visitados = set()

    while fila:
        dist_atual, no = min(fila, key=lambda x: x[0])
        fila.remove((dist_atual, no))
        if no == destino:
            return dist_atual
        if no in visitados:
            continue
        visitados.add(no)
        i = idx[no]
        for j, peso in enumerate(matriz[i]):
            if peso != float('inf'):
                vizinho = nodes[j]
                if vizinho not in visitados:
                    fila.append((dist_atual + peso, vizinho))
    return float('inf')

# ========================
#   Planejamento de Rotas
# ========================

def planejar_rotas(entregas, caminhoes, centros, buscar):
    """
    Aloca entregas a caminhões e centros baseando-se em menor distância.

    Parâmetros:
        entregas (list): Lista de objetos Entrega, ordenados por prazo.
        caminhoes (list): Lista de objetos Caminhao disponíveis.
        centros (list): Lista de nomes de centros de distribuição.
        buscar (callable): Função de busca de distância (origem->destino).
    Retorna:
        tuple: (rotas, nao_alocadas)
            rotas (dict): mapeia id do caminhão -> lista de (centro, destino, km).
            nao_alocadas (list): entregas que não caberam.
    """
    rotas = {c.id: [] for c in caminhoes}
    nao_alocadas = []

    # Ordena entregas pelo prazo (mais urgente primeiro)
    for entrega in sorted(entregas, key=lambda x: x.prazo):
        melhor = (None, None, float('inf'))  # (caminhao, centro, distancia)
        for centro in centros:
            distancia = buscar(centro, entrega.destino)
            if distancia == float('inf'):
                continue
            horas_viagem = distancia / 50  # considera velocidade fixa de 50 km/h

            # Testa todos os caminhões para achar o mais adequado
            for cam in caminhoes:
                if (cam.capacidade >= entrega.peso and
                    cam.horas_disponiveis >= horas_viagem and
                    horas_viagem <= entrega.prazo):
                    if distancia < melhor[2]:
                        melhor = (cam, centro, distancia)

        # Se encontrou combinação válida, aplica alocação
        cam_sel, centro_sel, dist_sel = melhor
        if cam_sel:
            cam_sel.capacidade -= entrega.peso
            cam_sel.horas_disponiveis -= dist_sel / 50
            rotas[cam_sel.id].append((centro_sel, entrega.destino, dist_sel))
        else:
            nao_alocadas.append(entrega)

    return rotas, nao_alocadas

# ========================
#   Funções de Escalabilidade
# ========================

def escalar_grafo(grafo, escala):
    """
    Gera uma cópia do grafo com distâncias escaladas.

    Parâmetros:
        grafo (dict): Grafo original.
        escala (float): Fator multiplicador de distâncias.
    Retorna:
        dict: Grafo escalado.
    """
    return {
        centro: [(dest, dist * escala) for dest, dist in adj]
        for centro, adj in grafo.items()
    }


def escalar_matriz(matriz, escala):
    """
    Gera uma cópia da matriz com distâncias escaladas.

    Parâmetros:
        matriz (list): Matriz original.
        escala (float): Fator de escala.
    Retorna:
        list: Matriz escalada.
    """
    return [
        [(d * escala if d != float('inf') else float('inf')) for d in row]
        for row in matriz
    ]


# ========================
#   Nova Função: Resumo em Arquivo
# ========================

def escrever_resumo_entregas(
    rotas: Dict[int, List[Tuple[str, str, float]]],
    buscar: Callable[[str, str], float],
    filename: str = "resumo_entregas.txt"
 ) -> None:
    
    """
    Gera um arquivo de texto com o resumo das entregas:
      - Linhas sem '*' são as primeiras entregas de cada caminhão (origem = centro de distribuição).
      - Linhas com '*' indicam entregas **subsequentes** do mesmo caminhão,
        ou seja, partem da cidade de destino da entrega anterior.

    Exemplo de linha sem '*':
      Entrega para BH a partir de SP (Caminhão 2): 590 km
    Exemplo de linha com '*':
      *Entrega para RJ a partir de BH (Caminhão 2): 450 km
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=== Resumo das Entregas ===\n")
        for cid, lst in rotas.items():
            last_orig: str = None
            for idx, (centro, destino, _) in enumerate(lst):
                if idx == 0:
                    origem = centro
                    star = ""
                else:
                    origem = last_orig
                    star = "*"
                dist = buscar(origem, destino)
                f.write(f"{star}Entrega para {destino} a partir de {origem} (Caminhão {cid}): {dist:.0f} km\n")
                last_orig = destino

# ========================
#   Benchmark de Desempenho
# ========================

def benchmark_distancias(escala, entregas, caminhoes, grafo0, mat0, idx, nodes):
    """
    Executa benchmarks comparando tempo e memória de quatro implementações.

    Parâmetros:
        escala (float): Fator de escala para distâncias.
        entregas (list): Lista de objetos Entrega.
        caminhoes (list): Frota de caminhões.
        grafo0 (dict): Grafo original.
        mat0 (list): Matriz original.
        idx (dict): Índices de nós.
        nodes (list): Lista de nós.
    Retorna:
        dict: mapeando nome da implementação -> métricas de tempo e memória.
    """
    # Aplica escala aos dados originais
    grafo = escalar_grafo(grafo0, escala)
    matriz = escalar_matriz(mat0, escala)

    funcs = {
        "Lista Simples (Adj)": lambda o, d: dijkstra_lista_simples(grafo, o, d),
        "Heap (Adj)"         : lambda o, d: dijkstra_lista_heap(grafo, o, d),
        "Lista Simples (Mat)": lambda o, d: dijkstra_matriz_simples(matriz, idx, nodes, o, d),
        "Heap (Mat)"         : lambda o, d: dijkstra_matriz_heap(matriz, idx, nodes, o, d),
    }

    resultados = {}
    for nome, func in funcs.items():
        start = time.perf_counter()
        tracemalloc.start()

        # executa roteamento completo
        _rotas, _nao = planejar_rotas(
            entregas,
            copy.deepcopy(caminhoes),
            centros_distribuicao,
            func
        )

        duracao = time.perf_counter() - start
        memoria, _ = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        resultados[nome] = {"tempo_s": duracao, "mem_KB": memoria / 1024}
    return resultados

def rodar_uma_escala(args):
    """
    Função helper para multiprocessing: 
    args = (escala, entregas, caminhoes, grafo0, mat0, idx, nodes)
    Retorna (escala, resultados_do_benchmark).
    """
    escala, entregas, caminhoes, grafo0, mat0, idx, nodes = args
    res = benchmark_distancias(escala, entregas, caminhoes, grafo0, mat0, idx, nodes)
    return escala, res

# ========================
#   Ponto de Entrada
# ========================
def main():

    # Busca do caminho do arquivo .py
    caminho_completo_do_script = os.path.abspath(__file__)
    script_dir = os.path.dirname(caminho_completo_do_script)
    caminho_saida = os.path.join(script_dir, "Resultado")

    # Tentativa de criar a pasta 'Resultado' no caminho definido na variavel caminho_saida
    try:
        os.makedirs(caminho_saida, exist_ok=True)
    except PermissionError:
        # Caso não tenha permissão para escrita, utilizaremos a pasta temporária do sistema
        temp = tempfile.gettempdir()
        caminho_saida = os.path.join(temp, "Resultado")
        os.makedirs(caminho_saida, exist_ok=True)

    # Cenarios baseados no número de entregas e caminhões
    cenarios = [(100, 20), (1000, 200), (10000, 2000)]
    
    # Fatores da escala para ser utilizadas no benchmark
    escalas = [0.5, 0.75, 1.0, 1.25, 1.5]

    print("Iniciando benchmark... Tempo estimado: 1 min 30 s")
    
    # Abre o arquivo de resultados de benchmark dentro da pasta
    resultados_path = os.path.join(caminho_saida, "resultados.txt")
    with open(resultados_path , "w", encoding="utf-8") as arquivo:
        arquivo.write("cenario\tescala\testrutura\ttempo_s\tmem_KB\n")

        for n_ent, n_cam in cenarios:
            print(f"Gerando cenário: {n_ent} entregas x {n_cam} caminhões")
            entregas = gerar_entregas(n_ent)
            caminhoes = gerar_caminhoes(n_cam)

            # Resumo de entregas
            grafo = gerar_lista_adjacencia()
            buscar = partial(dijkstra_lista_heap, grafo)
            rotas, nao_alocadas = planejar_rotas(entregas, caminhoes, centros_distribuicao, buscar)

            # escreve o resumo também dentro da pasta
            resumo_path = os.path.join(caminho_saida, f"resumo_{n_ent}x{n_cam}.txt")
            escrever_resumo_entregas(rotas, buscar, filename=resumo_path)

            # Grava as entregas não alocadas em um outro arquivo
            if nao_alocadas:
                nao_path = os.path.join(caminho_saida, f"nao_alocadas_{n_ent}x{n_cam}.txt")
                with open(nao_path, "w", encoding="utf-8") as f:
                    for e in nao_alocadas:
                        f.write(f"{e.destino}, peso={e.peso}, prazo={e.prazo}\n")

            # Prepara dados para o benchmark
            grafo0 = gerar_lista_adjacencia()
            mat0, idx, nodes = gerar_matriz_adjacencia()

            # Monta a lista de argumentos para cada escala
            tarefas = [
                (esc, entregas, caminhoes, grafo0, mat0, idx, nodes)
                for esc in escalas
            ]

            # Utilizacao do multiprocessing.Pool para executar rodar_uma_escala em paralelo nas tarefas (escalas e métricas)
            pool = Pool(processes=cpu_count())
            resultados_list = pool.map(rodar_uma_escala, tarefas)

            pool.close()
            pool.join()

            # Itera sobre cada resultado de escala e grava no arquivo de saída
            for escala, resultados in resultados_list:
                print(f"[Cenário {n_ent}x{n_cam}] Escala {escala:.2f} concluída")
                for estrutura, dados in resultados.items():
                    arquivo.write(
                        f"{n_ent}x{n_cam}\t"
                        f"{escala:.2f}\t"
                        f"{estrutura}\t"
                        f"{dados['tempo_s']:.6f}\t"
                        f"{dados['mem_KB']:.2f}\n"
                    )

    print(f"Benchmark finalizado. Confira '{resultados_path}'.")

if __name__ == "__main__":
    main()