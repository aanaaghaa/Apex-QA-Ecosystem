import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from ..state import QAState

load_dotenv()