import os
import sys  # ✅ ДОБАВЬ ЭТУ СТРОКУ

# Добавляем путь к корневой папке
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paradise.settings')

application = get_wsgi_application()