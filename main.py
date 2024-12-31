import logging
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Class to store the previous response from OpenAI API
class Reference:
    '''
    A class to store the previous response from the OpenAI API
    '''
    def __init__(self) -> None:
        self.response = ""  # Store the previous response

reference = Reference()
model_name = "gpt-3.5-turbo"

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

def clear_past():
    """Clears the previous conversation context."""
    reference.response = ""  # Clear the previous response

# Default command handler
@dp.message_handler(commands=['start'])
async def command_start_handler(message: types.Message):
    """Handles the '/start' command."""
    await message.reply("Hi\nWelcome to caption Credits @ NITK!!!")

# Clear past conversation handler
@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    """Handles the '/clear' command."""
    clear_past()
    await message.reply("I have cleared the past conversation.")

# Main handler to process user messages
@dp.message_handler()
async def chatgpt(message: types.Message):
    """Processes user input and generates a response using the ChatGPT API."""
    print(f">>> USER: \n\t{message.text}")
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "assistant", "content": reference.response},
                {"role": "user", "content": message.text},
            ]
        )

        # Save the response and send it back to the user
        reference.response = response['choices'][0]['message']['content']
        print(f">>> ChatGPT: \n\t{reference.response}")
        await bot.send_message(chat_id=message.chat.id, text=reference.response)
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await bot.send_message(chat_id=message.chat.id, text="An error occurred. Please try again later.")

# Start polling for messages
if __name__ == "__main__":
    logging.info("Bot started. Waiting for messages...")
    executor.start_polling(dp, skip_updates=True)
