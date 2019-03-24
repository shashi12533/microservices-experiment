"""added seeds

Revision ID: b750768a21ea
Revises: 6562cf173496
Create Date: 2016-05-27 22:31:18.115347

"""

# revision identifiers, used by Alembic.
from media_engine.api_models import Currency
from media_engine.models import CountryInfo, ServiceProviderParam
from media_engine.models import ServiceProvider
from media_engine.models.seeds.countries import COUNTRY_LIST
from media_engine.models.seeds.currencies import CURRENCY_LIST
from media_engine.models.seeds.service_providers import SERVICE_PROVIDER_LIST

revision = 'b750768a21ea'
down_revision = '6562cf173496'
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.bulk_insert(Currency.__table__, CURRENCY_LIST)
    op.bulk_insert(CountryInfo.__table__, COUNTRY_LIST)

    providers_list = []
    params_list = []
    for provider in SERVICE_PROVIDER_LIST:
        _id = provider.get('id')
        params = provider.pop('provider_params', None)

        providers_list.append(provider)
        for x in params:
            x['service_provider_id'] = _id
            params_list.append(x)
    op.bulk_insert(ServiceProvider.__table__, providers_list)
    op.bulk_insert(ServiceProviderParam.__table__, params_list)


def downgrade():
    op.execute(ServiceProviderParam.__table__.delete())
    op.execute(ServiceProvider.__table__.delete())
    op.execute(CountryInfo.__table__.delete())
    op.execute(Currency.__table__.delete())
