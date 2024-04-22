import sys
import matplotlib.pyplot as plt

def lerDocumento(diretorio):
    base_referencia = []
    base_resposta_ideal = []
    base_resposta_sistema = []

    try:
        with open(diretorio, 'r', encoding='utf-8') as arquivo:
            dados = arquivo.readlines() #Ler todo o arquivo

            for linha in dados:
                base_referencia.append(linha.strip()) #remove os espaços em branco e quebra de linha e adiciona na lista

            num_consulta = int(base_referencia[0]) #pega o primeiro item para saber a quantidade de consulta

            for i in range(1, num_consulta + 1):
                elemento = base_referencia[i].split() #para não ficar como uma unica string, quebro por elemento
                base_resposta_ideal.append(elemento)

            for n in range(num_consulta + 1, len(base_referencia)):
                elemento = base_referencia[n].split()
                base_resposta_sistema.append(elemento)

            #gera uma nova base de dicionario
            nova_base = {"num_consulta": num_consulta, "referencia_ideal": base_resposta_ideal, "referencia_sistema": base_resposta_sistema}

        return nova_base

    except:
        print("Não foi possível abrir o arquivo.")
        arquivo.close()

def calculo_precisao_revocacao(num_consulta, referencia_ideal, referencia_sistema):
    precisao = []
    revocacao = []

    '''Para cada documento, irei percorrer a lista  de referencia sistemica para saber se existe o item 
    na lista ideal, se sim irei realizar o cálculo da precisão, que nada mais é que a quantidade de item
     encontrado dividio pela quantidade de termo percorrido até achar o item. 
     A revocação é a quantidade encontrado dividido pela quantidade de item daquela consulta ideal'''

    for i in range(num_consulta):
        qtd_ideal = len(referencia_ideal[i])
        encontrou = 0

        aux_precisao = []
        aux_revocacao = []

        for j in range(len(referencia_sistema[i])):
            if referencia_sistema[i][j] in referencia_ideal[i]:
                encontrou += 1
                #print(f"Count = {count}, j + 1 = {j + 1}, precisão = {count/(j + 1)}\n")
                aux_precisao.append(encontrou/(j + 1))
                #print(f"Count = {count}, qtd_ideal = {qtd_ideal}, revocação = {count / qtd_ideal}\n")
                aux_revocacao.append(encontrou/qtd_ideal)

        precisao.append(aux_precisao)
        revocacao.append(aux_revocacao)

    return precisao, revocacao

def interpolacao(num_consulta, precisao, revocacao):
    #Cria a lista de níveis ex: 0%, 10%, 20%...100%
    niveis = []
    for i in range(0, 101, 10):
        niveis.append(i/100)

    interpolacao = []
    for i in range(num_consulta):
        juncao = []

        #Junta a revocacao com a precisão
        for revoc, prec in zip(revocacao[i], precisao[i]):
            juncao.append((revoc, prec))

        aux_interpolacao = []
        for nivel in niveis:
            precisao_maxima = 0

            for rev, prec in juncao:
                if rev >= nivel and prec > precisao_maxima:
                    precisao_maxima = prec
            aux_interpolacao.append((nivel, precisao_maxima))
        interpolacao.append(aux_interpolacao)

    return interpolacao

def media_precisao(interpolacao):
    media_resposta = {}
    soma_precisoes_nivel = {}
    contagem_nivel = {}

    #percorre a interpolação ex. [[(n, p), (n, p)], [(n, p), (n, p)],...]
    for consulta_interp in interpolacao:
        #percorre a [(n, p), (n, p), ...]
        for nivel, precisao in consulta_interp:
            #verifica se o item já está na lista, se sim soma com a outra precisao e
            # acrescenta a qtd de nivel
            if nivel in soma_precisoes_nivel:
                soma_precisoes_nivel[nivel] += precisao
                contagem_nivel[nivel] += 1
            #se não estiver na lista adiciona o valor da precisão e inicia a contagem
            # de nivel com 1
            else:
                soma_precisoes_nivel[nivel] = precisao
                contagem_nivel[nivel] = 1

    #Percorre a soma realizada e realiza o cálculo da médica
    for nivel, soma in soma_precisoes_nivel.items():
        media_resposta[nivel] = soma/contagem_nivel[nivel]

    return media_resposta

def guardarArquivo(documento):
    with open("media.txt", "w") as arquivo:
        for _, media in documento.items():
            arquivo.write(f"{round(media, 2)} ")

def plot_grafico(interpolacao, media):

    fig, eixos = plt.subplots(1, len(interpolacao) + 1, figsize=(15, 5))

    for i, dados in enumerate(interpolacao):
        interpolacao_percentual = []
        for rev, prec in dados:
            revocacao_precentual = rev * 100
            precisao_percentual = prec * 100
            interpolacao_percentual.append((revocacao_precentual, precisao_percentual))

        revocacao, precisao = zip(*interpolacao_percentual)

        eixos[i].plot(revocacao, precisao, marker="o", linestyle="-")
        eixos[i].set_xlabel("Revocação %")
        eixos[i].set_ylabel("Precisão %")
        eixos[i].set_title(f"Consulta {i + 1}")
        eixos[i].grid(True)

    #Plotar a média
    revocacao_media = []
    for rev in media.keys():
        revocacao_media.append(rev * 100)

    precisao_media = []
    for prec in media.values():
        precisao_media.append(prec * 100)

    eixos[len(interpolacao)].plot(revocacao_media, precisao_media, marker="o", linestyle="-")
    eixos[len(interpolacao)].set_xlabel("Revocação %")
    eixos[len(interpolacao)].set_ylabel("Precisão %")
    eixos[len(interpolacao)].set_title("Média")
    eixos[len(interpolacao)].grid(True)

    plt.tight_layout()
    plt.show()

def main():

    if len(sys.argv) != 2:
        sys.exit(1)
    parametro = sys.argv[1]

    print("\n******Autor: Tárick Lorran Batista Leite******\n")
    print("Buscando a(s) referencia(s)...\n")

    base_referencia = lerDocumento(parametro)

    #acessando um item do dicionario usando as chaves
    num_consulta = base_referencia["num_consulta"]
    resposta_ideal = base_referencia["referencia_ideal"]
    resposta_sistema = base_referencia["referencia_sistema"]

    print(f"Consulta: {num_consulta}\n")
    print(f"Resposta Ideal: {resposta_ideal}\n")
    print(f"Resposta Sistema: {resposta_sistema}")

    print("\nCalculando a precisão e revocação...")

    precisao, revocacao = calculo_precisao_revocacao(num_consulta, resposta_ideal, resposta_sistema)

    print("\nCalculando a interpolação...")

    interp = interpolacao(num_consulta, precisao, revocacao)

    print("\nCalculando a média das precisões...")

    media = media_precisao(interp)

    print("\nGerando o arquivo media.txt...")

    guardarArquivo(media)

    print("\nPlotando gráfico...")

    plot_grafico(interp, media)

    print("\nFim da execução.")


if __name__ == "__main__":
    main()