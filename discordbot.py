import discord
import asyncio
import json
import datetime as dt

with open('config.json') as f: CONFIG = json.loads(f.read())

class DiscordClient(discord.Client):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.last_deleted_uid = None

    async def start(self):
        await super().start(CONFIG['discord']['token'])

    async def on_ready(self):
        self.del_vids_channel = self.get_channel(CONFIG['discord']['deleted-vids-channel'])
        self.bot.on('delete', self.handle_vid_delete)
        self.bot.on('chatMsg', self.handle_chatMsg)
        #await self.del_vids_channel.send('ready')

    async def handle_vid_delete(self, data):
        self.last_deleted_uid = data['uid']

    async def handle_chatMsg(self, data):
        #on bot event 'chatMsg'
        if data['msg'].split(' ', 1)[0] != 'deleted': return
        try:
            if data['meta']['action'] != True or data['meta']['addClass'] != 'action': return
        except KeyError: return

        title = data['msg'].split('"', 1)[1].rsplit('"', 1)[0]

        async with self.bot.db.lock:
            async with self.bot.db.db.transaction():
                x = await self.bot.db.db.fetch("""select videos.type, videos.id, videos.title, video_adds.from_username
                    from videos
                    inner join video_adds
                    on videos.id = video_adds.video_id and videos.type = video_adds.video_type
                    /*where videos.title = $1*/
                    where videos.title = $1
                    order by video_adds.timestamp desc limit 1
                    """, 
                    title
                )
        print(x)
        x = x[0]
        embed = discord.Embed()
        embed.title = title
        embed.type = 'rich'
        embed.set_author(name='Video deleted')
        embed.color = 0xFF6666
        embed.add_field(name='Posted by', value=x['from_username'])
        embed.add_field(name='Deleted by', value=data['username'])

        if x['type'] == 'yt':
            embed.description = 'https://youtu.be/' + x['id']

        await self.del_vids_channel.send(embed=embed)