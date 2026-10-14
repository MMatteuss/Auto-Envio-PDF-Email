# Importação
import pandas as pd
from ollama import Client
from pypdf import PdfReader
from datetime import datetime

# Base de dados com base planilha
baseDados = pd.read_excel('dados\Excel-03-10-2026.xlsx', sheet_name='Sheet1')

# Relatorio
relatorioName = f"relatorio {datetime.now().strftime('%d-%m-%Y')}.txt"
relatorio = relatorioName.replace(":", "-").replace("/", "-")

# Config Ollama IA
OLLAMA_HOST = "http://127.0.0.1:11434" # IP Local da IA
client = Client(host=OLLAMA_HOST)

# Trasformar PDF em texto para prompt
curriculoPdf = r"C:\Users\Yale\Documents\GitHub\Auto Envio PDF Email\CV\MATEUS ARAUJO MONTEIRO - Assitente Logistica.pdf"
leitor = PdfReader(curriculoPdf)
curriculo = ""
for pagina in leitor.pages:
  curriculo += pagina.extract_text() + "\n"

# Otimizar o texto do curriculo
def otimiCurriculo(curriculo):
    texto = str(curriculo)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    linhas = []
    for linha in texto.split("\n"):
        linha = " ".join(linha.split())
        if linha:
            linhas.append(linha)
    texto = "\n".join(linhas)
    return f"""
  CURRÍCULO DO CANDIDATO:
  {texto}

  FIM DO CURRÍCULO
  """.strip()

# Otimizar o texto da vaga
def otimiVaga(vagas):
    texto = (str(vagas)).replace("\r\n", "\n").replace("\r", "\n")
    linhas = []

    for linha in texto.split("\n"):
        linha = " ".join(linha.split())
        if linha:
            linhas.append(linha)
    texto = "\n".join(linhas)

    return f"""
  VAGA DE EMPREGO:
  {texto}

  FIM DA VAGA
  """.strip()

# region IA+Prompt
# Função para resposta da IA Local
def perguntarIA(vaga1, cv1):
  prompt = f"""
Você é um avaliador de currículos.
Compare o CURRÍCULO com a VAGA e determine o quanto o candidato combina com ESSA VAGA.

CURRÍCULO:
{cv1}

VAGA:
{vaga1}

COMO AVALIAR:
1. Dê maior importância às experiências profissionais relacionadas às atividades da vaga.
2. Considere experiências semelhantes como experiência transferível.
3. Verifique os requisitos da vaga.
4. Compare as atividades já realizadas pelo candidato com as atividades da vaga.
5. Considere conhecimentos e cursos somente quando forem relevantes para a vaga.
6. Considere projetos somente quando ajudarem na função.
7. Não invente experiências, conhecimentos ou qualificações.
8. Não penalize o candidato por não possuir algo que a vaga não exige.
9. Ignore informações do currículo que não tenham relação com esta vaga.
10. A porcentagem deve representar a compatibilidade REAL entre candidato e vaga.
11. Primeiro identifique os pontos mais relevantes do currículo para esta vaga.
12. Depois identifique os principais pontos que faltam.
13. Use essas informações para determinar a porcentagem.

ESCALA:
0-20 = praticamente incompatível
21-40 = pouca compatibilidade
41-60 = compatibilidade média
61-80 = boa compatibilidade
81-100 = excelente compatibilidade

IMPORTANTE:
Avalie SOMENTE a vaga apresentada acima.
Não confunda experiências de outras áreas com a função da vaga.
Uma experiência só deve aumentar bastante a nota quando possuir relação com os requisitos ou atividades da vaga.

FORMATO OBRIGATÓRIO:
Responda em UMA ÚNICA LINHA.
Use exatamente este formato, substituindo as chaves pelo conteúdo real:
-XX%-Texto da justificativa aqui.

Exemplo de resposta válida:
-80%-O candidato possui experiência sólida em logística e controle de estoque, atendendo aos principais requisitos da vaga.

REGRAS DA RESPOSTA:
- XX deve ser um número inteiro entre 0 e 100.
- Deve existir apenas UMA porcentagem.
- A justificativa deve ser curta e objetiva (máximo de 2 frases).
- NUNCA escreva a palavra "JUSTIFICATIVA" na sua resposta. Escreva o texto real.
- Não use listas, títulos ou quebras de linha.
- Não use títulos.
- Não use quebra de linha.
- Não escreva nada antes de "-XX%-".
- Não escreva nada depois do ponto final.
- Use "." para separar ideias dentro da justificativa.
- Não use "%" na justificativa.
- Não repita a porcentagem.
- Não escreva instruções ou explicações sobre sua resposta.

Agora avalie o candidato.
  """
  print("-----")
  print(prompt)
  resposta = client.chat(
    model='qwen2.5:3b',
    messages=[{'role': 'user', 'content': prompt}]
  )
  return resposta['message']['content']
#endregion

# Envio da IA + CR (criação de relatorio)
def main():
  with open(relatorio, 'w', encoding='utf-8') as arquivo:
    arquivo.write("Relatório\n")
    num=0

    # Tive que explicar assim que eu achei complexo:
    for indice, linha_atual in baseDados.iterrows():
      num=num+1
      # Aqui o 'indice' ele vai começar do 0, os dados da 'linha_atual' são das linha inteira (exemplo: Linha 0 vai pegar todas as info)
      linhaCompleta = " " # Aqui vai começar vazio
      for coluna in baseDados.columns:
      # 'baseDados.columns' contém os nomes das colunas. O 'for' interno percorre cada nome; por exemplo, 'Nome', depois 'Cargo'
          valor = linha_atual[coluna]
          # Converte o conteúdo inteiro da célula para texto
          if valor is not None:
              valor = str(valor)
          # Ele irar ver se o valor é None, caso seja (exemplo: 25 -não é string-), ele irar pegar e irar colocar o str
          linhaCompleta += f"{coluna}: {valor}\n"
          # Aqui ele irar juntar e irar quebrar a linha para jogar na variavel, por isso tem '+=' e formando assim uma frase completa
      cv = otimiCurriculo(curriculo)
      vaga = otimiVaga(linhaCompleta)
      resposta = perguntarIA(vaga, cv)
      arquivo.write(f"{num};{resposta}\n")
      print(resposta)
main()