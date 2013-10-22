# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

class account_voucher_installer(osv.osv_memory):
    _name = 'account.voucher.installer'
    _inherit = 'res.config.installer'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'exchange_gains': fields.many2one(
            'account.account',"Exchange rate gains",
            domain="[('type', '=', 'other'), ('company_id', '=', company_id)]",),
        'exchange_losses': fields.many2one(
            'account.account', "Exchange rate losses",
            domain="[('type', '=', 'other'), ('company_id', '=', company_id)]",),
        'writeoff_gains': fields.many2one(
            'account.account',"Writeoff gains",
            domain="[('type', '=', 'other'), ('company_id', '=', company_id)]",),
        'writeoff_losses': fields.many2one(
            'account.account', "Writeoff losses",
            domain="[('type', '=', 'other'), ('company_id', '=', company_id)]",),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False

    def _default_exchange_gains(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.exchange_gains and user.company_id.exchange_gains.id or False

    def _default_exchange_losses(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.exchange_losses and user.company_id.exchange_losses.id or False

    def _default_writeoff_gains(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.writeoff_gains and user.company_id.writeoff_gains.id or False

    def _default_writeoff_losses(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.writeoff_losses and user.company_id.writeoff_losses.id or False

    _defaults = {
        'company_id': _default_company,
        'exchange_gains': _default_exchange_gains,
        'exchange_losses': _default_exchange_losses,
        'writeoff_gains': _default_writeoff_gains,
        'writeoff_losses': _default_writeoff_losses,
    }

    def execute(self, cr, uid, ids, context={}):
        super(account_voucher_installer, self).execute(cr, uid, ids, context=context)
        company_pool = self.pool.get('res.company')
        for config_form in self.browse(cr, uid, ids, context=context):
            company_pool.write(cr, uid, config_form.company_id.id,
                              {
                                  'exchange_gains': config_form.exchange_gains and config_form.exchange_gains.id,
                                  'exchange_losses': config_form.exchange_losses and config_form.exchange_losses.id,
                                  'writeoff_gains': config_form.writeoff_gains and config_form.writeoff_gains.id,
                                  'writeoff_losses': config_form.writeoff_losses and config_form.writeoff_losses.id,
                              }, context=context)

account_voucher_installer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
