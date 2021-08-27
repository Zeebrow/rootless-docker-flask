FROM python:3.8-slim-buster

WORKDIR app
COPY . .

RUN pip install --no-cache-dir --root -r requirements.txt

# user comes after pip install, because permissions
# the app will run but os.getuid() errors out, saying 
# 'no such user 1001'
USER 1001:1001

ENV FLASK_APP=simpleflask

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
