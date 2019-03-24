from media_engine.api_models import oa_session, ExchangeRate
from media_engine.lib.validators import not_empty


def get_exchange_rate(**kwargs):
    return oa_session.query(ExchangeRate.exchange_rate) \
        .filter(ExchangeRate.currency_code == kwargs['currency_code'], ExchangeRate.is_active == 1).first()[0]


@not_empty('from_currency', err_code='CONVERT-NULL-FROM-CURRENCY', req=True)
@not_empty('to_currency', err_code='CONVERT-NULL-TO-CURRENCY', req=True)
@not_empty('value', err_code='CONVERT-NULL-VALUE', req=True, var_type=float)
def convert_currency(from_currency=None, to_currency=None,  value=None):
    if from_currency == to_currency:
        return value
    exchange_rate_of_from_currency_wrt_usd = get_exchange_rate(currency_code=from_currency)
    exchange_rate_of_to_currency_wrt_usd = get_exchange_rate(currency_code=to_currency)
    new_value = (value / exchange_rate_of_from_currency_wrt_usd) * exchange_rate_of_to_currency_wrt_usd
    return new_value
