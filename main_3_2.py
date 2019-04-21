'''
using discord.py version 1.0.0a
'''
import discord
import asyncio
import re

BOT_OWNER_ROLE = 'admin' # change to what you need
#BOT_OWNER_ROLE_ID = "544387608378343446"
lock = asyncio.Lock()

answer_scores = {
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 0
}
answer_scores_last = {
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 0
}

oot_channel_id_list = [
    "538176524470190090",
    "516780082619088905",
    "523360037067030530",
	"514915043796713482",
	"496855838703616032",
	"532833017706577930",
	"544381529829146645",
    "558136902885048329",
    "559442345674670082" #test channel (zlex)
]

apgscore = 150
nomarkscore = 80
markscore = 40

async def update_scores(content):
    global answer
    global answer_scores
    global answer_scores_last

    if re.match(r'(not)?[1-4](\?)?(apg)?',content) is None:
        return False

    async with lock:
        if content == "1":
            answer_scores["1"] += nomarkscore
        elif content == "2":
            answer_scores["2"] += nomarkscore
        elif content == "3":
            answer_scores["3"] += nomarkscore
        elif content == "4":
            answer_scores["4"] += nomarkscore
        elif content.startswith("1?") or content.startswith("1apg?"):
            answer_scores["1"] += markscore
        elif content.startswith("2?") or content.startswith("2apg?"):
            answer_scores["2"] += markscore
        elif content.startswith("3?") or content.startswith("3apg?"):
            answer_scores["3"] += markscore
        elif content.startswith("4?") or content.startswith("4apg?"):
            answer_scores["4"] += markscore
        elif content == "1apg":
            answer_scores["1"] += apgscore
        elif content == "2apg":
            answer_scores["2"] += apgscore
        elif content == "3apg":
            answer_scores["3"] += apgscore
        elif content == "4apg":
            answer_scores["4"] += apgscore
        elif content in ["not1", "n1"]:
            answer_scores["1"] -= nomarkscore
        elif content in ["not2", "n2"]:
            answer_scores["2"] -= nomarkscore
        elif content in ["not3", "n3"]:
            answer_scores["3"] -= nomarkscore
        elif content in ["not4", "n4"]:
            answer_scores["4"] -= nomarkscore
        elif content.startswith("not1?") or content.startswith("n1?"):
            answer_scores["1"] -= markscore
        elif content.startswith("not2?") or content.startswith("n2?"):
            answer_scores["2"] -= markscore
        elif content.startswith("not3?") or content.startswith("n3?"):
            answer_scores["3"] -= markscore
        elif content.startswith("not4?") or content.startswith("n4?"):
            answer_scores["4"] -= markscore

        allanswers = answer_scores.values()
        highest = max(allanswers)
        answer = list(allanswers).index(highest)+1
        answer_scores_last = answer_scores.copy()

    return True

class SelfBot(discord.Client):

    def __init__(self, main_bot):
        super().__init__()
        if 'update_embeds' in dir(main_bot):
            self.main_bot = main_bot
        else:
            self.main_bot = None

    async def on_ready(self):
        print("======================")
        print("Self Bot")
        print("Connected to discord.")
        print("User: " + self.user.name)
        print("ID: " + str(self.user.id))

    async def on_message(self, message):
        global oot_channel_id_list
        if message.guild == None:
            return
        if str(message.channel.id) in oot_channel_id_list:
            content = message.content.lower().replace(' ', '').replace("'", "")
            updated = await update_scores(content)
            if updated and self.main_bot is not None:
                print('selfbot: external score update')
                await self.main_bot.update_embeds()

class Bot(discord.Client):

    def __init__(self):
        super().__init__()
        self.bot_channel_id_list = []
        self.embed_msg = None
        self.embed_channel_id = None

    async def clear_results(self):
        global answer
        global answer_scores
        global answer_scores_last

        answer_scores = {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0
        }

        answer_scores_last = answer_scores.copy()
        answer = ""

    async def update_embeds(self):
        global answer
        global answer_scores

        one_check = ""
        two_check = ""
        three_check = ""
        four_check = ""

        if answer == 1:
            one_check = " :white_check_mark:"
        if answer == 2:
            two_check = " :white_check_mark:"
        if answer == 3:
            three_check = " :white_check_mark:"
        if answer == 4:
            four_check = " :white_check_mark:"

        self.embed=discord.Embed(title=" ", description="", color=0xadd8e6 )
        self.embed.add_field(name="A", value=f"{answer_scores['1']}.0{one_check}", inline=False)
        self.embed.add_field(name="B", value=f"{answer_scores['2']}.0{two_check}", inline=False)
        self.embed.add_field(name="C", value=f"{answer_scores['3']}.0{three_check}", inline=False)
        self.embed.add_field(name="D", value=f"{answer_scores['4']}.0{four_check}", inline=False)
        self.embed.set_footer(text=f" ", icon_url="")

        if self.embed_msg is not None:
            await self.edit_embed(self.embed_msg, self.embed)

    async def on_ready(self):
        print("==============")
        print("trivia")
        print("Connected to discord.")
        print("User: " + bot.user.name)
        print("ID: " + str(bot.user.id))

        await self.clear_results()
        await self.update_embeds()

    async def send_embed(self, channel, embed):
        return await channel.send('', embed=embed)

    async def edit_embed(self, old_embed, new_embed):
        return await old_embed.edit(embed=new_embed)

    async def on_message(self, message):
        global answer
        global answer_scores
        global answer_scores_last

        # if message is private
        if message.author == self.user or message.guild == None:
            return

        if message.content.lower() == "-lo":
            if BOT_OWNER_ROLE in [role.name for role in message.author.roles]:
                self.embed_msg = None
                await self.clear_results()
                await self.update_embeds()
                self.embed_msg = \
                    await self.send_embed(message.channel,self.embed)
                self.embed_channel_id = message.channel.id
                print(self.embed_channel_id)
            else:
                await message.add_reaction(emoji='❌')
            return

        # process votes
        if message.channel.id == self.embed_channel_id:
            content = message.content.lower().replace(' ', '').replace("'", "")
            updated = await update_scores(content)
            if updated:
                await self.update_embeds()

if __name__ == '__main__':
    bot = Bot()
    selfbot = SelfBot(bot)

    loop = asyncio.get_event_loop()
    task1 = loop.create_task(bot.start(" "))
    task2 = loop.create_task(selfbot.start(" ", bot=False))
    keep_alive()
    gathered = asyncio.gather(task1, task2, loop=loop)
    loop.run_until_complete(gathered)
