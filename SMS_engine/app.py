
from flask import Flask
from media_engine.config import get_config
from media_engine.resources import create_restful_api
from media_engine.models import m_session
from media_engine.api_models import oa_session


def create_app(**kwargs):
    config = get_config()

    app = Flask(config.FLASK_APP_NAME)

    app.config.from_object(config)

    if kwargs.get('rest'):
        create_restful_api(app)

    def close_session(response_or_exc):
        m_session.remove()
        oa_session.remove()
        return response_or_exc
    app.teardown_appcontext(close_session)
    return app

if __name__ == '__main__':
    app = create_app(rest=True)
    app.run(port=9184, debug=True, host='0.0.0.0')

