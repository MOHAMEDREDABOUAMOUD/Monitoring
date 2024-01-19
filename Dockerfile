FROM python
WORKDIR /app
COPY . /app
RUN pip install -r requirement.txt
EXPOSE 8080
ENTRYPOINT [ "python3" ]
CMD [ "run.py" ]