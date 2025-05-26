# Projeto A3 – Otimização Logística

Este repositório contém o código-fonte e instruções para o **Projeto A3 – Otimização Logística**, desenvolvido por:

- Pedro Pimentel  
- Guilherme Sampaio  
- Eduardo Oliveira  
- Daniel Koshino  
- Arthur Santos Lima  
- Allan da Silva Gomes  

## Visão Geral

O objetivo deste projeto é simular um sistema de alocação de entregas em uma frota de caminhões, comparando diferentes implementações de cálculo de rotas (lista vs. heap e lista vs. matriz) e avaliando desempenho em termos de tempo e uso de memória.

## Pré-requisitos

- Python 3.8 ou superior  

## Estrutura do Repositório

```
├── main.py           # Contém TUDO: classes, geração, Dijkstra, roteamento, resumo e benchmark
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
   python main.py
   ```

Ao rodar, serão gerados em `Resultado/`:

- `resumo_<n_ent>x<n_cam>.txt` — detalhes das entregas alocadas  
- `nao_alocadas_<n_ent>x<n_cam>.txt` — entregas sem alocação  
- `resultados.txt` — tabela de tempos e memória por cenário e implementação  

## Parâmetros Configuráveis

- **Cenários:** no `main.py`, ajuste a lista `cenarios` para outros tamanhos de entregas e caminhões.  
- **Escalas:** no `main.py`, modifique `escalas` para testar mais ou menos fatores de escala.  
- **Velocidade média:** altere a constante de `50 km/h` dentro de `planejar_rotas` se desejar outra velocidade.  

## Autores

Desenvolvido por Pedro Pimentel, Guilherme Sampaio, Eduardo Oliveira, Daniel Koshino, Arthur Santos Lima e Allan da Silva Gomes.

---

Qualquer dúvida ou sugestão, abra uma issue ou envie um e-mail para pe.pimentel19@gmail.com.
