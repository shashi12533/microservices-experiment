#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort, reqparse, fields, marshal_with, inputs
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.errors import NotFoundError
from media_engine.lib.labels import add_label, delete_label,\
    list_labels_with_details, update_label
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

log = get_logger()
crash_log = get_logger('crash')


label_post_request_parser = reqparse.RequestParser()
label_post_request_parser.add_argument('customer_id', type=unicode, required=True, help='LABEL-REQ-CUSTOMER-ID')
label_post_request_parser.add_argument('product_id', type=unicode, required=True, help='LABEL-REQ-PRODUCT-ID')
label_post_request_parser.add_argument('comment', type=unicode, required=False, help='LABEL-BAD-COMMENT')
label_post_request_parser.add_argument('country_code', type=unicode, required=True, help='LABEL-REQ-COUNTRY-CODE')
label_post_request_parser.add_argument('label', type=unicode, required=True, help='LABEL-REQ-LABEL')
label_post_request_parser.add_argument('is_active', type=inputs.boolean, required=True, help='LABEL-REQ-IS-ACTIVE')

label_delete_request_parser = reqparse.RequestParser()
label_delete_request_parser.add_argument('customer_id', type=unicode, required=True)
label_delete_request_parser.add_argument('label_id', type=unicode, required=True)

label_update_request_parser = reqparse.RequestParser()
label_update_request_parser.add_argument('label_id', type=unicode, required=True, help='LABEL-BAD-LABEL-ID')
label_update_request_parser.add_argument('customer_id', type=unicode, required=True, help='LABEL-REQ-CUSTOMER-ID')
label_update_request_parser.add_argument('product_id', type=unicode, required=True, help='LABEL-REQ-PRODUCT-ID')
label_update_request_parser.add_argument('comment', type=unicode, required=False, help='LABEL-BAD-COMMENT')
label_update_request_parser.add_argument('country_code', type=unicode, required=True, help='LABEL-REQ-COUNTRY-CODE')
label_update_request_parser.add_argument('label', type=unicode, required=True, help='LABEL-REQ-LABEL')
label_update_request_parser.add_argument('is_active', type=inputs.boolean, required=True, help='LABEL-REQ-IS-ACTIVE')


label_response_format = dict(
    id=fields.String,
    label=fields.String,
    comment=fields.String,
    is_active=fields.Boolean,
    country_code=fields.String,
    product_id=fields.String,
    deleted_on=fields.DateTime,
)

label_details_response_format = dict(
    customer_id=fields.String,
    labels_list=fields.List(
        fields.Nested(label_response_format)
    ),
)


def transform_label(a_label=None):
    return dict(
        id=a_label.id,
        label=a_label.label,
        is_active=a_label.is_active,
        country_code=a_label.country_code,
        product_id=a_label.product_id,
        comment=a_label.comment,
        deleted_on=a_label.deleted_on
    )


