FROM python:3.9-buster

RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
EXPOSE 5000