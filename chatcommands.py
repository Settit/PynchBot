import random
from collections import defaultdict
import datetime as dt

class ChatCommand:
    def __init__(self, bot):
        self.bot = bot
        self.command_name = '' #e.g. $roll
        self.min_rank = 1
        self.user_cooldown = dt.timedelta(seconds=0)
        self.global_cooldown = dt.timedelta(seconds=0)
        self.last_uses = defaultdict(lambda: dt.datetime.fromtimestamp(0))
        self.last_global_use = dt.datetime.fromtimestamp(0)

    async def __call__(self, *args, **kwargs): return await self.on_chat_message(*args, **kwargs)

    async def on_chat_message(self, data):
        if not self.check(data): return
        if await self.command(data):
            self.update_cooldowns(data)

    def check(self, data):
        msg = data['msg']
        name = data['username'].lower()
        args = msg.split(' ')
        if args[0].lower() != self.command_name.lower(): return False
        if self.bot.userlist.get_user_by_name(name).rank < self.min_rank: return False
        if not dt.datetime.now() - self.last_global_use > self.global_cooldown: return False
        if not dt.datetime.now() - self.last_uses[name] > self.user_cooldown: return False
        return True

    def update_cooldowns(self, data):
        name = data['username'].lower()
        self.last_global_use = dt.datetime.now()
        self.last_uses[name.lower()] = dt.datetime.now()

    async def command(self, data):
        #should return true or false, indicating whether cooldown should be triggered
        return True

class QuoteCommand(ChatCommand):
    def __init__(self, bot):
        super().__init__(bot)
        self.command_name = '$quote'

    async def command(self, data):
        quotes = await self.bot.db.get_quote(data['username'])
        try: q_name, q_msg, q_time = quotes[0][0], quotes[0][1], quotes[0][2]
        except IndexError: return False
        q_time = dt.datetime.fromtimestamp(q_time / 1000).strftime("%m/%d/%Y %H:%M:%S")
        quote = f'[{q_name} {q_time}] {q_msg}'
        await self.bot.send_chat_message(quote)
        return True

class RollCommand(ChatCommand):
    def __init__(self, bot):
        super().__init__(bot)
        self.command_name = '$roll'
        self.min_rank = 3

    async def command(self, data):
        args = data['msg'].split(' ')

        if data['username'].lower() == 'RookieMcSpooks'.lower() or data['username'].lower() == 'Gigago'.lower():
            await self.bot.send_chat_message('Fuck ' + data['username'])
            return True

        size = None
        print(args)
        try:
            size = int(args[1])
        except (ValueError, IndexError): pass
        if size is None or size < 0 or size > 100: size = 2

        result = random.randint(0, 10**size - 1)
        result = str(result).zfill(size)

        rev_result = result[::-1]
        consec = 1
        for i in range(1, len(rev_result)):
            if rev_result[i-1] != rev_result[i]: break
            consec += 1

        msg = data['username'] + ' rolled: ' + result
        if consec > 1: msg = '[3d]' + msg + '[/3d] /go'

        await self.bot.send_chat_message(msg)
        return True