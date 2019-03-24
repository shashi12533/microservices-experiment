#!/usr/bin/env python
# -*- coding: utf-8 -*-
from media_engine.helper import get_worker_logger
from media_engine.lib.errors import NotFoundError, LabelNotActiveError, \
    InsufficientBalanceError, ProductNotFoundError, LabelNotFound, InvalidCountryForProduct, InvalidMobileNumberError
from media_engine.models import m_session, Label, CountryInfo
from media_engine.product import Product
from media_engine.models.provider import DefaultProduct
from media_engine.api_models.models import Customer
from media_engine.lib.common import normalize_number
from media_engine.lib.global_product_list import load_global_product_dict, global_product_obj_dict
from media_engine.models.provider import ServiceProvider, ServiceProviderConfig
from media_engine.lib.accounting import get_provider_params, get_provider_dynamically, get_product_details
from media_engine.api_models import oa_session
from media_engine.lib.global_product_list import get_countryinfo_by_id, get_countryinfo_by_name, \
    get_countryinfo_by_id_obj, get_countryinfo_by_name_obj
from media_engine.api_models.product import Product as ProductModel
from media_engine.api_models.merchant import Merchant
from sqlalchemy import or_

logger = get_worker_logger('worker')


def get_product(account_id=None, label=None, country_code=None, sender_id=None, mobile_number=None):
    logger.info("get_product :: account_id = {} and label = {}".format(
        account_id, label))
    is_global = False

    if label is not None:  # if label is present
        logger.debug("Label is present in given request")
        label_obj = m_session.query(Label).filter(
            Label.account_id == account_id,
            Label.label == label,
            Label.is_active == 1,
            Label.deleted_on.is_(None)
        )

        label_obj = label_obj.first()

        if label_obj is not None:
            logger.debug("label object is present")
            product_id = label_obj.product_id

            product_obj = Product(account_id, product_id)
            check_balance = product_obj.check_balance()
            logger.debug("check-balance : {}".format(check_balance))
            if check_balance==False:
                raise InsufficientBalanceError
            # Get international mobile number

            if country_code is None:
                logger.debug("Country is None")
                # todo: use country_id
                country = label_obj.country
                if country.code:
                    country_code = country.code
                    logger.debug("With Label sending SMS country code : {}".format(country_code))
                    formatted_mobile_number = normalize_number(
                        mobile_number,
                        country_code
                    )
                    if formatted_mobile_number is None:
                        raise InvalidMobileNumberError(mobile_number)

                    logger.debug("Country Code from Label : {}".format(country_code))
                else:
                    logger.debug("Global Product with Label : Sending SMS")
                    customer_country_obj = oa_session.query(Customer).filter(
                        Customer.account_id == account_id
                    ).with_entities(
                        Customer.country_code
                    ).first()
                    country_code = customer_country_obj.country_code

                    # get_countryinfo_by_id_obj = get_countryinfo_by_name()
                    # get_countryinfo_by_id_obj

                    try:
                        country_id = get_countryinfo_by_name_obj[country_code]
                    except Exception as e:
                        raise InvalidCountryForProduct

                    formatted_mobile_number = normalize_number(
                        mobile_number,
                        country_id
                    )
                    if formatted_mobile_number is None:
                        raise InvalidMobileNumberError(mobile_number)
                    logger.debug("Country Code from Customer : {}".format(country_code))
            else:
                logger.debug("Found Product from Label and country is also present")
                formatted_mobile_number = mobile_number

        else:
            raise LabelNotFound()
    else:
        logger.debug("Label is Not present in given request")
        if country_code is None:
            logger.debug("Label is None and Country Code is None")
            product_id, formatted_mobile_number, country_code, is_global = _get_default_product_no_country(account_id,
                                                                                                           sender_id,
                                                                                                           country_code,
                                                                                                           mobile_number)
        else:
            logger.debug("Label is None and Country Code : {}".format(country_code))
            product_id, formatted_mobile_number, country_code, is_global = _get_default_product(account_id, sender_id,
                                                                                                country_code,
                                                                                                mobile_number)

    if product_id is None:
        logger.debug("Something is wrong : did not received the Product Id")
        return None

    logger.debug("Finally we got the product with Product ID : {}".format(product_id))
    product = Product(account_id, product_id)
    logger.info("get_product :: product = {}".format(product.id))
    logger.info("get_product :: product Details = {}".format(product))
    product.formatted_mobile_number = formatted_mobile_number

    product_country_code = get_countryinfo_by_name_obj.get(product.country_code)

    if product.country_code == "OG":
        is_global = True

    elif product_country_code != country_code:
        logger.error(
            "Product Country : {0} and Mobile Country : {1} are different".format(product_country_code, country_code))
        raise InvalidCountryForProduct()

    product.is_global = is_global
    if is_global:
        product.customer_country_code = get_countryinfo_by_id_obj.get(country_code)

    return product


