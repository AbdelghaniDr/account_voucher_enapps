# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Enapps LTD (<http://www.enapps.co.uk>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from osv import osv

class res_currency(osv.osv):
    _name = "res.currency"
    _inherit = "res.currency"

    def compute_to_date(self, cr, uid, from_currency_id, to_currency_id, from_amount, date=None, round=True, context=None):
        if date == None:
            date = time.strftime('%Y-%m-%d')
        if not from_currency_id:
            from_currency_id = to_currency_id
        if not to_currency_id:
            to_currency_id = from_currency_id
        xc = self.browse(cr, uid, [from_currency_id,to_currency_id], context=context)
        to_currency = (xc[0].id == to_currency_id and xc[0]) or xc[1]
        if to_currency_id == from_currency_id:
            if round:
                return self.round(cr, uid, to_currency, from_amount)
            else:
                return from_amount
        else:
            rate_from = self._get_latest_currency_rate(cr, uid, from_currency_id, date, context=context)
            rate_to = self._get_latest_currency_rate(cr, uid, to_currency_id, date, context=context)
            rate = rate_to/rate_from
            if round:
                return self.round(cr, uid, to_currency, from_amount * rate)
            else:
                return (from_amount * rate)

    def _get_latest_currency_rate(self, cr, uid, currency_id, target_date, context={}):
        cr.execute("""SELECT rate
                      FROM res_currency_rate
                      WHERE currency_id = %s
                        AND name <= %s
                      ORDER BY name DESC
                      LIMIT 1
                   """, (currency_id, target_date))
        currency_rate = cr.fetchone()
        return currency_rate[0]

res_currency()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
