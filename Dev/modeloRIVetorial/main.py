import spacy
import sys
import math
import os

#Token é uma porção de texto que pode ser uma palavra, pontuação, numerais, sentenças, etc.
nlp = spacy.load("pt_core_news_lg")

def pasta_projeto(pasta, arquivo):

    diretorio_atual = os.getcwd()
    pasta_raiz = os.path.join(diretorio_atual, pasta)

    caminho_arquivo = os.path.join(pasta_raiz, arquivo)

    return caminho_arquivo
def criarVetorConsulta(consulta, baseTermoIdf):

    termo_consulta, _ = gerar_indice_invertido(consulta)
    #Retorna uma lista de tupla ex: [('w', ['1,1]), ('y', ['1,1'])]

    # Monta um dicionario de consulta apenas com os termos ex: {'y', 'w'}
    consulta = set()
    for termo, _ in termo_consulta:
        consulta.add(termo)

    #[0.12493873660829993, 0, 0.6020599913279624]
    vetorConsulta = []
    for termo, peso in baseTermoIdf:
        if termo in consulta:
            vetorConsulta.append(peso)
        else:
            vetorConsulta.append(0)
    return vetorConsulta
def criarVetorDocumento(TfIdf, baseTermoIdf):

    vetorDocTfIdf = []
    for termo, _ in baseTermoIdf:
        pesoTermo = 0
        for t, p in TfIdf:
            if t == termo:
                pesoTermo = p
                break

        vetorDocTfIdf.append(pesoTermo)
    return vetorDocTfIdf
def calcSimilaridade(vetorConsultaIdf, vetorDocTfIdf):
    produtoEscalar = 0
    potenciaVetor1 = 0
    potenciaVetor2 = 0

    for x, y in zip(vetorConsultaIdf, vetorDocTfIdf):
        produtoEscalar += x * y
        potenciaVetor1 += x**2
        potenciaVetor2 += y**2
    potenciaVetor1 = math.sqrt(potenciaVetor1)
    potenciaVetor2 = math.sqrt(potenciaVetor2)

    if potenciaVetor1 == 0 or potenciaVetor2 == 0:
        return 0
    else:
        return produtoEscalar/(potenciaVetor1 * potenciaVetor2)
def tf_idf_peso(qtdDocumentos, indiceInvertido, docIndiceInvertido):

    qtdReptTermosDoc = [] #quantidade de repetição em todo o documento
    for termo, conjunto in indiceInvertido:
        qtd = len(conjunto)
        qtdReptTermosDoc.append((termo, qtd,))

    listaIdf = []
    for termo, qtd in qtdReptTermosDoc:
        idf = math.log10(qtdDocumentos/qtd)
        listaIdf.append((termo, idf))

    dicTf_Idf = {}
    for conjunto in docIndiceInvertido:
        doc, dicionario = conjunto

        if doc not in dicTf_Idf:
            dicTf_Idf[doc] = []

        novoConjunto = []
        for termo, peso in listaIdf:
            if termo in dicionario:
                f = int(dicionario[termo][0]) #frequencia de repetição no documento
                w = (1 + math.log10(f)) * peso
                novoConjunto.append((termo, w))

        dicTf_Idf[doc].extend(novoConjunto)

    return listaIdf, dicTf_Idf
def higienizarDocumento(documento):
    doc = nlp(documento)
    termos = []
    for token in doc:
        if not token.is_stop: #remove stopwords
            if not token.is_punct: #Remove as pontuações
                if token.text.strip() != "": #remove caracteres em branco
                    termo = token.lemma_ #lemma_ retorna a forma base da palavra ex: profressores = professor
                    if not len(termo.split()) >= 2: #É raro ter lema formada por mais de uma palavra, logo é bem provável ser stopwords
                        termos.append(termo.lower().strip())
    return termos
def gerar_indice_invertido(base_documentos):

    indiceInvertido = {} #dicionário
    indiceInvertidoDocumento = {}
    for indiceDocumento, nome_documento in enumerate(base_documentos, start=1):

        print(f"Realizando a leitura do arquivo {indiceDocumento}, higienização e gerando indice invertido...")

        dir_doc = pasta_projeto("docs", nome_documento)
        arquivo = lerDocumento(dir_doc)

        #como o conteudo está vindo como lista, utilizo o join para virar uma string
        juntaTexto = " ".join(arquivo)

        termos = higienizarDocumento(juntaTexto)

        frequencia = contaFrequencia(indiceDocumento, termos)

        for termo, valores in frequencia.items():
            novoValor = valores[0].split(',')[1]
            indiceInvertidoDocumento.setdefault(nome_documento, {})[termo] = [novoValor]

        for termo, freq in frequencia.items():
            if termo not in indiceInvertido:
                indiceInvertido[termo] = []

            #adiciona a frequencia ao dicionario indiceInvertido separando por virgula
            indiceInvertido[termo].extend(freq)

    indiceOrdenado = sorted(indiceInvertido.items()) #retorna o dicionário ordenado

    indiceOrdenadoDocumento = sorted((indiceInvertidoDocumento.items()))
    
    return indiceOrdenado, indiceOrdenadoDocumento
def lerDocumento(diretorio):
    caminho_arquivo = []
    try:
        with open(diretorio, 'r') as arquivo:
            for linha in arquivo:
                caminho = linha.strip() #remove os espaços em branco e quebra de linha
                if caminho:
                    caminho_arquivo.append(caminho)
        return caminho_arquivo
    except FileNotFoundError:
        print(f"O arquivo {diretorio} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao abrir o arquivo: {e}")
        return None
