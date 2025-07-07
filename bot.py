#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Caminho absoluto pro .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Carrega variáveis de ambiente do .env
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"AVISO: Arquivo .env não encontrado em {dotenv_path}")

# Lê o TOKEN do .env
token = os.getenv("TOKEN")

# Configura logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Verifica se o token foi carregado
if not token:
    logger.error("TOKEN não encontrado no .env")
    exit(1)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.mention_markdown_v2()}!",
        parse_mode=ParseMode.MARKDOWN_V2
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")

# Qualquer outra mensagem
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

# Função principal
def main():
    try:
        app = ApplicationBuilder().token(token).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        app.run_polling()
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")

# Executa se rodado diretamente
if __name__ == "__main__":
    main()
