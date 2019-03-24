from media_engine.models import m_session
from media_engine.helper import get_worker_logger
from media_engine.api_models.product import GlobalProductPrice
from media_engine.api_models import oa_session
from media_engine.models.common import CountryInfo

logger = get_worker_logger('worker')


def load_global_product_dict():
    logger.debug("Inside load_global_product_dict")
    record_tup = oa_session.query(GlobalProductPrice).filter().all()  # fetch all records from table

    logger.debug("Record Tuple : {}".format(record_tup))

    product_dict = {
        (x.product_id, x.country_code): (x.price, x.custom_product_id)
        for x in record_tup
    }

    logger.debug("Record from Dict : {} ".format(product_dict))
    return product_dict


global_product_obj_dict = load_global_product_dict()


def get_countryinfo_by_id():
    # dict = {1 : 'US',
    #         91 : 'IN',
    #         61 : 'AU'}

    logger.debug("Inside get_countryinfo_by_id")
    record_tup = m_session.query(CountryInfo).filter().with_entities(CountryInfo.char_code,
                                                                     CountryInfo.code).all()  # fetch all records from table
    return {x.code: x.char_code for x in record_tup}


get_countryinfo_by_id_obj = get_countryinfo_by_id()


def get_countryinfo_by_name():
    # dict = {
    #     'AUS' : 61,
    #     'IN' : 91,
    #     'US' : 1
    # }

    logger.debug("Inside get_countryinfo_by_name")
    record_tup = m_session.query(CountryInfo).filter().with_entities(CountryInfo.char_code,
                                                                     CountryInfo.code).all()  # fetch all records from table
    return {x.char_code: x.code for x in record_tup}


get_countryinfo_by_name_obj = get_countryinfo_by_name()
