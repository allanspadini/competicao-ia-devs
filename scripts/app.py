import streamlit as st
import pandas as pd
from langflow.load import run_flow_from_json
import json


# Cria a interface para o jogo
st.title("Jogo de Adivinhação de Palavras")
st.image("robo.png")

# Interface para o input do link
endereco = st.text_input("Insira o link de uma página com o tema do jogo que quer gerar:")

# Botão para gerar o jogo
if st.button("Gerar Jogo"):
    if endereco:
        # Executa o restante do código apenas se o link for fornecido e o botão for clicado
        
        TWEAKS = {
            "URL-AyNM0": {
                "urls": []
            },
            "ParseData-PCQiY": {
                "sep": "\n",
                "template": "{text}"
            },
            "Prompt-9CB7X": {
                "template": "Você é um criador de jogos de palavras. Sua tarefa é criar um jogo Double-Crostic baseado em um texto fornecido. Siga os passos abaixo:\n\nSeleção de Palavras: Leia o texto fornecido e selecione 20 palavras que sejam relevantes ao tema do texto. \n\n\n\n\nAqui está o texto: {texto}\n\n\n\nComo resultado escreva apenas a lista de palavras. Não escreva nada sobre a lista. Não precisa explicar o que é o resultado só a lista mesmo.\n\nResultado:",
                "texto": ""
            },
            "Prompt-vsAnn": {
                "template": "Você vai receber um texto e uma lista de palavras.\n\nCriação de Dicas: Para cada uma das 20 palavras selecionadas relacionadas ao tema do texto, crie uma dica clara e precisa que ajude o jogador a adivinhar a palavra.\n\nTexto:\n\n{texto}\n\nLista de palavras:\n\n{lista}\n\nComo resultado retorne a dica de cada palavra em uma linha na mesma sequência que as palavras apareceram. Escreva a palavra seguida da dica. Garanta que o delimitador entre a palavra e a dica seja um ponto e vírgula ;. Não escreva nenhuma outra explicação na resposta.\n\nResposta:",
                "texto": "",
                "lista": ""
            },
            "TextOutput-z3deA": {
                "input_value": ""
            },
            "OpenAIModel-jfGrd": {
                "api_key": "API_gpt_Allan",
                "input_value": "",
                "json_mode": False,
                "max_tokens": None,
                "model_kwargs": {},
                "model_name": "gpt-4o-mini",
                "openai_api_base": "",
                "output_schema": {},
                "seed": 1,
                "stream": False,
                "system_message": "",
                "temperature": 0.1
            },
            "OpenAIModel-fJosl": {
                "api_key": "API_gpt_Allan",
                "input_value": "",
                "json_mode": False,
                "max_tokens": None,
                "model_kwargs": {},
                "model_name": "gpt-4o-mini",
                "openai_api_base": "",
                "output_schema": {},
                "seed": 1,
                "stream": False,
                "system_message": "",
                "temperature": 0.1
            },
            "TextInput-15V3m": {
                "input_value": endereco
            }
        }


        result = run_flow_from_json(flow="Jogo de Palavras.json",
                                    input_value="message",
                                    fallback_to_env_vars=True,
                                    tweaks=TWEAKS)
        text_data = result[0].outputs[0].results['text']
        data_dict = json.loads(str(text_data))
        text_content = data_dict.get("text")
        # Processamento dos dados para garantir que o DataFrame é criado corretamente
        linhas = text_content.split('\n')
        dados = [linha.split('; ') for linha in linhas]

        # Verifica se o número de colunas é o esperado
        if len(dados) > 0 and len(dados[0]) == 2:
            df = pd.DataFrame(dados, columns=["Palavra", "Dica"])
        else:
            st.error("Erro ao processar os dados. Verifique o formato do texto.")

        # Inicializa uma lista para armazenar as palavras acertadas com o comprimento correto
        if 'acertos' not in st.session_state or len(st.session_state['acertos']) != len(df):
            st.session_state['acertos'] = [False] * len(df)

        # Inicializa um dicionário para armazenar as letras corretas já adivinhadas
        if 'letras_acertadas' not in st.session_state:
            st.session_state['letras_acertadas'] = {}

        # Variável para verificar se todas as palavras foram acertadas
        todas_acertadas = True

        for index, row in df.iterrows():
            # Remove espaços em branco extras da palavra
            palavra_corrigida = row['Palavra'].strip()

            # Exibe a dica
            st.write(f"Dica: {row['Dica']}")

            # Cria uma coluna para cada letra da palavra
            cols = st.columns(len(palavra_corrigida))

            # Armazena as letras digitadas pelo usuário
            user_input = []

            for i in range(len(palavra_corrigida)):
                with cols[i]:
                    # Se a palavra já foi acertada, mostrar a letra correta em verde
                    if st.session_state['acertos'][index]:
                        st.success(palavra_corrigida[i])
                        user_input.append(palavra_corrigida[i])
                    else:
                        # Preenche os inputs com letras corretas já adivinhadas se disponíveis
                        sugestao_letra = st.session_state['letras_acertadas'].get(palavra_corrigida[i], "")
                        letra = st.text_input("", value=sugestao_letra, key=f"{index}-{i}", max_chars=1)
                        user_input.append(letra)

            # Verifica se a palavra está correta
            if st.button('Enviar', key=f"button-{index}"):
                if "".join(user_input).lower() == palavra_corrigida.lower():
                    st.session_state['acertos'][index] = True
                    st.success("Você acertou!")
                    # Armazena as letras corretas para sugestões futuras
                    for letra in palavra_corrigida:
                        st.session_state['letras_acertadas'][letra] = letra
                else:
                    st.error("Tente novamente.")

            # Verifica se a palavra foi acertada
            if not st.session_state['acertos'][index]:
                todas_acertadas = False

            st.write("---")  # Divisória entre as palavras

        # Se todas as palavras foram acertadas, exibe balões
        if todas_acertadas:
            st.balloons()
        