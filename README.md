# Projeto A3 – Otimização Logística usando Estrutura de Dados

Este repositório contém o código-fonte e instruções para o **Projeto A3 – Otimização Logística**, desenvolvido por:

- Allan da Silva Gomes  
- Arthur Santos Lima
- Eduardo Oliveira  
- Daniel Koshino  
- Guilherme Sampaio 
- Pedro Pimentel  

## Visão Geral

O objetivo deste projeto é simular um sistema de alocação de entregas em uma frota de caminhões, comparando diferentes implementações de cálculo de rotas (lista de adjacência vs. heap e lista de adjacência vs. matriz de adjacência) e avaliando desempenho em termos de tempo e uso de memória.

## Pré-requisitos

- Python 3.12.2 ou superior  

## Estrutura do Repositório

```
├── roteamento_entregas.py           # Contém TUDO: classes, geração, Dijkstra, roteamento, resumo e benchmark
├── README.md         # Este documento
└── Resultado/        # Arquivos gerados (resumos, resultados, não alocadas)
```

## Como Executar

1. Clone este repositório e entre na pasta:

   ```bash
   git clone https://github.com/PedroPimentelDev/A3-Estrutura-de-Dados-e-Analise-de-Algoritmos.git && \
     cd A3-Estrutura-de-Dados-e-Analise-de-Algoritmos
   ```

2. Execute o script principal:

   ```bash
   python roteamento_entregas.py
   ```

Ao rodar, serão gerados em `Resultado/`:

- `resumo_<n_ent>x<n_cam>.txt` — detalhes das entregas alocadas  
- `nao_alocadas_<n_ent>x<n_cam>.txt` — entregas sem alocação  
- `resultados.txt` — tabela de tempos e memória por cenário e implementação  

## Parâmetros Configuráveis

- **Cenários:** no `roteamento_entregas.py`, ajuste a lista `cenarios` para outros tamanhos de entregas e caminhões.  
- **Escalas:** no `roteamento_entregas.py`, modifique `escalas` para testar mais ou menos fatores de escala.  
- **Velocidade média:** altere a constante de `50 km/h` dentro de `planejar_rotas` se desejar outra velocidade.  

Qualquer dúvida ou sugestão, abra uma issue ou envie um e-mail para pe.pimentel19@gmail.com.