def abrirArqConsulta(nomeArquivo):
    try:
        with open(nomeArquivo, 'r') as arquivo:
            conteudo = arquivo.read()
            return conteudo
    except FileNotFoundError:
        print(f"O arquivo {nomeArquivo} não foi encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao abrir o arquivo: {e}")
        return None
def contaFrequencia(numero_arquivo, termos):
    freq = {}
    for termo in termos:
        if termo not in freq: #se termo não está na frequencia
            freq[termo] = []
            dados = str(numero_arquivo) + "," + str(termos.count(termo)) #com a lista criada adiciono os valores concatenados
            freq[termo].append(dados) #adiciona os dados filtrando pelo termo
    return freq
def guardarArquivoPeso(dicTfIdf):

    if not os.path.exists("respostas"):
        os.makedirs("respostas")
    
    diretorio = pasta_projeto("respostas", "peso.txt")

    with open(diretorio, "w") as arquivoPeso:
        for documento,  lista_termos in dicTfIdf.items():
            arquivoPeso.write(f"{documento}: ")
            for t, peso in lista_termos:
                arquivoPeso.write(f"{t}:{peso} ")
            arquivoPeso.write("\n")
def guardarArquivoRespostaConsulta(qtdDocs, similaridades):

    if not os.path.exists("respostas"):
        os.makedirs("respostas")
    
    diretorio = pasta_projeto("respostas", "resposta.txt")

    with open(diretorio, "w") as arquivoSimilaridades:
        arquivoSimilaridades.write(f"{qtdDocs}\n")
        for documento,  similaridade in similaridades.items():
            arquivoSimilaridades.write(f"{documento}: {similaridade}")
            arquivoSimilaridades.write("\n")
def guardarArquivoIndiceInvertido(IndiceInvertido):
    
    if not os.path.exists("respostas"):
        os.makedirs("respostas")
    
    diretorio = pasta_projeto("respostas", "indice.txt")

    with open(diretorio, "w") as arquivo:
        for termo, numeros in IndiceInvertido:
            arquivo.write(f"{termo}: ")
            for n in numeros:
                arquivo.write(f"{n} ")
            arquivo.write("\n")
def main():
    '''
    if len(sys.argv) != 3:
        sys.exit(1)

    baseDoc = sys.argv[1]
    consulta = sys.argv[2]
    '''
    # Ler a base.txt retornará uma lista de nomes de arquivo
    print("\n******Autor: Tárick Lorran Batista Leite******\n")
    print("Buscando a base de documentos...\n")

    baseDoc = "base.txt"
    consulta = "consulta6.txt"

    dir = pasta_projeto("docs", baseDoc)

    base_documentos = lerDocumento(dir)

    #Quantidade de documentos a ser lidos
    qtdDocumentos = len(base_documentos)

    print(f"Quantidade de documentos: {qtdDocumentos}\n")

    print(f"{base_documentos}\n")

    indiceInvertido, docIndiceInvertido = gerar_indice_invertido(base_documentos)
    # indiceInvertido = [('w', ['1,3', '2,2', '3,2']), ('x', ['1,1', '4,2']), ('y', ['2,1'])]
    # docIndiceInvertido = [('Doc1.txt', {'w': ['3'], 'x': ['1']}), ('Doc.txt', {'w': ['2'], 'y': ['1']}), ('Doc3.txt', {'w': ['2']}), ('Doc4.txt', {'x': ['2']})]

    print("Indice invertido gerado...\n")

    print("Calculando os pesos de cada termo do documento...\n")

    listaIdf, dicTfIdf = tf_idf_peso(qtdDocumentos, indiceInvertido, docIndiceInvertido)
    #listaIdf = [('w', 0.12493873660829993), ('x', 0.3010299956639812), ('y', 0.6020599913279624)]
    #dicTfIdf = {'Doc1.txt': [('w', 0.18454966338194143), ('x', 0.3010299956639812)], 'Doc2.txt': [('w', 0.16254904394775976), ('y', 0.6020599913279624)], 'Doc3.txt': [('w', 0.16254904394775976)], 'Documento4.txt': [('x', 0.39164905395343774)]}

    print("Calculo dos pesos finalizado...\n")

    print("Gerando o arquivo indice.txt...\n")
    guardarArquivoIndiceInvertido(indiceInvertido)

    print("Gerando o arquivo peso.txt...\n")
    guardarArquivoPeso(dicTfIdf)

    print("Montando o vetor consulta...\n")

    listConsulta = []
    listConsulta.append(consulta)

    vetorConsultaIdf = criarVetorConsulta(listConsulta, listaIdf)
    #vetorConsulta = [0.12493873660829993, 0, 0.6020599913279624]

    print("\nMontando o vetor de peso dos documentos e calculando a similaridade...\n")

    similaridades = {}
    for doc, tfIdf in dicTfIdf.items():
        vetorDocTfIdf = criarVetorDocumento(tfIdf, listaIdf)
        #vetorDocTfIdf = [0.18454966338194143, 0.3010299956639812, 0]

        similaridade = calcSimilaridade(vetorConsultaIdf, vetorDocTfIdf)

        #Patamar minimo para um doc ser considerado relevante
        if similaridade > 0.01:
            similaridades[doc] = similaridade

    #Ordena os documentos de acordo com sua similaridade
    similaridades_ordenadas = dict(sorted(similaridades.items(), key=lambda item: item[1], reverse=True))
    #similaridades_ordenadas = {'Documento2.txt': 0.9982549184765698, 'Documento3.txt': 0.20318977863036336, 'Documento1.txt': 0.1061990994632494}

    print("Gerando o arquivo resposta.txt...\n")
    qtdDocs = len(similaridades_ordenadas)

    guardarArquivoRespostaConsulta(qtdDocs, similaridades_ordenadas)

    print("Processo finalizado!")

if __name__ == "__main__":
    main()