class LabelDetails(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(label_details_response_format)
    def get(self, customer_id):
        """
        @api {get} /v1/customer/<string:customer_id>/label_details/ List labels for an account
        @apiVersion 1.0.0
        @apiName List labels
        @apiGroup Labels

        @apiHeader {String} apiKey Api key of onehop-api

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
            "customer_id": "a8d95ac6-b8cc-4199-833f-88e1fa8f6580",
            "labels_list": [
                {
                    "comment": "Yay, I'm a comment",
                    "country_code": "IN",
                    "deleted_on": null,
                    "is_active": true,
                    "label": "campaignIndia",
                    "product": {
                    "code": "3141",
                    "id": "4be8244e-0b1d-45aa-8f9f-42d0104dfcf9",
                    "name": "Lavenia"
                }
                },
                {
                    "comment": "yay! LOL!!",
                    "country_code": "IN",
                    "deleted_on": null,
                    "is_active": true,
                    "label": "shiny label",
                    "product": {
                    "code": "3141",
                    "id": "4be8244e-0b1d-45aa-8f9f-42d0104dfcf9",
                    "name": "Some Name"
                }
                }
            ]
        }

        """

        try:
            label_object_list = list_labels_with_details(customer_id=customer_id)
            result = [transform_label(a_label) for a_label in label_object_list]
            return dict(
                customer_id=customer_id,
                labels_list=result
            )
        except NotFoundError as nf_error:
            log.error(nf_error)
            m_session.rollback()
            abort(400, message=nf_error.message)
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

    @marshal_with(label_response_format)
    def post(self):
        """
        @api {post} /v1/label/save/ Post a label for an account
        @apiVersion 1.0.0
        @apiName Post label
        @apiGroup Labels

        @apiHeader {String} apiKey Api key of onehop-api

        @apiParam {String} customer_id Customer id
        @apiParam {String} product_id Product id
        @apiParam {String} country_code Country code
        @apiParam {String} label Label
        @apiParam {String} [comment] Comment
        @apiParam {Boolean} is_active If active then true, else false

        (
            customer_id=user.customer.id,
            product_id=kwargs['product_id'],
            country_code=kwargs['country_code'],
            label=kwargs['label'],
            comment=kwargs['comment'],
            is_active=kwargs['is_active']
        )

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
            "comment": "yay! LOL!!",
            "country_code": "IN",
            "deleted_on": null,
            "id": "e13d1096-668a-40fe-8852-246cf37653cc",
            "is_active": true,
            "label": "shiny label",
            "product_id": "4be8244e-0b1d-45aa-8f9f-42d0104dfcf9"
        }
        """
        try:
            params = label_post_request_parser.parse_args()
            label_obj = add_label(**params)
            m_session.commit()
            return transform_label(label_obj)
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
            abort(400, message=nf_err.message)
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")

    @marshal_with(label_response_format)
    def put(self):
        """
        @api {put} /v1/label/update/ Update a label for an account
        @apiVersion 1.0.0
        @apiName Update label
        @apiGroup Labels

        @apiHeader {String} apiKey Api key of onehop-api

        @apiParam {String} customer_id Customer id
        @apiParam {String} product_id Product id
        @apiParam {String} country_code Country code
        @apiParam {String} label Label
        @apiParam {String} [comment] Comment
        @apiParam {Boolean} is_active If active then true, else false
        (
            customer_id=user.customer.id,
            product_id=kwargs['product_id'],
            country_code=kwargs['country_code'],
            label=kwargs['label'],
            comment=kwargs['comment'],
            is_active=kwargs['is_active']
        )

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
            "comment": "yay! LOL!!",
            "country_code": "IN",
            "deleted_on": null,
            "id": "e13d1096-668a-40fe-8852-246cf37653cc",
            "is_active": true,
            "label": "shiny label",
            "product_id": "4be8244e-0b1d-45aa-8f9f-42d0104dfcf9"
        }
        """
        try:
            params = label_update_request_parser.parse_args()
            label_obj = update_label(**params)
            m_session.commit()
            return transform_label(label_obj)
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
            abort(400, message=nf_err.message)
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")

    @marshal_with(label_response_format)
    def delete(self, customer_id, label_id):
        """
        @api {delete} /v1/customer/{customer_id}/label/{label_id} Delete a label for a customer
        @apiVersion 1.0.0
        @apiName Delete label
        @apiGroup Labels

        @apiHeader {String} apiKey Api key of onehop-api

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
            "comment": "yay! LOL!!",
            "country_code": "IN",
            "deleted_on": "Mon, 23 May 2016 18:40:33 -0000",
            "id": "e13d1096-668a-40fe-8852-246cf37653cc",
            "is_active": false,
            "label": "shiny label",
            "product_id": "4be8244e-0b1d-45aa-8f9f-42d0104dfcf9"
        }
        """
        try:
            # params = label_delete_request_parser.parse_args()
            label_obj = delete_label(customer_id=customer_id, label_id=label_id)
            m_session.commit()
            return transform_label(label_obj)
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
        except NotFoundError as nf_error:
            log.error(nf_error)
            m_session.rollback()
            abort(400, message=nf_error.message)
