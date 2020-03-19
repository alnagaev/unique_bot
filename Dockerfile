FROM python:3
ADD bot.py /
ADD  images.py /
ADD group_dict.json /
RUN pip install pyTelegramBotApi pysocks
CMD [ "python", "./bot.py"]
