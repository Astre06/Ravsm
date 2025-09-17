import asyncio
import os
from telegram import Update, ForceReply
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import threading
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

TOKEN = "8017025108:AAEN8QkEB66iJxAl3TtA89axtImXL5dETSs"
CHAT_ID = 6679042143
SERVER, RANGE = range(2)

def run_playwright(server_num, range_start, range_end, bot, chat_id, loop):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to True for headless on VPS
        context = browser.new_context()
        page = context.new_page()

        url = "https://my.sonjj.com/login?back=https%3A%2F%2Fsmailpro.com%2F"
        email = "oops-mud-handclasp@duck.com"
        password = "Neljane143"

        # Clear or create output file
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write('')

        try:
            # Navigate to login page
            page.goto(url)

            # Fill email input
            try:
                page.wait_for_selector('input[name="email"]', timeout=10000)
                page.fill('input[name="email"]', email)
            except PlaywrightTimeoutError:
                print("Email input not found within timeout")

            # Fill password input and submit
            try:
                page.wait_for_selector('input[name="password"]', timeout=10000)
                page.fill('input[name="password"]', password)
                page.keyboard.press('Enter')
            except PlaywrightTimeoutError:
                print("Password input not found within timeout")

            # Click login button
            try:
                page.wait_for_selector('.button_primary_mod', timeout=5000)
                page.click('.button_primary_mod')
            except PlaywrightTimeoutError:
                print("Login button not found or not clickable")

            # Click 'Full Access' button
            try:
                page.wait_for_selector("//button[contains(., 'Full Access')]", timeout=500)
                page.click("//button[contains(., 'Full Access')]")
            except PlaywrightTimeoutError:
                print("Full Access button not found or not clickable")

            # Initial batch generation with seq_num=1
            seq_num = 1

            try:
                # Click 'Create' button
                page.wait_for_selector("//div[contains(@class, 'sm:block') and text()='Create']", timeout=5000)
                page.click("//div[contains(@class, 'sm:block') and text()='Create']")

                # Click 'Google'
                page.wait_for_selector("//span[text()='Google']", timeout=5000)
                page.click("//span[text()='Google']")

                # Click 'Sequential'
                page.wait_for_selector("//span[text()='Sequential']", timeout=5000)
                page.click("//span[text()='Sequential']")
                time.sleep(0.5)

                # Input sequential number '1'
                page.wait_for_selector("//input[@type='number']", timeout=5000)
                seq_input = page.locator("//input[@type='number']")
                seq_input.click()
                seq_input.fill(str(seq_num))

                # Click 'Real Account'
                page.wait_for_selector("//span[text()='Real Account']", timeout=5000)
                page.click("//span[text()='Real Account']")

                # Select server dropdown and option
                page.wait_for_selector("//select", timeout=5000)
                page.select_option("select", str(server_num))

                time.sleep(10)  # Wait for server processing or page updates

                # Click 'Generate' button
                page.wait_for_selector("//button[contains(., 'Generate')]", timeout=5000)
                page.click("//button[contains(., 'Generate')]")

                # Wait for email with '@gmail.com' to appear
                page.wait_for_selector("//div[contains(text(), '@gmail.com')]", timeout=5000)

                print(f"Generated batch with sequential number {seq_num}")
            except PlaywrightTimeoutError as e:
                print(f"Error during first generation: {e}")

            # Continue generating for user-defined range from range_start to range_end
            seq_num = range_start
            max_seq = range_end

            while seq_num <= max_seq:
                try:
                    # Click 'Create' button
                    page.wait_for_selector("//div[contains(@class, 'sm:block') and text()='Create']", timeout=5000)
                    page.click("//div[contains(@class, 'sm:block') and text()='Create']")

                    # Fill sequence input with seq_num
                    page.wait_for_selector("//input[@type='number']", timeout=5000)
                    seq_input = page.locator("//input[@type='number']")
                    seq_input.click()
                    seq_input.fill(str(seq_num))

                    # Click 'Generate' button
                    page.wait_for_selector("//button[contains(., 'Generate')]", timeout=5000)
                    page.click("//button[contains(., 'Generate')]")

                    time.sleep(5)  # Wait for generation to process

                    # Extract generated email text element
                    page.wait_for_selector("//div[contains(@class, 'text-sm') and contains(@class, 'text-gray-500') and contains(@class, 'truncate')]", timeout=500)
                    email_element = page.locator("//div[contains(@class, 'text-sm') and contains(@class, 'text-gray-500') and contains(@class, 'truncate')]").first
                    email_address = email_element.inner_text().strip()

                    # Append to output file
                    with open('output.txt', 'a', encoding='utf-8') as f:
                        f.write(email_address + '\n')

                    print(f"Extracted email {email_address} saved for sequential number {seq_num}")

                    # Delete generated items (trash buttons) loop
                    while True:
                        trash_buttons = page.locator("//button[contains(@class, 'bg-red-400') and contains(@class, 'rounded-full')]").all()
                        if not trash_buttons:
                            break
                        trash_buttons[0].click()
                        time.sleep(1)
                        try:
                            modal_delete_btn = page.wait_for_selector("//button[contains(@class, 'bg-red-500') and text()='Delete']", timeout=5000)
                            modal_delete_btn.click()
                            time.sleep(1)
                        except PlaywrightTimeoutError:
                            break

                    seq_num += 1
                except Exception as e:
                    print(f"Error in iteration for seq_num {seq_num}: {e}")
                    seq_num += 1

        except Exception as e:
            print(f"Error during Playwright automation: {e}")

        browser.close()

        # Send the output.txt file asynchronously in the bot's event loop
        try:
            with open('output.txt', 'rb') as f:
                future = asyncio.run_coroutine_threadsafe(
                    bot.send_document(chat_id=chat_id, document=f),
                    loop
                )
                future.result()  # Wait for completion and raise exceptions if any
        except Exception as e:
            print(f"Failed to send output.txt automatically: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please enter a server number (e.g., 1,2,3,4):', reply_markup=ForceReply(selective=True))
    return SERVER

async def server_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    server_num = update.message.text.strip()
    if not server_num.isdigit():
        await update.message.reply_text('Please enter a valid server number.')
        return SERVER
    context.user_data['server_num'] = int(server_num)
    await update.message.reply_text('Please input range (e.g., 1-890):', reply_markup=ForceReply(selective=True))
    return RANGE

async def range_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_range = update.message.text.strip()
    if '-' not in user_range:
        await update.message.reply_text('Please enter range in format start-end (e.g., 1-890).')
        return RANGE
    parts = user_range.split('-')
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        await update.message.reply_text('Invalid range format. Use start-end (e.g., 1-890).')
        return RANGE
    start, end = int(parts[0]), int(parts[1])
    if start > end:
        await update.message.reply_text('Range start should be less than or equal to end.')
        return RANGE
    context.user_data['range_start'] = start
    context.user_data['range_end'] = end
    await update.message.reply_text(f'Starting generation on server {context.user_data["server_num"]} for range {start}-{end}.')

    loop = asyncio.get_event_loop()
    threading.Thread(target=run_playwright, args=(
        context.user_data['server_num'], start, end,
        context.bot, update.effective_chat.id, loop)).start()

    await update.message.reply_text('Running. You will receive the output.txt file here when done.')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

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
app.run_polling()


