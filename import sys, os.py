import sys, os

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(__file__))

# Importer l'application depuis votre module app
from app import create_app
application = create_app()