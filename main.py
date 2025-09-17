import asyncio
import threading
from telegram import Update, ForceReply
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from playwright.async_api import async_playwright

TOKEN = "8017025108:AAEN8QkEB66iJxAl3TtA89axtImXL5dETSs"
SERVER, RANGE = range(2)

async def run_playwright(server_num, range_start, range_end, bot, chat_id, loop):
    output_file = 'output.txt'
    # Clear previous output file content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('')

    proxy_address = "http://157.180.121.252:55574"

    async with async_playwright() as p:
        # Launch browser once with proxy configuration
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": proxy_address}
        )
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://my.sonjj.com/login?back=https%3A%2F%2Fsmailpro.com%2F")

        # Login steps
        await page.fill('input[name="email"]', "oops-mud-handclasp@duck.com")
        await page.fill('input[name="password"]', "Neljane143")
        await page.press('input[name="password"]', 'Enter')
        await page.click('.button_primary_mod')
        await page.click("//button[contains(., 'Full Access')]")

        seq_num = 1
        try:
            # Initial generation setup
            await page.click("//div[contains(@class, 'sm:block') and text()='Create']")
            await page.click("//span[text()='Google']")
            await page.click("//span[text()='Sequential']")
            await page.wait_for_timeout(500)
            await page.fill("//input[@type='number']", str(seq_num))
            await page.click("//span[text()='Real Account']")
            await page.click("//select")
            await page.select_option("//select", server_num)
            await page.wait_for_timeout(10000)
            await page.click("//button[contains(., 'Generate')]")
            await page.wait_for_selector("//div[contains(text(), '@gmail.com')]")
        except Exception as e:
            print(f"Error during first generation: {e}")

        # Loop for sequential generation within the specified range
        for seq_num in range(range_start, range_end + 1):
            try:
                await page.click("//div[contains(@class, 'sm:block') and text()='Create']")
                await page.fill("//input[@type='number']", str(seq_num))
                await page.click("//button[contains(., 'Generate')]")
                await page.wait_for_timeout(5000)

                email_elem = await page.wait_for_selector(
                    "//div[contains(@class, 'text-sm') and contains(@class, 'text-gray-500') and contains(@class, 'truncate')]")
                email_address = await email_elem.inner_text()

                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(email_address + '\n')

                # Delete generated emails in the trash if any
                while True:
                    trash_buttons = await page.query_selector_all(
                        "//button[contains(@class, 'bg-red-400') and contains(@class, 'rounded-full')]")
                    if not trash_buttons:
                        break
                    await trash_buttons[0].click()
                    await page.wait_for_timeout(1000)
                    modal_delete_btn = await page.wait_for_selector("//button[contains(@class, 'bg-red-500') and text()='Delete']")
                    await modal_delete_btn.click()
                    await page.wait_for_timeout(1000)

                print(f"Extracted email {email_address} saved for sequential number {seq_num}")
            except Exception as e:
                print(f"Error in iteration for seq_num {seq_num}: {e}")

        # Close browser after all operations
        await browser.close()

    # Send the output file to the Telegram chat asynchronously
    try:
        with open(output_file, 'rb') as f:
            future = asyncio.run_coroutine_threadsafe(
                bot.send_document(chat_id=chat_id, document=f),
                loop
            )
            future.result()
    except Exception as e:
        print(f"Failed to send output.txt automatically: {e}")

# Telegram command handlers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Enter server number:', reply_markup=ForceReply(selective=True))
    return SERVER

async def server_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit():
        await update.message.reply_text('Invalid server number.')
        return SERVER
    context.user_data['server_num'] = int(update.message.text)
    await update.message.reply_text('Enter range (start-end):', reply_markup=ForceReply(selective=True))
    return RANGE

async def range_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_range = update.message.text.strip()
    parts = user_range.split('-')
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        await update.message.reply_text('Invalid range format.')
        return RANGE
    start, end = int(parts[0]), int(parts[1])
    if start > end:
        await update.message.reply_text('Start must be <= end.')
        return RANGE
    context.user_data['range_start'] = start
    context.user_data['range_end'] = end
    await update.message.reply_text(f'Starting on server {context.user_data["server_num"]} range {start}-{end}.')

    # Start the run_playwright async function in a separate thread to avoid blocking telegram handlers
    loop = asyncio.get_event_loop()
    threading.Thread(
        target=asyncio.run,
        args=(run_playwright(context.user_data['server_num'], start, end, context.bot, update.effective_chat.id, loop),)
    ).start()

    await update.message.reply_text('Running. Output will be sent here.')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Cancelled.')
    return ConversationHandler.END


# Setup Telegram bot application and handlers

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        SERVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, server_input)],
        RANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, range_input)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

app.add_handler(conv_handler)

# Run bot polling loop
app.run_polling()
