FROM python:3.9-buster

RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

COPY . /app

CMD [ "/bin/bash", "start.sh"]
EXPOSE 5000
EXPOSE 30000