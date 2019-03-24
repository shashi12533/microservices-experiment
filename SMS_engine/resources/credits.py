#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful import abort, reqparse, fields, marshal_with
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.credits import upsert_credits, get_credits_of_product, get_products_with_credit
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

log = get_logger()
crash_log = get_logger('crash')

credits_post_parser = reqparse.RequestParser()
credits_post_parser.add_argument('customer_id', type=unicode, required=True, help='CREDIT-REQ-CUSTOMER-ID')
credits_post_parser.add_argument('product_id', type=unicode, required=True, help='CREDIT-REQ-PRODUCT-ID')
credits_post_parser.add_argument('currency_code', type=unicode, required=True, help='CREDIT-REQ-CURRENCY-CODE')
credits_post_parser.add_argument('balance', type=float, required=True, help='CREDIT-REQ-BALANCE')

credits_response_format = dict(
    product_id=fields.String,
    currency_code=fields.String,
    added_credits=fields.Float,
    consumed_credits=fields.Float,
    remaining_credits=fields.Float,
)


def transform_credit(credit_obj=None):
    return dict(
        product_id=credit_obj.product_id,
        currency_code=credit_obj.currency_code,
        added_credits=credit_obj.balance + credit_obj.used_balance,
        consumed_credits=credit_obj.used_balance,
        remaining_credits=credit_obj.balance,
    )


class Balance(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(credits_response_format)
    def get(self, customer_id=None, product_id=None):
        """
        @api {get} /v1/customer/{customer_id}/product/{product_id}/credits/ Get credits
        @apiName Get credits
        @apiVersion 1.0.0
        @apiGroup Credits

        @apiHeader {String} apiKey Api key of onehop-api

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
            "product_id": "some-uuid",
            "currency_code": "EUR",
            "added_credits": "1000.50",
            "consumed_credits": "800.50",
            "remaining_credits": "200.00"
        }

        """
        try:
            credit_params = dict(customer_id=customer_id, product_id=product_id)
            credit_obj = get_credits_of_product(**credit_params)
            m_session.commit()
            return transform_credit(credit_obj=credit_obj)
        except ValueError as val_err:
            log.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except NotFoundError as nf_err:
            log.error(nf_err)
            m_session.rollback()
            return {
                "product_id": product_id,
                "currency_code": "",
                "added_credits": "0.0",
                "consumed_credits": "0.0",
                "remaining_credits": "0.0"
            }
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")

    @marshal_with(credits_response_format)
    def post(self):
        """
        @api {post} /v1/credits/ Add-Update credits
        @apiName Upsert credits
        @apiVersion 1.0.0
        @apiGroup Credits

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} customer_id Customer id
        @apiParam {String} product_id Product id
        @apiParam {String} balance Account balance for a product
        @apiParam {String} currency_code Currency code e.g. USD

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
            "product_id": "some-uuid",
            "currency_code": "EUR",
            "added_credits": "1000.50",
            "consumed_credits": "800.50",
            "remaining_credits": "200.00"
        }

        """
        credits_params = credits_post_parser.parse_args()
        log.debug('params : {}'.format(credits_params))

        try:
            credit_obj = upsert_credits(**credits_params)
            m_session.commit()
            return transform_credit(credit_obj=credit_obj)
        except ValueError as val_err:
            log.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")


class ProductCredits(Resource):
    method_decorators = [authenticate_account]
    products_credit_obj_list = []

    @marshal_with(credits_response_format)
    def get(self, customer_id=None):
        """
        @api {get} /v1/customer/{customer_id}/products Get product credits info
        @apiVersion 1.0.0
        @apiName get product credits
        @apiGroup Credits

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 201 OK
        {
            product_id='uuid',
            currency_code='USD',
            added_credits=10,
            consumed_credits=5,
            remaining_credits=5
        }
        """
        try:
            self.products_credit_obj_list = get_products_with_credit(customer_id=customer_id)
            return self.transform_product_credit()
        except ValueError as val_err:
            log.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")

    def transform_product_credit(self):
        response = []
        for a_product_credit_obj in self.products_credit_obj_list:
            if not a_product_credit_obj.deleted_on:
                response.append(transform_credit(credit_obj=a_product_credit_obj))
        log.info(response)
        return response
