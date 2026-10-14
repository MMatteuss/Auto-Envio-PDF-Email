import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime


def download_html(url):
    """Faz o download do HTML direto na memória (sem salvar em disco)."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer download: {e}")
        return None


def extrair_vagas_direto(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    vagas_data = []

    containers = soup.find_all('div', class_='container')

    for container in containers:
        card_body = container.find('div', class_='card-body')
        if not card_body:
            continue

        # Nome da vaga
        h5_tag = card_body.find('h5', style='color:#00F')
        if not h5_tag:
            continue
        nome_vaga = h5_tag.get_text(strip=True)

        # Email
        email = None
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', card_body.get_text())
        if email_match:
            email = email_match.group()

        dados_vaga = {
            'Nome da Vaga': nome_vaga,
            'Email': email,
            'Requisitos': '',
            'Atividades': '',
            'Benefícios': '',
            'Observações': ''
        }

        texto_completo = card_body.get_text()

        # Requisitos
        m = re.search(r'Requisitos\s*(.*?)(?=Atividades|Benefícios|Observações|Inserida em:|$)', texto_completo, re.DOTALL)
        if m:
            dados_vaga['Requisitos'] = m.group(1).strip()

        # Atividades
        m = re.search(r'Atividades\s*(.*?)(?=Benefícios|Observações|Inserida em:|$)', texto_completo, re.DOTALL)
        if m:
            dados_vaga['Atividades'] = m.group(1).strip()

        # Benefícios
        m = re.search(r'Benefícios\s*(.*?)(?=Observações|Inserida em:|$)', texto_completo, re.DOTALL)
        if m:
            dados_vaga['Benefícios'] = m.group(1).strip()

        # Observações
        m = re.search(r'Observações\s*(.*?)(?=Inserida em:|É proibido|$)', texto_completo, re.DOTALL)
        if m:
            dados_vaga['Observações'] = m.group(1).strip()

        # Datas
        datas = re.findall(r'(\d{2}/\d{2}/\d{4})', texto_completo)
        if len(datas) >= 2:
            dados_vaga['Data Inserida'] = datas[-2]
            dados_vaga['Data Limite'] = datas[-1]
        elif len(datas) == 1:
            dados_vaga['Data Inserida'] = datas[0]
            dados_vaga['Data Limite'] = None

        vagas_data.append(dados_vaga)

    return vagas_data


def main():
    url = "https://www.advancerh.com.br/vagas.php"

    # 1) Download do HTML (somente em memória)
    print("Fazendo download do HTML...")
    html_content = download_html(url)
    if not html_content:
        print("Não foi possível obter o HTML. Encerrando.")
        return

    # 2) Garantir que a pasta "dados" exista
    os.makedirs('dados', exist_ok=True)

    # 3) Extrair vagas
    print("Extraindo vagas...")
    vagas = extrair_vagas_direto(html_content)

    if not vagas:
        print("Nenhuma vaga foi extraída. Verifique a estrutura do HTML.")
        return

    # 4) Montar DataFrame
    df = pd.DataFrame(vagas)

    colunas_ordenadas = ['Nome da Vaga', 'Email', 'Data Inserida', 'Data Limite',
                         'Requisitos', 'Atividades', 'Benefícios', 'Observações']
    for coluna in colunas_ordenadas:
        if coluna not in df.columns:
            df[coluna] = None
    df = df[colunas_ordenadas]

    # 5) Nome do arquivo (barras são inválidas em nomes de arquivo)
    data_str = datetime.now().strftime('%d-%m-%Y')  # troque por %d/%m/%Y se preferir
    nome_arquivo = os.path.join('dados', f'Excel-{data_str}.xlsx')

    # 6) Salvar Excel
    df.to_excel(nome_arquivo, index=False, engine='openpyxl')
    print(f"\n✅ Foram extraídas {len(vagas)} vagas.")
    print(f"📁 Arquivo salvo em: {nome_arquivo}")

    # 7) Estatísticas rápidas
    print("\nEstatísticas:")
    print(f"  Total de vagas:          {len(vagas)}")
    print(f"  Vagas com requisitos:    {sum(1 for v in vagas if v['Requisitos'])}")
    print(f"  Vagas com atividades:    {sum(1 for v in vagas if v['Atividades'])}")
    print(f"  Vagas com benefícios:    {sum(1 for v in vagas if v['Benefícios'])}")
    print(f"  Vagas com observações:   {sum(1 for v in vagas if v['Observações'])}")


if __name__ == "__main__":
    main()