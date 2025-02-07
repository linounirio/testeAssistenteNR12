from langchain_community.document_loaders import PyMuPDFLoader

def carrega_pdf(caminho):
    loader = PyMuPDFLoader(caminho)
    lista_doc = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_doc])
    return documento