def _get_default_product(account_id=None, sender_id=None, country_code=None,
                         mobile_number=None):
    subtype = len(sender_id)
    check_balance = False
    if (subtype < 7):
        subtype = "short_code"
    else:
        subtype = "long_code"

    logger.debug("Subtype  : {}".format(subtype))


    logger.debug("COuntry Code : {}".format(country_code))

    try:
        if country_code.isdigit():
            #country_code = get_countryinfo_by_id_obj[country_code]
            try:
                country_code = get_countryinfo_by_id_obj[country_code]
            except Exception as e:
                raise InvalidCountryForProduct
        else:
            pass
    except Exception as e:
        #country_code = get_countryinfo_by_id_obj[country_code]
        try:
            country_code = get_countryinfo_by_id_obj[country_code]
        except Exception as e:
            raise InvalidCountryForProduct

    logger.debug("COuntry Code : {}".format(country_code))

    default_product_obj = m_session.query(DefaultProduct).filter(
        DefaultProduct.account_id == account_id,
        or_(DefaultProduct.subtype == subtype, DefaultProduct.subtype == 'one_way'),
        DefaultProduct.is_active == 1,
        DefaultProduct.country_code == country_code
    ).with_entities(
        DefaultProduct.product_id, DefaultProduct.country_code, DefaultProduct.account_id
    ).all()

    # logger.debug("COuntry COde :: account_id : {}".format(country_code))
    if default_product_obj:
        default_product_obj, check_balance = _check_product_price(default_product_obj)

    if not default_product_obj or not check_balance:  # if product not found or else check balance is False
        default_product_obj = m_session.query(DefaultProduct).filter(
            DefaultProduct.account_id == account_id,
            DefaultProduct.is_active == 1,
            DefaultProduct.country_code == "OG"
        ).with_entities(
            DefaultProduct.product_id, DefaultProduct.country_code, DefaultProduct.account_id
        ).all()

        if default_product_obj:
            default_product_obj, check_balance = _check_product_price(default_product_obj)

        if default_product_obj and check_balance:
            return (default_product_obj.product_id, mobile_number,
                    country_code, True)
        else:
            if check_balance:
                logger.warn("Did not found the Required Product : SMS will Fail")
                return (None, None, None, None)
            else:
                logger.warn("Balance is Low")
                return (None, None, None, None)

    else:
        logger.debug("Found the default product with only country code")
        return (default_product_obj.product_id, mobile_number,
                country_code, False)


def _get_default_product_no_country(account_id=None, sender_id=None,
                                    country_code=None, mobile_number=None):
    subtype = len(sender_id)
    check_balance = False
    if (subtype < 7):
        subtype = "short_code"
    else:
        subtype = "long_code"

    customer_country_obj = oa_session.query(Customer).filter(
        Customer.account_id == account_id
    ).with_entities(
        Customer.country_code
    ).first()

    country_code = customer_country_obj.country_code
    logger.debug("Customer COuntry COde : {}".format(country_code))

    # get_country_info_obj = get_countryinfo_by_name()
    try:
        country_id = get_countryinfo_by_name_obj[country_code]
    except Exception as e:
        raise InvalidCountryForProduct

    logger.debug("country_id : {}".format(country_id))

    formatted_mobile_number = normalize_number(
        mobile_number,
        country_id
    )
    if formatted_mobile_number is None:
        raise InvalidMobileNumberError(mobile_number)
    logger.debug("Formatted Number Using Customer's COuntry : {}".format(formatted_mobile_number))
    default_product_obj = m_session.query(DefaultProduct).filter(
        DefaultProduct.account_id == account_id,
        or_(DefaultProduct.subtype == subtype, DefaultProduct.subtype == 'one_way'),
        DefaultProduct.is_active == 1,
        DefaultProduct.country_code == country_code
    ).with_entities(
        DefaultProduct.product_id, DefaultProduct.country_code, DefaultProduct.account_id
    ).all()

    if default_product_obj:
        default_product_obj, check_balance = _check_product_price(default_product_obj)

    if not default_product_obj or not check_balance:
        default_product_obj = m_session.query(DefaultProduct).filter(
            DefaultProduct.account_id == account_id,
            DefaultProduct.country_code == "OG",
            DefaultProduct.is_active == 1
        ).with_entities(
            DefaultProduct.product_id, DefaultProduct.country_code, DefaultProduct.account_id
        ).all()

        if default_product_obj:
            default_product_obj, check_balance = _check_product_price(default_product_obj)

        if default_product_obj and check_balance:
            logger.debug("Successfully Received the Product without Label and Without COuntry : Global Product")
            return (default_product_obj.product_id, formatted_mobile_number,
                    country_code, True)
        else:
            if check_balance:
                logger.debug("Did not found the Required Product : SMS will Fail")
                return (None, None, None, None)
            else:
                logger.debug("Balance is Low")
                return (None, None, None, None)
    else:
        logger.debug("Successfully Received the Product without Label and Without COuntry : Default Product")
        return (default_product_obj.product_id, formatted_mobile_number,
                country_code, False)


