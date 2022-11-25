FROM python:3.6.4-slim
COPY . /server
CMD ["python","/server/server.py"]
EXPOSE 5040-5041