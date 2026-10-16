import sys
import os

# Thêm thư mục gốc vào PYTHONPATH để Vercel Serverless Function import được src và main
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from main import app
