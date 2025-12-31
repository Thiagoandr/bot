import telebot
import requests
from bs4 import BeautifulSoup

TOKEN = ""  #tirei o token, vou esconder ela de forma formal em outros commits
bot = telebot.TeleBot(TOKEN)


def buscar_livros_anna(termo):
 
    url = "https://annas-archive.org/search"
    params = {
        "q": termo,
        "ext": "epub", #por enquanto quero epub
        "sort": "most_relevant"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        print(f"\nBuscando: {termo}")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        livros = []
        
        
        all_links = soup.find_all('a', href=True)
        book_links = [a for a in all_links if '/md5/' in a.get('href', '')][:10]
        
        print(f"Links de livros encontrados: {len(book_links)}")
        
        if not book_links:
            print("Nenhum link encontrado!")
            print("HTML (primeiros 500 chars):")
            print(response.text[:500])
            return []
        
        for item in book_links[:5]:
            try:
                link_completo = item.get('href', '')
                
                if link_completo.startswith('/'):
                    link_completo = "https://annas-archive.org" + link_completo
                
            
                titulo = "Titulo nao disponivel"
                autor = "Autor desconhecido"
                
                
                text = item.get_text(strip=True)
                if text and len(text) > 3:
                    titulo = text
                
              
                parent = item.find_parent()
                if parent:
                    # Tentar encontrar título
                    bold = parent.find('div', class_='font-bold') or parent.find('span', class_='font-bold')
                    if bold:
                        titulo = bold.get_text(strip=True)
                    
                    # vai encontrar o autor
                    italic = parent.find('div', class_='italic') or parent.find('span', class_='italic')
                    if italic:
                        autor = italic.get_text(strip=True)
                
                livros.append({
                    "titulo": titulo[:150],
                    "autor": autor[:100],
                    "link": link_completo
                })
                
            except Exception as e:
                print(f"Erro ao processar item: {e}")
                continue
        
        print(f"Total de livros extraidos: {len(livros)}")
        return livros
        
    except requests.exceptions.Timeout:
        print("Timeout na requisicao")
        raise Exception("Site demorou muito para responder. Tente novamente.")
    
    except requests.exceptions.RequestException as e:
        print(f"Erro de rede: {e}")
        raise Exception(f"Erro ao conectar: {str(e)[:100]}")
    
    except Exception as e:
        print(f"Erro geral: {type(e).__name__} - {e}")
        raise


@bot.message_handler(commands=['start'])
def start(message):
    mensagem = """
Bot de Busca - Anna's Archive

Ola! Estou aqui para te ajudar a encontrar livros.

Como usar:
/livro nome do livro

Exemplo:
/livro harry potter
/livro clean code
/livro 1984

Vou buscar ate 5 resultados para voce!
    """
    bot.send_message(message.chat.id, mensagem)


@bot.message_handler(commands=['livro'])
def livro(message):
    termo = message.text.replace('/livro', '').strip()
    
    if not termo:
        bot.send_message(
            message.chat.id, 
            "Uso incorreto!\n\nDigite assim:\n/livro nome do livro\n\nExemplo:\n/livro harry potter"
        )
        return
    
    msg_aguarde = bot.send_message(
        message.chat.id, 
        f"Buscando '{termo}' no Anna's Archive...\nAguarde um momento."
    )
    
    try:
        livros = buscar_livros_anna(termo)
        
        bot.delete_message(message.chat.id, msg_aguarde.message_id)
        
        if not livros:
            bot.send_message(
                message.chat.id,
                f"Nenhum livro encontrado para: {termo}\n\n"
                "Dicas:\n"
                "- Tente palavras-chave mais simples\n"
                "- Verifique a ortografia\n"
                "- Tente buscar pelo autor"
            )
            return
        
        resposta = f"Encontrei {len(livros)} resultado(s) para: {termo}\n\n"
        
        for i, livro in enumerate(livros, 1):
            resposta += f"{i}. {livro['titulo']}\n"
            resposta += f"Autor: {livro['autor']}\n"
            resposta += f"Link: {livro['link']}\n\n"
        
        resposta += "Clique no link para ver detalhes e baixar"
        
        if len(resposta) > 4000:
            bot.send_message(message.chat.id, resposta[:4000])
            bot.send_message(message.chat.id, resposta[4000:])
        else:
            bot.send_message(message.chat.id, resposta)
    
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, msg_aguarde.message_id)
        except:
            pass
        
        erro_msg = f"Erro ao buscar livros\n\n"
        erro_msg += f"{str(e)}\n\n"
        erro_msg += "Possiveis solucoes:\n"
        erro_msg += "- Tente novamente em alguns segundos\n"
        erro_msg += "- Verifique sua conexao\n"
        erro_msg += "- O site pode estar temporariamente indisponivel"
        
        bot.send_message(message.chat.id, erro_msg)
        
        print(f"\nERRO COMPLETO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")


@bot.message_handler(func=lambda message: True)
def resposta_padrao(message):
    bot.send_message(
        message.chat.id,
        "Nao entendi esse comando.\n\n"
        "Use: /livro nome do livro\n"
        "Ou: /start para ver as instrucoes"
    )


if __name__ == "__main__":
    print("Bot iniciando...")
    print("Bot online e pronto!")
    print("=" * 50)
    bot.infinity_polling(skip_pending=True)