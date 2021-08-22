import requests as r
import datetime as dt
import csv
from PIL import Image
from IPython.display import display
from urllib.parse import quote

#define os helpers (vão ajudar a colocar no formato que a API do gráfico pede)
def get_datasets(y, labels):
    if (type(y[0]) == list):
        datasets = []
        for i in range(len(y)):
            datasets.append({
                'label': labels[i],
                'data': y[i]
            })
        return datasets
    else:
        return[
            {
                'label': labels[0],
                'data': y
            }
        ]


def set_title(title=''):
    if title != '':
        display = 'true'
    else:
        display = 'false'
    return {
        'title': title,
        'display': display
    }


def create_chart(x, y, labels, kind='bar', title=''):
    datasets = get_datasets(y, labels)
    options = set_title(title)

    chart = {
        'type': kind,
        'data': {
            'labels': x,
            'datasets': datasets
        },
        'options': options
    }

    return chart


def get_api_chart(chart):
    url_base = 'https://quickchart.io/chart'
    resp = r.get(f'{url_base}?c={str(chart)}')

    return resp.content


#funções para salvar/mostrar as imagens geradas
def save_image(path, content):
    with open(path, 'wb') as image:
        image.write(content)

def display_image(path):
    img_pil = Image.open(path)
    display(img_pil)


def get_api_qrcode(link):
    text = quote(link) #parsing do link para url
    url_base = 'https://quickchart.io/qr'
    resp = r.get(f'{url_base}?text={text}')
    return resp.content



def main():
    #define a url e faz o request para obter os dados "crus"
    url = 'https://api.covid19api.com/dayone/country/brazil'
    resp = r.get(url)

    #converte os dados obtidos em json para csv
    raw_data = resp.json()

    #armazena os valores que interessam (casos confirmados, mortes, recuperados, ativos e a data dos dados)
    final_data = []
    for obs in raw_data:
        final_data.append([obs['Confirmed'], obs['Deaths'], obs['Recovered'], obs['Active'], obs['Date']])

    #insere o header
    final_data.insert(0, ['Confirmados', 'Mortes', 'Recuperados', 'Ativos', 'Data'])

    #criando os índices
    CONFIRMADOS = 0
    MORTES = 1
    RECUPERADOS = 2
    ATIVOS = 3
    DATA = 4

    #deixa a data com os caracteres necessários somente
    for i in range(1, len(final_data)):
        final_data[i][DATA] = final_data[i][DATA][:10]

    #cria um arquivo e escreve os dados que nós obtemos
    with open('brasil-covid.csv', 'w') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(final_data)

    #coloca a data no formato "comum"
    for i in range(1, len(final_data)):
        final_data[i][DATA] = dt.datetime.strptime(final_data[i][DATA], '%Y-%m-%d')

    #faz uma lista com os números de casos confirmados
    y_data_1 = []
    for obs in final_data[1::30]: #começa de 1 porque o 0 é o header
        y_data_1.append(obs[CONFIRMADOS])

    #faz uma lista com os números de mortes
    y_data_2 = []
    for obs in final_data[1::30]:
        y_data_2.append(obs[MORTES])

    #faz uma lista com os números de casos recuperados
    y_data_3 = []
    for obs in final_data[1::30]:
        y_data_3.append(obs[RECUPERADOS])

    #define a legenda do gráfico
    labels = ['Confirmados', 'Mortos', 'Recuperados']

    #insere as informações do eixo x
    x = []
    for obs in final_data[1::30]:
        x.append(obs[DATA].strftime('%d/%m/%Y'))


    chart = create_chart(x, [y_data_1, y_data_2, y_data_3], labels, title = 'Confirmados/Mortos/Recuperados')
    chart_content = get_api_chart(chart)
    save_image('graficovid.png', chart_content)
    #display_image('graficovid.png') deveria mostrar a image, mas o pycharm nao abre

    url_base = 'https://quickchart.io/chart'
    link = f'{url_base}?c={str(chart)}'
    save_image('qrcode.png', get_api_qrcode(link))
    #display_image('qrcode.png') deveria mostrar a image, mas o pycharm nao abre

if __name__ == '__main__':
    main()
