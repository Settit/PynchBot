import socketio
import asyncio
import json
import logging
from logging import DEBUG, INFO, WARN

from bot import Bot
from db import PostgresBotDB
import userlist

logging.basicConfig(level=logging.WARN)
logging.getLogger('engineio').setLevel(WARN)
logging.getLogger('socketio').setLevel(WARN)
logging.getLogger('bot').setLevel(WARN)
logging.getLogger('db').setLevel(DEBUG)
logging.getLogger('userlist').setLevel(WARN)
logging.getLogger('playlist').setLevel(WARN)

with open('config.json') as f: config = json.loads(f.read())

db_config = config['database']


async def main():
    bot = Bot(config['server'], config['channel'], config['username'], config['password'])
    bot.db = PostgresBotDB(bot)
    await bot.db.connect(db_config['username'], db_config['password'], db_config['database'], db_config['host'])
    await bot.start()
    await bot.socket.wait()

asyncio.run(main())
#asyncio.run(main(), debug=True)