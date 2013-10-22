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

from osv import fields, osv
import time
from tools.translate import _


class account_move(osv.osv):
    _name = 'account.move'
    _inherit = 'account.move'


    def button_cancel(self, cr, uid, ids, context={}, check_voucher=True, check_invoice=True, **kwars):
        invoice_pool = self.pool.get('account.invoice')
        for move in self.browse(cr, uid, ids, context=context):
            invoice_ids = invoice_pool.search(cr, uid, [('move_id', '=', move.id)])
            if invoice_ids and check_invoice:
                invoice_obj = invoice_pool.browse(cr, uid, invoice_ids, context=context)[0]
                raise osv.except_osv(_('Error !'), _("You cannot cancel this transaction from here - cancel the invoice '%s' directly" % invoice_obj.number))
            for line in move.line_id:
                if line.voucher_id and check_voucher:
                    raise osv.except_osv(_('Error !'), _("You cannot cancel this transaction from here - cancel the payment '%s' directly" % line.voucher_id.number))
                if line.statement_id and line.statement_id.state == 'confirm':
                    raise osv.except_osv(_('Error !'), _("You cannot cancel this payment as it is bank reconciled '%s'" % line.statement_id.name))
        result = super(account_move, self).button_cancel(cr, uid, ids, context=context, **kwars)
        return result

    def copy(self, cr, uid, id, default={}, context={}):
        result = super(account_move, self).copy(cr, uid, id, default, context)
        for move_line in self.browse(cr, uid, result, context=context).line_id:
            move_line.write({'voucher_id': None}, context=context)
        return result

account_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
