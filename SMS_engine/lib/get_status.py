from __future__ import absolute_import
from media_engine.helper import get_worker_logger
from media_engine.models import m_session,Account,Label, SmsHistory
from media_engine.models import Credit, m_session
from media_engine.lib.validators import not_empty
from sqlalchemy import and_, Date, func


logger = get_worker_logger('worker')

#@not_empty('customer_ids', err_code='CUSTOMER-ID-LIST-NULL', var_type=list, req=True)
def get_customer_status(**params):
    customer_list = params['customer_ids']
    start_date = params['from_date']
    end_date = params['to_date']

    q = (
        m_session.query(Account.customer_id).filter(
            and_(Account.customer_id.in_(customer_list),  Account.id == SmsHistory.account_id)
        ).join(SmsHistory).filter(
         and_(start_date <= func.DATE(SmsHistory.created_on), func.DATE(SmsHistory.created_on) < end_date)
        ).group_by(Account.customer_id)
      )

    active_customer = q.all()
    records = []
    for record in active_customer:
        records.append(record[0])

    customer_status = []

    for id in customer_list:
        if id in records:
            customer_status.append({"customer_id" : id, "status" : 'active'})
        else:
            customer_status.append({"customer_id" : id, "status" : 'inactive'})

    return customer_status



# if __name__ == '__main__':
#     params = {'from_date': '2016-01-04', 'to_date': '2017-01-05', 'customer_ids': ['a', 'b', 'c']}
#     result = get_customer_status(**params)
#     print result




