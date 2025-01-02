import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, DocumentAttributeVideo
from dotenv import load_dotenv

load_dotenv()

# Substitua pelos seus valores da API do Telegram
api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")

# Nome da sessão do cliente
session_name = "jmhbot"
# Nome da pasta para salvar as imagens e vídeos
output_folder = "imagens"

# Certifique-se de que a pasta existe
os.makedirs(output_folder, exist_ok=True)

# Inicialize o cliente
client = TelegramClient(session_name, api_id, api_hash)


async def save_media(event):
    """Função para salvar imagens e vídeos"""
    message = event.message

    if isinstance(message.media, MessageMediaPhoto):
        # Salva imagens
        file_path = await client.download_media(message.media, output_folder)
        print(f"Imagem salva em: {file_path}")

    elif message.media and message.media.document:
        # Verifica se o documento é um vídeo
        for attribute in message.media.document.attributes:
            if isinstance(attribute, DocumentAttributeVideo):
                file_path = await client.download_media(message.media, output_folder)
                print(f"Vídeo salvo em: {file_path}")


async def main():
    # Substitua pelo nome ou ID do grupo desejado
    target_group = input("Digite o nome ou link do grupo/ID: ")

    async for dialog in client.iter_dialogs():
        if target_group in (dialog.name, dialog.entity.username, str(dialog.id)):
            print(f"Entrando no grupo: {dialog.name}")
            group = dialog.entity
            break
    else:
        print("Grupo não encontrado.")
        return

    @client.on(events.NewMessage(chats=group))
    async def handler(event):
        await save_media(event)

    print("Escutando novas mensagens... Pressione Ctrl+C para sair.")
    await client.run_until_disconnected()


# Executa o cliente
with client:
    client.loop.run_until_complete(main())
