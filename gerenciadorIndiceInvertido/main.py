import spacy
import sys

#Token é uma porção de texto que pode ser uma palavra, pontuação, numerais, sentenças, etc.
diretorio = r"C:\Users\lorra\Documents\Cursos\Udemy\Python\pythonProject\\"

def higienizarDocumento(documento):
    nlp = spacy.load("pt_core_news_lg")
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
    for indiceDocumento, nome_documento in enumerate(base_documentos, start=1):

        print(f"Realizando a leitura do arquivo {indiceDocumento}, higienização e gerando indice invertido...")

        arquivo = lerDocumento(diretorio + nome_documento)

        #como o conteudo está vindo como lista, utilizo o join para virar uma string
        juntaTexto = " ".join(arquivo)

        termos = higienizarDocumento(juntaTexto)

        frequencia = contaFrequencia(indiceDocumento, termos)

        for termo, freq in frequencia.items():
            if termo not in indiceInvertido:
                indiceInvertido[termo] = []

            #adiciona a frequencia ao dicionario indiceInvertido separando por virgula
            indiceInvertido[termo].extend(freq)

    indiceOrdenado = sorted(indiceInvertido.items()) #retorna o dicionário ordenado
    return indiceOrdenado
def lerDocumento(diretorio):
    caminho_arquivo = []
    try:
        with open(diretorio, 'r') as arquivo:
            for linha in arquivo:
                caminho = linha.strip() #remove os espaços em branco e quebra de linha
                if caminho:
                    caminho_arquivo.append(caminho)
        return caminho_arquivo
    except:
        print("Não foi possível abrir o arquivo.")
        arquivo.close()
#Gera o indice invertido
def contaFrequencia(numero_arquivo, termos):
    freq = {}
    for termo in termos:
        if termo not in freq: #se termo não está na frequencia
            freq[termo] = []
            dados = str(numero_arquivo) + "," + str(termos.count(termo)) #com a lista criada adiciono os valores concatenados
            freq[termo].append(dados) #adiciona os dados filtrando pelo termo
    return freq
def guardarArquivo(documento):
    with open("indice.txt", "w") as arquivo:
        for termo, numeros in documento:
            arquivo.write(f"{termo}: ")
            for n in numeros:
                arquivo.write(f"{n} ")
            arquivo.write("\n")
def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    parametro = sys.argv[1]

    # Ler a base.txt retornará uma lista de nomes de arquivo
    print("\n******Autor: Tárick Lorran Batista Leite******\n")
    print("Buscando a base de documentos...\n")
    base_documentos = lerDocumento(diretorio + parametro)

    print(f"{base_documentos}\n")

    arquivo = gerar_indice_invertido(base_documentos)

    print("Indice invertido gerado...\n")
    print("Gerando o arquivo Indice.txt...\n")

    guardarArquivo(arquivo)

    print("Processo finalizado!")




if __name__ == "__main__":
    main()