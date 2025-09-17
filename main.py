import asyncio
import os
from telegram import Update, ForceReply
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

TOKEN = "8017025108:AAEN8QkEB66iJxAl3TtA89axtImXL5dETSs"
CHAT_ID = 6679042143

SERVER, RANGE = range(2)

chrome_driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver.exe")

def run_selenium(server_num, range_start, range_end, bot, chat_id, loop):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for VPS headless mode
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    url = "https://my.sonjj.com/login?back=https%3A%2F%2Fsmailpro.com%2F"
    email = "oops-mud-handclasp@duck.com"
    password = "Neljane143"
    
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write('')  # Clear previous content

    try:
        driver.get(url)
    except Exception as e:
        print(f"Failed to load URL: {e}")

    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.clear()
        email_input.send_keys(email)
    except Exception as e:
        print(f"Email input not found: {e}")

    try:
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.clear()
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"Password input error: {e}")

    try:
        login_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "button_primary_mod"))
        )
        login_button.click()
    except Exception as e:
        print(f"Login button error: {e}")

    try:
        full_access_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Full Access')]"))
        )
        full_access_button.click()
    except Exception as e:
        print(f"Full Access button error: {e}")

    # Initial run with default seq_num = 1 and user-defined server_num
    seq_num = 1
    try:
        create_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sm:block') and text()='Create']"))
        )
        create_button.click()
        google_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Google']"))
        )
        google_button.click()
        sequential_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Sequential']"))
        )
        sequential_button.click()
        time.sleep(0.5)
        seq_number_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='number']"))
        )
        seq_number_input.click()
        seq_number_input.send_keys(Keys.CONTROL + 'a')
        seq_number_input.send_keys(str(seq_num))
        real_acc_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Real Account']"))
        )
        real_acc_button.click()
        server_dropdown = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//select"))
        )
        server_dropdown.click()
        option_xpath = f"//option[@value='{server_num}']"
        option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        option.click()
        time.sleep(10)
        generate_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Generate')]"))
        )
        generate_button.click()
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), '@gmail.com')]"))
        )
        print(f"Generated batch with sequential number {seq_num}")
    except Exception as e:
        print(f"Error during first generation: {e}")

    # Continue with user range
    seq_num = range_start
    max_seq = range_end
    while seq_num <= max_seq:
        try:
            create_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sm:block') and text()='Create']"))
            )
            create_button.click()
            seq_number_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='number']"))
            )
            seq_number_input.click()
            seq_number_input.send_keys(Keys.CONTROL + 'a')
            seq_number_input.send_keys(str(seq_num))
            generate_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Generate')]"))
            )
            generate_button.click()
            time.sleep(5)
            email_text_elem = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'text-sm') and contains(@class, 'text-gray-500') and contains(@class, 'truncate')]"))
            )
            email_address = email_text_elem.text.strip()
            with open('output.txt', 'a', encoding='utf-8') as f:
                f.write(email_address + '\n')
            print(f"Extracted email {email_address} saved for sequential number {seq_num}")
            while True:
                try:
                    trash_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'bg-red-400') and contains(@class, 'rounded-full')]")
                    if not trash_buttons:
                        break
                    driver.execute_script("arguments[0].click();", trash_buttons[0])
                    time.sleep(1)
                    modal_delete_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'bg-red-500') and text()='Delete']"))
                    )
                    modal_delete_btn.click()
                    time.sleep(1)
                except StaleElementReferenceException:
                    time.sleep(1)
                    continue
                except TimeoutException:
                    break
            seq_num += 1
        except Exception as e:
            print(f"Error in iteration for seq_num {seq_num}: {e}")
            seq_num += 1
    print("Job done. Browser will stay open waiting for new commands...")

    # Wait without closing the browser
    try:
        while True:
            time.sleep(10)  # or implement actual waiting for commands
    except KeyboardInterrupt:
        print("Exiting and closing browser")
        driver.quit()

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
    threading.Thread(target=run_selenium, args=(context.user_data['server_num'], start, end, context.bot, update.effective_chat.id, loop)).start()

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
