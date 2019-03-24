from __future__ import absolute_import
from sqlalchemy import func
from media_engine.helper import get_worker_logger
from media_engine.models import m_session,Account,Label, SmsHistory
from media_engine.models import Credit, m_session
from media_engine.lib.validators import not_empty
from sqlalchemy import and_


logger = get_worker_logger('worker')


@not_empty('customer_ids', err_code='CUSTOMER-ID-LIST-NULL', var_type=list, req=True)
def get_unused_balance_for_customer_id(**params):
    #print 'In get_unused_balance_for_customer_id'
    #print 'PARAMS: ',params
    params_list = params['customer_ids']
    q = (
        m_session.
    query(Account.customer_id, Credit.currency_code,
          func.sum(Credit.balance).label("unused_balance"))
        .filter(Account.customer_id.in_(params_list))
        .join(Credit)
        .group_by(Account.customer_id, Credit.currency_code)
    )
    result=q.all()

    dict = {}

    for i in range(len(params_list)):
        list = []
        for x in result:
            if x[0] == params_list[i]:
                tup = (x[1], x[2])
                list.append(tup)

        dict[params_list[i]] = list

    return dict
























