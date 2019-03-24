"""seeds for incoming

Revision ID: a9bc32908191
Revises: b750768a21ea
Create Date: 2016-06-08 14:31:19.807116

"""

# revision identifiers, used by Alembic.
revision = 'a9bc32908191'
down_revision = '774059857ba2'
branch_labels = None
depends_on = None

from alembic import op

from media_engine.models import IncomingProvider, IncomingProviderParams
from media_engine.models.seeds.incoming_providers import INCOMING_PROVIDER_LIST


def upgrade():
    incoming_providers = []
    incoming_provider_params = []
    for p in INCOMING_PROVIDER_LIST:
        _id = p.get('id')
        for i in p.pop('params', []):
            i.update(dict(incoming_provider_id=_id))
            incoming_provider_params.append(i)
        incoming_providers.append(p)

    op.bulk_insert(IncomingProvider.__table__, incoming_providers)
    op.bulk_insert(IncomingProviderParams.__table__, incoming_provider_params)


def downgrade():
    op.execute(IncomingProviderParams.__table__.delete())
    op.execute(IncomingProvider.__table__.delete())
