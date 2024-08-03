import sys
import datetime
import requests
from bs4 import BeautifulSoup
import csv
from pyrogram import Client
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

CONFIG = {
    "telegram_api_id": int(os.getenv("TG_API_ID")),
    "telegram_hash": os.getenv("TG_API_HASH"),
}

app = Client("my_account", CONFIG["telegram_api_id"], CONFIG["telegram_hash"])

def scrape_web(url, scrape_type):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        if scrape_type == "1":
            data = soup.prettify()
        elif scrape_type == "2":
            data = soup.get_text()
        else:
            data = "Invalid scrape type selected."
        return data
    except requests.RequestException as e:
        return f"Error during web scraping: {e}"

async def scrape_telegram(chat_identifier):
    dataTele = []
    try:
        async with app:
            try:
                chat = await app.get_chat(chat_identifier)
                chat_id = chat.id
                print(f"Chat ID: {chat_id}")
                
                async for message in app.get_chat_history(chat_id):
                    if message.text:
                        dataTele.append(message.text)
            except Exception as e:
                print(f"An error occurred while retrieving chat history: {e}")
    except Exception as e:
        print(f"Error initializing Pyrogram client: {e}")
    return dataTele, chat_id

def save_to_file(data, file_type, chat_id=None):
    try:
        now = datetime.datetime.now()
        if file_type == "1":
            filename = now.strftime("scraped_data_%Y-%m-%d_%H-%M-%S.txt")
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(str(data))
            print(f"Data saved to {filename}")
        elif file_type == "2":
            filename = now.strftime("scraped_data_%Y-%m-%d_%H-%M-%S.csv")
            with open(filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                header = ["Scraped Data"]
                if chat_id:
                    header = [f"Scraped Data for Telegram Chat ID: {chat_id}"]
                writer.writerow(header)
                writer.writerows([[line] for line in data])
            print(f"Data saved to {filename}")
        else:
            print("Invalid file type selected.")
    except IOError as e:
        print(f"Error saving data to file: {e}")

def main():
    while True:
        try:
            print("What do you want to scrape?")
            print("1. Web")
            print("2. Telegram")
            print("3. Exit")
            choice = input("> ").strip().lower()

            if choice == "3":
                print("Exiting the program.")
                break

            if choice == "1":
                url = input("Enter the URL: ")
                print("What do you want to scrape from the web?")
                print("1. Everything")
                print("2. Just text")
                scrape_type = input("> ")
                data = scrape_web(url, scrape_type)
                chat_id = None
            elif choice == "2":
                chat_identifier = input("Enter the chat_id or username: ")
                data, chat_id = asyncio.run(scrape_telegram(chat_identifier))
            else:
                print("Invalid choice.")
                continue

            print("How do you want to save the data?")
            print("1. Text file (.txt)")
            print("2. CSV file (.csv)")
            file_type = input("> ")

            save_to_file(data, file_type, chat_id)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()