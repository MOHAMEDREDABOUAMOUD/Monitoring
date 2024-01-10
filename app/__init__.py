from flask import Flask
from config import Config
from app.controller import app

app.config.from_object(Config)
