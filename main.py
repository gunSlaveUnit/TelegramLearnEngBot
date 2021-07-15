import logging

from bot import Bot

try:
    import settings
except ImportError:
    import settings_default as settings
    exit('Rename settings_default.py to settings.py and set TOKEN')

logger = logging.getLogger(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


if __name__ == '__main__':
    bot = Bot(token=settings.TOKEN)
    bot.run()
