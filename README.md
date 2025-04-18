# FIAP - Faculdade de Informática e Administração Paulista
Enterprise Challenge - Sprint 2 - Ingredion

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap (3).png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Nome do projeto
🌱 Sistema de Previsão de Produtividade Agrícola usando IA.

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/bryanjfagundes/">Bryan Fagundes</a>
- <a href="https://br.linkedin.com/in/brenner-fagundes">Brenner Fagundes</a>
- <a href="https://www.linkedin.com/in/diogo-botton-46ba49197/">Diogo Botton</a> 
- <a href="https://www.linkedin.com/in/hyankacoelho/">Hyanka Coelho</a> 
- <a href="https://www.linkedin.com/in/julianahungaro/">Juliana Hungaro Fidelis</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/leonardoorabona?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app">Leonardo Ruiz Orabona</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi</a>

## 📋 Visão Geral
Este projeto desenvolve um sistema de previsão de produtividade para culturas de milho na região de Sorriso-MT, utilizando dados de sensoriamento remoto, informações meteorológicas e técnicas de aprendizado de máquina.

## 📊 Dados Utilizados
- 🛰️ Imagens de satélite: Índices de vegetação (NDVI) do sistema SatVeg
- ☁️ Dados meteorológicos: Temperatura, precipitação e radiação do INMET
- 📈 Dados de produtividade: Série histórica de produtividade (CONAB)

## 🔍 Metodologia
O projeto segue três etapas principais:

- 1️⃣ Pré-processamento de Dados
  - 🧹 Limpeza e organização de dados temporais de NDVI
  - 🔄 Tratamento de dados meteorológicos
  - 📉 Análise exploratória para identificação de padrões sazonais

- 2️⃣ Processamento de Imagens
  - 🖼️ Segmentação de imagens utilizando diferentes técnicas:
    - 📏 Limiares de NDVI
    - 🧩 Algoritmo K-means
    - 💧 Watershed

- 📑 Extração de características relevantes para análise de produtividade

## 3️⃣ Modelagem (em desenvolvimento) CONTINUAR
🤖 Seleção de algoritmos de aprendizado de máquina
🏋️‍♂️ Treinamento com dados históricos
⚙️ Validação e ajuste de hiperparâmetros
📊 Avaliação de desempenho
🔬 Resultados Preliminares
📈 A análise de NDVI mostra clara sazonalidade alinhada com os ciclos de cultivo
🔗 Identificação de correlações entre índices meteorológicos e vigor da vegetação
🗺️ Segmentação eficiente das áreas de cultivo em diferentes níveis de desenvolvimento
🚀 Próximos Passos
✅ Finalizar implementação e treinamento do modelo preditivo
🧪 Validar resultados com dados de produtividade reais
🖥️ Desenvolver interface para visualização de previsões
🛠️ Dependências
🐍 Python 3.x
🐼 Pandas, NumPy
🧠 Scikit-learn, Scikit-image
📊 Matplotlib, Seaborn

**Sobre os entregáveis:**

O notebook *banana_detector.ipynb* contém os entregáveis para a Entrega 1.

O notebook *banana_classification.ipynb* contém os entregáveis para a Entrega 2, inclusive pelo fato de ser realizado Transfer Learning e Fine Tuning, talvez possa se enquadrar em uma das atividades do "Ir Além", onde o objetivo era realizar justamente estas duas técnicas. No caso, neste notebook há 3 tipos de implementações, dentre elas: CNN treinada do zero, CNN com Transfer Learning e CNN com Fine Tuning, este último utilizando como base o modelo pré-treinado (InceptionV3) anteriormente com o Transfer Learning.

## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>src</b>: Todo o código fonte criado com os dois notebooks, um chamado *banana_detector.ipynb* e outro *banana_classification.ipynb*.

## 🔧 Como executar o código

Para rodar o código basta fazer uma cópia do notebook para o Google Colab (é mais prático, porém também é possível rodar localmente, caso for necessário), assim como, fazer o download dos dois datasets necessários para realizar o treinamento. Informações sobre quais datasets foram utilizados para os treinamentos se encontram nos notebooks.

Após realizar o download do dataset, zipar a pasta e fazer o upload para o seu Google Drive pessoal. Porém, também é possível fazer uma cópia do dataset que já se encontra no Google Drive de um dos integrantes do grupo, segue links para download dos datasets:

##### Classificador de bananas:
- [Banana_Classification.zip](https://drive.google.com/file/d/1lAhs54E3FUOSJGk1S6ij8FGL8eszyu4u/view?usp=drive_link)

**Fonte:**
[Banana Ripeness Classification Computer Vision Project](https://universe.roboflow.com/roboflow-universe-projects/banana-ripeness-classification)

##### Detector de Bananas:
- [Banana_detector.yolov11.zip](https://drive.google.com/file/d/1gDLfpKXPQUq2CK0k9ljSHGIQPZhgA8mQ/view?usp=drive_link)

**Fonte:**
[Banana Ripening Process Computer Vision Project](https://universe.roboflow.com/fruit-ripening/banana-ripening-process)

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
