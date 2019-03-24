#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import math
import operator
import re
import phonenumbers
from media_engine.helper import get_worker_logger
from media_engine.lib import errors
from media_engine.lib.validators import reject_non_text_args

logger = get_worker_logger('worker')


def truncate_sender_id(sender_id):
    """"truncate senderId when alphanumeric and containing more than 11 chars"""
    logger.info("truncate_sender_id :: sender_id : {}".format(sender_id))
    sender_id = sender_id.strip()
    if sender_id.isdigit():
        logger.info("truncate_sender_id :: Numeric senderID: {}".format(
            sender_id))
    elif len(sender_id) > 11:
        sender_id = sender_id[:11]
        logger.info(
            "truncate_sender_id :: Alphanumeric senderID after truncate : "
            "{}".format(sender_id))
    else:
        logger.info(
            "truncate_sender_id :: Alphanumeric senderID without truncate : "
            "{}".format(sender_id))
    return sender_id


def get_encoding(sms_text):
    logger.info('get_encoding :: {}'.format({'sms_text': sms_text}))

    try:
        from smspdu import gsm0338
    except ImportError:
        # chardet is used in case of python3
        import chardet
        encoding = 1 if chardet.detect(sms_text)['encoding'] == 'ascii' else 2
        logger.info('get_encoding :: chardet.encoding = {}'.format(encoding))
        return encoding
    else:
        gsm_object = gsm0338()
        gsm_enc = True

    try:
        sms_text.decode('ascii')
    except Exception as err:
        logger.info('get_encoding :: Not ascii sms_text: {}'.format(err))
        enc = 'utf-8'
    else:
        enc = 'ascii'

    try:
        gsm_object.encode(sms_text)
    except TypeError as warning:
        logger.info('get_encoding :: gsm TypeError {}'.format(warning))
        gsm_enc = False
    except Exception as err:
        logger.info('get_encoding :: gsm Exception {}'.format(err))
        enc = 'utf-8'
        gsm_enc = False

    logger.info('get_encoding :: encoding = {} and gsm_enc = {}'.format(
        enc, gsm_enc))
    encoding = 2 if enc == 'utf-8' and not gsm_enc else 1

    logger.info('get_encoding :: Encoding at our end is {}'.format(encoding))
    return encoding


def replace_characters(sms_text):
    logger.info('replace_characters :: sms_text : {}'.format(
        {'sms_text': sms_text}))
    sms_text_after_replacement = None
    if sms_text:
        dictionary = {
            u"“": '"',
            u"”": '"',
            u"’": "'",
            u"‘": "'",
            u"Ç": "C",
            u"ç": "c",
            u"Ğ": "G",
            u"ğ": "g",
            u"Ş": "S",
            u"ş": "s",
            u"Ö": "O",
            u"ö": "o",
            u"Ü": "U",
            u"ü": "u",
            u"è": "e",
            u"ć": "c",
            u"ę": "e",
            u"ł": "l",
            u"ń": "n",
            u"ó": "o"
        }
        pattern = '|'.join(map(re.escape, dictionary.keys()))
        sms_text_after_replacement = re.sub(
            pattern, lambda m: dictionary[m.group()], sms_text)
    logger.info('replace_characters :: {}'.format(
        {'sms_text_after_replacement': sms_text_after_replacement}))
    return sms_text_after_replacement


def get_number_of_sms(encoding, text):
    logger.info('get_number_of_sms :: {}'.format(
        {'encoding':encoding, 'sms_text':text}))
    if not text:
        raise errors.InvalidSMSTextError(text, 'Text is empty')
    # when you put 'coding' (see line 1)
    # len will act like mb_strlen (php)
    # Use some test cases and do verify PHP and
    # Python logic for this method.
    char_set = ['{', '}', '~', '[', ']', '|', '^', '\\']
    counter = sum(text.count(c) for c in char_set if c in text)
    textlen = len(text) + counter
    if textlen > 724:
        raise errors.InvalidSMSTextError(
            text, 'Character limit exceeded, greater than 700')

    char_limit = 160 if textlen <= 160 and encoding == 1 else 152
    if encoding == 2:
        char_limit = 70
    logger.info('get_number_of_sms :: Text length : {} and Chart Limit : {}'.format(
        textlen, char_limit))

    offset = textlen % char_limit
    additional_number_of_sms = 1 if offset > 0 else 0
    number_of_sms = int(math.floor(textlen / char_limit))
    number_of_sms += additional_number_of_sms
    logger.info('get_number_of_sms :: Number Of SMS = {}'.format(number_of_sms))
    return number_of_sms


