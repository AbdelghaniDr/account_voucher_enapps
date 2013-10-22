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

from osv import osv
from tools.translate import _


class invoice(osv.osv):
    _inherit = 'account.invoice'

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids:
            return []
        inv = self.browse(cr, uid, ids[0], context=context)

        voucher_defaults = self.get_voucher_defaults(cr, uid, ids, inv, context=context)
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': voucher_defaults,
        }

    def get_voucher_defaults(self, cr, uid, ids, invoice_obj, context={}):
        """Return the dict of keys as 'default_' + field_name and vals
        to be used as defaults in new Voucher"""
        return {
                'default_partner_id': invoice_obj.partner_id.id,
                'default_amount': invoice_obj.residual,
                'default_name': invoice_obj.name,
                'close_after_process': True,
                'invoice_type': invoice_obj.type,
                'invoice_id': invoice_obj.id,
                'default_type': (invoice_obj.type in ('out_invoice', 'out_refund') and 'receipt') or 'payment',
                'default_company_id': invoice_obj.company_id.id,
        }

    def set_current_state(self, cr, uid, ids, context={}):
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.reconciled:
                invoice.write({'state': 'paid'})
            else:
                invoice.write({'state': 'open'})
        return True

invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
