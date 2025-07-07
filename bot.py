#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import psutil
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
from telegram.error import Conflict

# --- Função para evitar múltiplas instâncias ---

def checar_instancias():
    """Impede múltiplas instâncias do bot rodando ao mesmo tempo."""
    atual_pid = os.getpid()
    nome_script = os.path.basename(__file__)

    for proc in psutil.process_iter(attrs=["pid", "cmdline"]):
        try:
            cmdline = proc.info["cmdline"]
            pid = proc.info["pid"]

            if cmdline and nome_script in ' '.join(cmdline) and pid != atual_pid:
                print(f"❌ Já existe outra instância rodando (PID: {pid})")
                sys.exit(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

# Chama a função logo no início do programa
checar_instancias()

# --- Carregando .env ---

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"AVISO: Arquivo .env não encontrado em {dotenv_path}")

token = os.getenv("TOKEN")

# --- Configura logging ---

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

if not token:
    logger.error("TOKEN não encontrado no .env")
    sys.exit(1)

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Olá, {user.first_name}! 👋\n\n"
        "Eu sou seu bot Telegram. Use /help para ver os comandos disponíveis.",
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Aqui estão os comandos que você pode usar:\n"
        "/start - Inicia o bot e mostra uma mensagem de boas-vindas\n"
        "/help - Mostra esta mensagem de ajuda\n"
        "Qualquer outra mensagem que você enviar será repetida por mim."
    )
    await update.message.reply_text(help_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Você disse: {update.message.text}")

# --- Antes do polling, remove webhook ativo ---

async def on_startup(app):
    await app.bot.delete_webhook()

# --- Função principal ---

def main():
    try:
        app = ApplicationBuilder().token(token).post_init(on_startup).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        app.run_polling()

    except Conflict:
        logger.error("Erro de conflito: outra instância do bot está rodando")
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")

if __name__ == "__main__":
    main()