def check_global_product(product_id, country_code):
    logger.debug("Checking Global Product with Product Id : {} and Country Code : {}".format(product_id, country_code))
    # global_product_obj_dict = load_global_product_dict()
    #
    # logger.debug("Dict {}".format(global_product_obj_dict))

    logger.debug("Country Id : {}".format(country_code))

    try:
        if country_code.isdigit():
            pass
    except Exception as e:
        # get_countryinfo_by_id_obj = get_countryinfo_by_id()
        country_code = get_countryinfo_by_id_obj[country_code]

    logger.debug("Country Code : {}".format(country_code))
    required_param = (product_id, country_code)
    logger.debug("required_param : {}".format(required_param))

    global_product_obj = global_product_obj_dict[required_param]

    logger.debug("Global Product : {}".format(global_product_obj))
    if global_product_obj is not None:
        logger.debug("Found Global Product with params : {}".format(global_product_obj))
        product_id = product_id
        price = global_product_obj[0]
        actual_provider, _, _, _ = get_product_details(global_product_obj[1])

        # logger.debug("Provider : {}".format(actual_provider.name))

        product_obj = oa_session.query(ProductModel).filter(
            ProductModel.id == product_id).first()
        currency = product_obj.base_currency

        logger.debug("Currency For Global Product : {}".format(currency))

        # currency = "EU"

        # logger.info("get_product_details :: provider = {}, price = {}, "
        #             "currency = {}".format(actual_provider.name, price, currency))

        global_product_details = [actual_provider, price, currency]
        logger.debug("global_product_details : {}".format(global_product_details))
        return global_product_details
    else:
        raise InvalidCountryForProduct


def get_module_by_product_id(product_id):
    logger.debug("Inside get_module_by_product_id : {}".format(product_id))

    product_obj = oa_session.query(ProductModel).filter(
        ProductModel.id == product_id).first()
    merchant_id = product_obj.merchant_id

    logger.debug("Received Product")

    merchant_obj = oa_session.query(Merchant).filter(
        Merchant.id == merchant_id).first()
    module = merchant_obj.module
    logger.debug("Received Merchant")
    module = module
    logger.debug("Inside get_module_by_product_id : {}".format(module))

    return module


def get_provider(module):
    logger.info("get_provider :: module = {} ".format(module))

    service_provider = m_session.query(ServiceProvider, ServiceProviderConfig).filter(
        ServiceProviderConfig.module == module).with_entities(ServiceProvider.id, ServiceProviderConfig.api_url).first()

    if service_provider is None:
        raise NotFoundError("SERVICE-PROVIDER-NOT-FOUND")
    logger.info("get_provider :: service_provider : {}".format(service_provider.id))

    api_url = service_provider.api_url
    if api_url is None:
        raise NotFoundError("API-URL-NOT-FOUND")

    provider_id = service_provider.id

    params = get_provider_params(provider_id)
    cls = get_provider_dynamically(module)
    # return cls(provider_id, api_url, params)
    return provider_id


def get_country_code(account_id, label):
    """{'IN': 91, 'US' : '1', 'AU': '61', 'GB': '44} mapper"""
    label_obj = m_session.query(Label).filter(
        Label.account_id == account_id, Label.label == label).first()
    if not label_obj:
        return None

    country_obj = m_session.query(CountryInfo).filter(
        CountryInfo.char_code == label_obj.country_code) \
        .with_entities(CountryInfo.code).first()
    if not country_obj:
        return None

    logger.info("get_country_code :: code = {}".format(country_obj.code))
    return country_obj.code


def _check_product_price(default_product_obj):
    logger.debug("Checking the balance for Default Product")
    for obj in default_product_obj:
        product_obj = Product(obj.account_id, obj.product_id)
        check_balance = product_obj.check_balance()
        if check_balance:
            logger.debug("Product Id : {0}, Has balance to send the SMS".format(obj.account_id))
            return obj, True
    return None, False
    # raise InsufficientBalanceError("INSUFFICIENT-BALANCE")


if __name__ == '__main__':
    print(get_product('10000000', 'campaignIndia'))
    print "Hello"
