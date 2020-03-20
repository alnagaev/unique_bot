FROM python:3
ADD bot.py /
ADD  images.py /
ADD group_dict.json /
RUN pip install -r requirements.txt
CMD [ "python", "./bot.py"]
