import os
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, DocumentAttributeVideo
from dotenv import load_dotenv

load_dotenv()

# 🔹 Substitua pelos seus valores da API do Telegram
api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")

# Nome da sessão do cliente
session_name = os.getenv("name")
# Nome da pasta para salvar imagens e vídeos
output_folder = "imagens"

# Certifique-se de que a pasta existe
os.makedirs(output_folder, exist_ok=True)

# Inicializa o cliente do Telegram
client = TelegramClient(session_name, api_id, api_hash)


async def search_and_download(group_name, hashtag):
    """Busca mensagens com uma hashtag e baixa suas mídias"""
    async with client:
        print(f"🔎 Pesquisando mensagens com '{hashtag}' em {group_name}...")

        # Obtém a entidade do grupo pelo nome/ID
        group = await client.get_entity(group_name)

        # Procura mensagens contendo a hashtag
        async for message in client.iter_messages(group, search=hashtag):
            if message.media:
                media_files = []

                if message.grouped_id:  # Verifica se a mensagem faz parte de um álbum
                    async for msg in client.iter_messages(
                        message.chat_id, min_id=message.id - 10, max_id=message.id + 10
                    ):
                        if msg.grouped_id == message.grouped_id and msg.media:
                            file_path = await client.download_media(
                                msg.media, output_folder
                            )
                            if file_path:
                                media_files.append(file_path)
                                print(f"📥 Mídia do álbum salva: {file_path}")
                else:
                    if message.media:
                        file_path = await client.download_media(
                            message.media, output_folder
                        )
                        if file_path:
                            media_files.append(file_path)
                            print(f"📥 Mídia salva: {file_path}")

        print("🎉 Download concluído!")


if __name__ == "__main__":
    group = input("Digite o nome ou ID do grupo: ")
    hashtag = input("Digite a hashtag a ser buscada: ")

    with client:
        client.loop.run_until_complete(search_and_download(int(group), hashtag))
