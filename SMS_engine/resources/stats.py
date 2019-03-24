#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort, reqparse

from media_engine.helper import get_logger
from media_engine.lib.stats import get_stats
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

logger = get_logger()


class Stats(Resource):
    method_decorators = [authenticate_account]

    def __init__(self, *args, **kwargs):
        super(Stats, self).__init__(*args, **kwargs)
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument(
            'account_id', type=unicode, required=True)
        self.request_parser.add_argument(
            'product_id', type=unicode, required=False)

    def get(self):
        """
          @api {get} /v1/stats/ Get Statistical data
          @apiVersion 1.0.0
          @apiName get
          @apiGroup Statistics

          @apiParam {String}      account_id    Customer Id
          @apiParam {String}      product_id    Product Id




        """

        params = self.request_parser.parse_args()
        logger.debug('params : {}'.format(params))

        try:
            params['stats'] = get_stats()
            m_session.commit()
        except Exception as exc:
            m_session.rollback()
            abort(400, message=exc.message)
        else:
            logger.debug(
                'Account: {} :: stats: {}'.format(
                    params['account_id'],
                    params['stats']
                )
            )
            return params