# only used for dialogue provider
@reject_non_text_args
def str_to_hex(text):
    logger.info('str_to_hex :: text = {}'.format(text))
    hex_string = functools.reduce(
        operator.add,
        (('%x' % ord(character)).ljust(2, '0') for character in text)
    )

    logger.info('str_to_hex :: hex = {}'.format(hex_string))
    return hex_string


def cleanup_message(message):
    logger.info('cleanup_message :: {}'.format({'message': message}))
    if message:
        message = re.sub("\'", "'", message)
        message = re.sub("\"", '"', message)
    message = message or ''
    logger.info('cleanup_message :: after cleanup : {}'.format({'message': message}))
    return message


def format_sms_text(sms_text, encoding=1):
    """
    Get formatted sms text
    :param sms_text
    :param encoding
    :return: formatted sms_text, encoding and number of sms
    """
    logger.info("format_sms_text :: {}".format({'sms_text': sms_text}))
    sms_text = cleanup_message(sms_text)
    if encoding != 2:
        sms_text = replace_characters(sms_text)
    encoding = get_encoding(sms_text)
    number_of_sms = get_number_of_sms(encoding, sms_text)
    return sms_text, encoding, number_of_sms


@reject_non_text_args
def get_numeric_number(mobile_number):
    """
    :param mobile_number: mobile number
    :return: numeric mobile number
    e.g.
    In [89]: mobile_number = '(555)555-5555'
    In [90]: get_numeric_number(mobile_number)
    Out[90]: '5555555555'
    In [91]: mobile_number = '+91 9975542588'
    In [92]: get_numeric_number(mobile_number)
    Out[92]: '919975542588'
    """
    logger.info(
        'get_numeric_number :: mobile_number = {}'.format(mobile_number))
    numeric_mobile_number = ''.join(
        x for x in mobile_number if x.isdigit()).lstrip('0')\
        if mobile_number is not None else None
    logger.info('get_numeric_number :: Numeric Mobile Number = {}'.format(
        numeric_mobile_number))
    return numeric_mobile_number


def normalize_number(mobile_number, country_code_of_label):
    """
    Parse number
    :param mobile_number:
    :param country_code_of_label:
    :return: international number
    """
    logger.info("normalize_number :: mobile_number = {} and "
                "country_code_of_label = {}".format(
                    mobile_number, country_code_of_label))
    if not isinstance(mobile_number, basestring):
        mobile_number = str(mobile_number)
    if mobile_number.startswith('+'):
        # If international phone number is provided, then
        # remove initial '+' character
        mobile_number = mobile_number[1:]
    try:
        region = phonenumbers.region_code_for_country_code(
            int(country_code_of_label)
        )
        phone_num = phonenumbers.parse(
            mobile_number,
            region=region,
        )
        is_valid_phone_no = phonenumbers.is_valid_number_for_region(
            phone_num, region)
        logger.info("normalize_number :: region = {} and "
                    "is_valid_phone_no = {}".format(region, is_valid_phone_no))
        if not is_valid_phone_no:
            #raise errors.InvalidMobileNumberError(mobile_number)
            return None
    except ImportError as e:
        logger.error("normalize_number :: {}".format(e.message))
        # todo: send email to admin. Is that a good idea?
        #raise errors.NotInstalledError(mobile_number, e.message)
        return None

    except Exception as e:
        logger.error(
            "normalize_number :: mobile_number : {} : Error : {}".format(
                mobile_number, e.message)
        )
        #raise errors.InvalidMobileNumberError(mobile_number)
        return None

    international_number = '{}{}'.format(
        phone_num.country_code, phone_num.national_number)
    return international_number


def get_ceil_value(value=None, precision=2):
    precision_factor = 10**precision
    return math.ceil(float(value) * precision_factor) / precision_factor


def count_gsm0338_length(sms_text):
    """Count the number of GSM 03.38 chars a conversion would contain.
        It's about 3 times faster to count than convert and do strlen()
            if conversion is not required"""

    length = len(sms_text)
    # fixme : test re.search and re.match. use appropriate
    length += re.search(u'/[\\^{}\\\~€|\\[\\]]/mu', sms_text) or 0
    return length

def country_code_from_mobile_number(mobile_number):
    #return 1
    logger.debug("By using mobile number fetch country code. Mobile Number : {}".format(mobile_number))

    try:
        country_code_status = phonenumbers.parse(mobile_number, None)

    except Exception as e:
        return None

    logger.debug("Country code : {}".format(country_code_status))
    if country_code_status.country_code != None:
        logger.debug("Country code : {}".format(country_code_status.country_code))
        return country_code_status.country_code
    return None
