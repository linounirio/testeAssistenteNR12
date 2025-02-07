import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from loader import *
from langchain.prompts import ChatPromptTemplate

load_dotenv()
#st.session_state['api_key'] = 
MEMORIA=ConversationBufferMemory()
ARQUIVOS_VALIDOS =['pdf','xxx','xxx','xxx']
MODELO_IA={'OpenAI':
                {'modelos':['gpt-4o-mini','xxx'],
                 'chat':ChatOpenAI},
           'xxx':
                {'modelos':['xxx','xxx'],
                 'chat':'xxxx'}}

def carrega_arquivos(tipo_arquivo,arquivo):
    if tipo_arquivo == 'pdf':
        with tempfile.NamedTemporaryFile(suffix='.pdf',delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_pdf(nome_temp)
    return documento


def carrega_modelo(provedor, modelo,api_key, tipo_arquivo, arquivo):
    documento = carrega_arquivos(tipo_arquivo=tipo_arquivo, arquivo=arquivo)
    
    system_message='''Você é um assistente amigável chamado Orçamentista.
    Você possui acesso às seguintes informações vindas 
    de um documento {}: 

    ####
    {}
    ####

    Utilize as informações fornecidas para basear as suas respostas.

    Sempre que houver $ na sua saída, substita por S.

    Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
    sugira ao usuário carregar novamente o Oráculo!'''.format(tipo_arquivo, documento)
    template = ChatPromptTemplate.from_messages([
        ('system',system_message),
        ('placeholder','{chat_history}'),
        ('user', '{input}')
    ])
    
    chat = MODELO_IA[provedor]['chat'](model=modelo,api_key=api_key)
    chain = template | chat
    st.session_state['chain'] = chain

def pagina_chat():
    col1,col2=st.columns([0.2,0.8])
    col1.image('nr12.icon')
    col2.header('Bem-vindo ao assistente',divider=True)  
    
    chain = st.session_state.get('chain')
    if chain is None:
        st.error("Selecione o modelo")
        st.stop()

    memoria=st.session_state.get('memoria', MEMORIA)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)
    
    input_usuario = st.chat_input('Fale com deseja para o assistente')
    if input_usuario:
        #Humano
        chat = st.chat_message('human')
        chat.markdown(input_usuario)
        #Assistente
        chat = st.chat_message('ai')
        resposta = chat.write_stream(chain.stream(input_usuario))
        #inserindo na memória
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria
    
def sidebar():
    st.image('dapmanutencao.png')
    tabs = st.tabs(['Seleção de Modelos','Upload de Arquivos'])
    
    with tabs[1]:
        tipo_arquivo = st.selectbox('Selecione o tipo de arquivo',ARQUIVOS_VALIDOS)
        if tipo_arquivo == 'pdf':
            arquivo = st.file_uploader('faça o upload', type=['.pdf'])
        if tipo_arquivo =='xxx':
            st.error('escolha uma opção válida')
            st.stop()
    with tabs[0]:
        provedor = st.selectbox('Selecione o modelo',MODELO_IA.keys())
        modelo = st.selectbox('Selecione o modelo',MODELO_IA[provedor]['modelos'])
        #api_key = os.environ["OPENAI_API_KEY"]
        api_key = st.text_input('insira a chave da API')
        #if not api_key:
        #    st.error('Insira uma chave de API Válida para o modelo escolhido')
        #    st.stop()
 
    if st.button('Carrega Assistente',use_container_width=True):
        carrega_modelo(provedor=provedor, modelo=modelo, api_key=api_key, tipo_arquivo=tipo_arquivo, arquivo=arquivo)
    if st.button('Apagar histórico de conversa', use_container_width=True):
        st.session_state['memoria']=MEMORIA
    
def main():
    with st.sidebar:
        sidebar()
        
    pagina_chat()
    
if __name__=='__main__':
    main()