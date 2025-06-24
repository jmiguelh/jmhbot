import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import (
    Channel,
    Chat,
)  # , DocumentAttributeVideo, MessageMediaPhoto

load_dotenv()

# 🔹 Substitua pelos seus valores da API do Telegram
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

# Nome da sessão do cliente
session_name = os.getenv("NAME")
# Nome da pasta para salvar imagens e vídeos
output_folder = "imagens"

last_message_file = "ultimo_processamento.txt"

# Certifique-se de que a pasta existe
Path.os.makedirs(output_folder, exist_ok=True)

# Inicializa o cliente do Telegram
client = TelegramClient(session_name, api_id, api_hash)


async def search_and_download(group_name, hashtag):
    """Busca mensagens com uma hashtag e baixa suas mídias"""
    async with client:
        print(f"🔎 Pesquisando mensagens com '{hashtag}' em {group_name}...")

        # Obtém a entidade do grupo pelo nome/ID
        group = await client.get_entity(group_name)
        last_date = load_last_message_date()

        # Procura mensagens contendo a hashtag
        async for message in client.iter_messages(group, search=hashtag, reverse=True):
            if last_date and message.date <= last_date:
                continue  # Ignora mensagens já processadas
            await download_all_media(message)
            save_last_message_date(message.date)

        print("🎉 Download concluído!")


async def download(group_name):
    """Busca mensagens com uma hashtag e baixa suas mídias"""
    async with client:
        print(f"🔎 Pesquisando mensagens do grupo {group_name}...")

        # Obtém a entidade do grupo pelo nome/ID
        group = await client.get_entity(group_name)
        last_date = load_last_message_date()

        # Procura mensagens contendo a hashtag
        async for message in client.iter_messages(group, reverse=True):
            if last_date and message.date <= last_date:
                continue  # Ignora mensagens já processadas
            await download_all_media(message)
            save_last_message_date(message.date)

        print("🎉 Download concluído!")


async def download_all_media(message):
    if message.media:
        media_files = []

        if message.grouped_id:  # Verifica se a mensagem faz parte de um álbum
            async for msg in client.iter_messages(
                message.chat_id, min_id=message.id - 10, max_id=message.id + 10
            ):
                if msg.grouped_id == message.grouped_id and msg.media:
                    file_path = await client.download_media(msg.media, output_folder)
                    if file_path:
                        media_files.append(file_path)
                        print(f"📥 Mídia do álbum salva: {file_path}")
        else:
            if message.media:
                file_path = await client.download_media(message.media, output_folder)
                if file_path:
                    media_files.append(file_path)
                    print(f"📥 Mídia salva: {file_path}")


def save_last_message_date(date):
    """Salva a data/hora da última mensagem processada (em UTC)."""
    with Path.open(last_message_file, "w") as f:
        f.write(date.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S"))


def load_last_message_date():
    """Carrega a última data/hora processada (como UTC)."""
    if Path.exists(last_message_file):
        with Path.open(last_message_file) as f:
            last_date = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
            return last_date.replace(tzinfo=UTC)  # Converte para timezone-aware
    return None  # Se não houver registro, retorna None


async def listar_grupos():
    print("🔍 Listando grupos e canais...")

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        if isinstance(entity, Channel | Chat):
            tipo = (
                "Canal" if isinstance(entity, Channel) and entity.broadcast else "Grupo"
            )
            print(
                f"{tipo}: {dialog.name} | ID: {entity.id} | Acesso: {'@'+entity.username if getattr(entity, 'username', None) else 'privado'}"
            )


with client:
    client.loop.run_until_complete(listar_grupos())


if __name__ == "__main__":

    group = input("Digite o nome ou ID do grupo: ")
    hashtag = input("Digite a hashtag a ser buscada: ")

    with client:
        # client.loop.run_until_complete(search_and_download(int(group), hashtag))
        client.loop.run_until_complete(download(int(group)))
    # with client:
    #     client.loop.run_until_complete(listar_grupos())
