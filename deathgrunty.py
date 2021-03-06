import discord
import argparse
import logging
import gruntyplugins
import time
import json
import sys

br = gruntyplugins.GruntyPlugins

# argparse setup for commandline args
parser = argparse.ArgumentParser()
parser.add_argument("-1","--loglevel",
                    help="Choose logging level: DEBUG INFO WARNING ERROR CRITICAL",
                    defaul="DEBUG",
                    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
parser.add_argument("-f", "--filename",
                    help="file to log to, default is 'grunty.log'",
                    default="grunty.log")
args = parser.parse_args()

# setup logging
logger = logging.getLogger("gruntylog")
formater = logging.Formatter(fmt='%(asctime)s %(message)s',
                             datefmt='%d/%m/%Y %I:%M:%S %p')
logger.setLevel(logging.DEBUG)
#file handler for logging
fh = logging.FileHandler(args.filename)
fh.setLevel("DEBUG")
# console handler for logging
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(args.loglevel)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

class DeathGrunty(discord.Client, br):

    def __init__(self):
        self.logger = logging.getLogger("gruntylog")
        self.fdb = self.getjson("factoids.json")
        self.qdb = self.getjetson("quots.json")
        self.rdb = self.getjson("reactions.json")
        self.bands = self.getjson("bands.json")
        self.writejson("msicdata.json")
        br.__init__(self)
        super().__init__()


    def cleanup(self):
        self.logger.info("cleaning up")
        self.writejson("factoids.json", self.fdb)
        self.writejson("reactions.json", self.rdb)
        self.writejson("quotes.json", self.qdb)
        self.writejson("bands.json", self.bands)
        self.writejson("miscdata.json", self.miscdata)

    async def on_ready(self):
        self.logger.info("logged in as")
        self.logger.info(self.user.name)
        self.logger.info(self.user.id)
        self.logger.info('-------')

    async def on_message(self, message, num=10):

        if message.author == self.user:
            return
        self.logger.info("Received message: '{}'".format(message.content))
        await self.get_response(message)

    async def safe_send_message(self, dest, content):
        msg = None
        try:
            await self.send_typing(dest)
            time.sleep(1)
            self.logger.info("Sending '{}' to {}".format(content, str(dest)))
            msg = await self.send_message(dest, content)
            return msg
        except:
            self.logger.info("nope")

    async def safe_send_file(self, dest, content):
        msg = None
        try:
            msg = await self.send_file(dest, content)
            return msg
        except:
            self.logger.info("Nada")

    async def safe_add_reaction(self, message, content):
        try:
            msg = await self.add_reaction(message, content)
            return msg
        except:
            self.logger.info("no way")

    async def guru_meditation(self, message, error):
        await self.safe_send_file(message.channel, "Guru_meditation.gif")
        await self.safe_send_message(message.channel, error)

    def writejson(self, path, jd):
        with open(path, 'w') as outfile:
            json.dump(jd, outfile, indent=2, sort_keys=True, separators=(',', ':'))

    def getjson(self, path):
        with open(path) as fn:
            jd = json.load(fn)
        return jd

# open secrets file for API token and start the bot
with open("SECRETS.yaml", 'r') as filein:
    secrets = yaml.load(filein)
bot = DeathGrunty()
bot.run(secrets["token"])

# make sure things get saved to file
@atexit.register
def save_stuff():
    bot.cleanup()

                               
