# test_main.py
from lecture_4.demo_service.api.main import create_app


def test_create_app():
    app = create_app()
    assert app.title == "Testing Demo Service"
