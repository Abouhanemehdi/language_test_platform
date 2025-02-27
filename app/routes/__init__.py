from app.routes.auth import bp as auth_bp
from app.routes.admin import bp as admin_bp
from app.routes.test import bp as test_bp
from app.routes.main import bp as main_bp

__all__ = ['auth_bp', 'admin_bp', 'test_bp', 'main_bp']