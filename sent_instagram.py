from instabot import Bot


ACCOUNT_USERNAME = "life_prescriber"
ACCOUNT_PASSWORD = "Lifeprescriber1234"

# Initialize the bot
bot = Bot()


# Login to your Instagram account
bot.login(username=ACCOUNT_USERNAME, password=ACCOUNT_PASSWORD)

user_id = ["real_lloydfx"]
message = "Instabot really worked"

bot.send_messages(message, user_id)

