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
from lxml import etree

import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _


class account_voucher(osv.osv):

    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('type', False)

    def _get_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_pool = self.pool.get('account.journal')
        invoice_pool = self.pool.get('account.invoice')
        if context.get('invoice_id', False):
            currency_id = invoice_pool.browse(cr, uid, context['invoice_id'], context=context).currency_id.id
            journal_id = journal_pool.search(cr, uid, [('currency', '=', currency_id)], limit=1)
            if journal_id:
                return journal_id and journal_id[0] or False
        if context.get('journal_id', False):
            return context.get('journal_id')
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            return context.get('search_default_journal_id')
        if not context.get('invoice_id') and not context.get('journal_id'):
            return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.default_bank_journal_id.id
        res = journal_pool.search(cr, uid, [('type', '=', 'bank')], limit=1)
        return res and res[0] or False

    def _get_partner(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('partner_id', False)

    def _get_invoice(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('invoice_id', False)

    def _get_reference(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('reference', False)

    def _get_period(self, cr, uid, context={}):
        date = time.strftime('%Y-%m-%d'),
        period_pool = self.pool.get('account.period')
        period_id = period_pool.find(cr, uid, dt=date, context=context)[0]
        return period_id

    def _get_narration(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('narration', False)

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(osv.osv, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        partner_node = doc.xpath("//field[@name='partner_id']")[0]
        if 'payment' in (context.get('default_type', None), context.get('type', None)):
            partner_node.set('domain', "[('supplier', '=', True)]")
            partner_node.set('string', "Supplier")
        else:
            partner_node.set('domain', "[('customer', '=', True)]")
            partner_node.set('string', "Customer")
        res['arch'] = etree.tostring(doc)
        return res

    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            writeoff_amount = voucher.amount - self.get_total_amount(cr, uid, voucher, context=context)
            result[voucher.id] = writeoff_amount
        return result

    def _get_writeoff_acc_id(self, cr, uid, ids, context={}):
        result = None
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for voucher_id in ids:
            result = user.company_id.writeoff_losses.id
        return result

    def get_total_amount(self, cr, uid, voucher_obj, voucher_id=None, context={}):
        if not voucher_obj:
            voucher_obj = self.browse(cr, uid, voucher_id, context=context)
        result = 0
        for line in voucher_obj.line_ids:
            if line.state != 'draft':
                result += line.amount
        return result

    _name = 'account.voucher'
    _inherit = 'account.voucher'
    _description = 'Accounting Voucher'
    _order = "date desc, id desc"
    _columns = {
        ### Modify fields that are required in origional account_voucher
        'account_id': fields.many2one('account.account',
                                    'Account',
                                    required=False,
                                    readonly=True,
                                    states={'draft': [('readonly', False)]}),
        ###
        'type': fields.selection([('payment', 'Payment'),
                                  ('receipt', 'Receipt'),
                                 ], 'Default Type',
                                 readonly=True,
                                 states={
                                     'draft': [('readonly', False)]
                                 },
                                ),
        'name': fields.char('Memo',
                             size=256,
                             readonly=True,
                             states={
                                 'open': [('readonly', False)],
                                 'draft': [('readonly', False)],
                             },
                            ),
        'date': fields.date('Date',
                             readonly=True,
                             select=True,
                             states={
                                 'draft': [('readonly', False)],
                                 'proforma': [('readonly', False)],
                             },
                             help="Effective date for accounting entries",
                            ),
        'company_id': fields.many2one('res.company',
                                     'Company'
                                     ),
        'journal_id': fields.many2one('account.journal',
                                     'Journal',
                                     required=False,
                                     readonly=True,
                                     states={
                                         'draft': [('readonly', False)],
                                     },
                                    ),
        'invoice_id': fields.many2one('account.invoice',
                                     'Invoice',
                                     required=False,
                                     readonly=True,
                                     states={
                                         'draft': [('readonly', False)],
                                     },
                                    ),
        'line_ids': fields.one2many('account.voucher.line',
                                     'voucher_id',
                                     'Voucher Lines',
                                     readonly=True,
                                     states={
                                         'open': [('readonly', False)],
                                     },
                                    ),
        'period_id': fields.many2one('account.period',
                                     'Period',
                                     required=False,
                                     readonly=True,
                                     states={
                                         'open': [('readonly', False)],
                                         'draft': [('readonly', False)],
                                     },
                                    ),
        'narration': fields.text('Notes',
                                 readonly=True,
                                 states={
                                     'open': [('readonly', False)],
                                     'draft': [('readonly', False)]
                                 },
                                ),
        'state': fields.selection([('draft', 'Draft'),
                                  ('open', 'Open'),
                                  ('precomputed', 'Pre-computed'),
                                  ('proforma', 'Pro-forma'),
                                  ('posted', 'Posted'),
                                  ('cancel', 'Cancelled'),
                                 ],
                                 'State',
                                 readonly=True,
                                 size=32,
                                ),
        'amount': fields.float('Amount to pay',
                             digits_compute=dp.get_precision('Account'),
                             required=False,
                             readonly=False,
                             states={
                                 'posted': [('readonly', True)],
                                 'draft': [('readonly', True)],
                                 'open': [('readonly', True)],
                                 'proforma': [('readonly', False)],
                                 'precomputed': [('readonly', False)],
                             },
                            ),
        'reference': fields.char('Ref #',
                                 size=256,
                                 readonly=False,
                                 help="Transaction reference number.",
                                 states={
                                     'posted': [('readonly', True)],
                                     'draft': [('readonly', False)],
                                     'open': [('readonly', False)],
                                     'precomputed': [('readonly', False)],
                                 },
                                ),
        'number': fields.char('Number',
                             size=32,
                             readonly=False,
                             states={
                                 'posted': [('readonly', True)],
                             },
                            ),
        'move_id': fields.many2one('account.move',
                                     'Account Entry',
                                    ),
        'move_ids': fields.related('move_id',
                                 'line_id',
                                 type='one2many',
                                 relation='account.move.line',
                                 string='Journal Items',
                                 readonly=True,
                                 states={
                                     'open': [('readonly', False)],
                                     'draft': [('readonly', False)]
                                 },
                                ),
        'partner_id': fields.many2one('res.partner',
                                     'Partner',
                                     change_default=1,
                                     readonly=True,
                                     states={
                                         'draft': [('readonly', False)],
                                     },
                                    ),
        'audit': fields.related('move_id',
                                 'to_check',
                                 type='boolean',
                                 relation='account.move',
                                 string='Audit Complete ?',
                                ),
        'date_due': fields.date('Due Date',
                                 readonly=True,
                                 select=True,
                                 states={
                                     'open': [('readonly', False)],
                                     'draft': [('readonly', False)]
                                 },
                                ),
        'payment_option': fields.selection([('without_writeoff', 'Keep Open'),
                                              ('with_writeoff', 'Reconcile with Write-Off'),
                                             ],
                                             'Payment Difference',
                                             required=False,
                                             readonly=False,
                                             states={
                                                 'posted': [('readonly', True)],
                                                 'draft': [('readonly', False)],
                                                 'open': [('readonly', False)],
                                                 'precomputed': [('readonly', False)],
                                             },
                                            ),
        'comment': fields.char('Ex diff comment',
                             size=64,
                             required=False,
                             readonly=False,
                             states={
                                 'posted': [('readonly', True)],
                             },
                            ),
        'analytic_id': fields.many2one('account.analytic.account',
                                     'Ex diff Analytic Account',
                                     readonly=False,
                                     states={
                                         'posted': [('readonly', True)],
                                     },
                                    ),
        'writeoff_amount': fields.function(_get_writeoff_amount,
                                         digits_compute=dp.get_precision('Account'),
                                         method=True,
                                         string='Payment diff',
                                         type='float',
                                         store=True,
                                        ),
        'writeoff_acc_id': fields.many2one('account.account',
                                           'Writeoff Account',
                                           required=False,
                                          ),
    }
    _defaults = {
        'partner_id': _get_partner,
        'journal_id': _get_journal,
        'invoice_id': _get_invoice,
        'reference': _get_reference,
        'narration': _get_narration,
        'amount': 0,
        'type': _get_type,
        'state': 'draft',
        'name': '',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'period_id': _get_period,
        'payment_option': 'with_writeoff',
        'comment': _('Write-Off'),
        'writeoff_acc_id': _get_writeoff_acc_id,
    }

    def name_get(self, cr, uid, ids, context={}):
        result = []
        for voucher in self.browse(cr, uid, ids, context=context):
            voucher_name = voucher.partner_id and voucher.partner_id.name or ""
            voucher_name += voucher.number and " :: %s" % (voucher.number) or ""
            result.append((voucher.id, voucher_name))
        return result

    def get_open_entries(self, cr, uid, ids, context={}):
        voucher_pool = self.pool.get('account.voucher')
        voucher_line_pool = self.pool.get('account.voucher.line')
        voucher_obj = self.browse(cr, uid, ids, context={})[0]
        context['date'] = voucher_obj.date or time.strftime('%Y-%m-%d')
        voucher_type = voucher_obj.type
        if voucher_type == 'payment':
            account_type = 'payable'
        else:
            account_type = 'receivable'
        voucher_line_pool.unlink(cr, uid, [line.id for line in voucher_obj.line_ids], context=context)
        voucher_pool.write(cr, uid, ids, {'line_ids': [], })
        voucher_id = voucher_obj.id
        invoice_obj = voucher_obj.invoice_id
        if invoice_obj:
            self.create_voucher_lines(cr, uid, ids, voucher_obj.partner_id.id, voucher_id, voucher_type, voucher_obj.journal_id.currency.id, account_type, context=context)
        else:
            self.create_voucher_lines(cr, uid, ids, voucher_obj.partner_id.id, voucher_id, voucher_type, voucher_obj.journal_id.currency.id, account_type, context=context)
        self.write(cr, uid, voucher_id, {
            'state': 'open',
            'amount': self.get_total_amount(cr, uid, None, voucher_id=voucher_id, context=context),
        })
        return True

    def create_voucher_lines(self, cr, uid, ids, partner_id, voucher_id, voucher_type, voucher_payment_currency_id, account_type, invoice_move_lines=[], context={}):
        voucher_line_pool = self.pool.get('account.voucher.line')
        reconciled_move_lines = self._get_unreconciled_move_lines(cr, uid, ids, partner_id, account_type, context=context)
        reconciled_move_lines.extend(self._get_reconciled_partial_move_lines(cr, uid, ids, partner_id, account_type, context=context))
        line_ids = []
        for move_line_id, debit, credit, date, date_maturity, amount_currency, reconcile_partial_id in reconciled_move_lines:
            if debit and voucher_type == 'payment' or credit and voucher_type == 'receipt':
                voucher_line_type = 'dr'
            else:
                voucher_line_type = 'cr'
            if move_line_id in invoice_move_lines:
                amount = voucher_line_pool.get_open_balance(cr, uid, voucher_type, voucher_payment_currency_id, move_line_id, context=context)
                is_used = True
            else:
                amount = 0
                is_used = False
            line_ids.append(voucher_line_pool.create(cr, uid, {
                                                                'voucher_id': voucher_id,
                                                                'move_line_id': move_line_id,
                                                                'amount': amount,
                                                                'is_used': is_used,
                                                                'date': date,
                                                                'date_maturity': date_maturity,
                                                                'type': voucher_line_type,
                                                                'state': 'work',

                                                            }, context=context))
        return line_ids

    def _get_unreconciled_move_lines(self, cr, uid, ids, partner_id, account_type, is_partial=False, context={}):
        if is_partial:
            reconcile_where_query = 'AND aml.reconcile_id IS NULL AND aml.reconcile_partial_id IS NOT NULL'
        else:
            reconcile_where_query = 'AND aml.reconcile_id IS NULL AND aml.reconcile_partial_id IS NULL'
        partner_query = "AND aml.partner_id = %s" % partner_id if partner_id else ''
        query = ("""
                    SELECT  aml.id,
                            aml.debit,
                            aml.credit,
                            aml.date,
                            aml.date_maturity,
                            aml.amount_currency,
                            aml.reconcile_partial_id
                    FROM account_move_line aml
                    JOIN account_account aa ON aa.id = aml.account_id
                    WHERE aml.state = 'valid' %s
                        AND aa.type = %r %s
                    """ % (reconcile_where_query, account_type, partner_query))
        cr.execute(query)
        reconciled_move_lines = cr.fetchall()
        return reconciled_move_lines

    def _get_reconciled_partial_move_lines(self, cr, uid, ids, partner_id, account_type, context={}):
        reconciled_partial_move_lines = self._get_unreconciled_move_lines(cr, uid, ids, partner_id, account_type, True, context=context)
        res_list = []
        grouped_list = {}
        for line in reconciled_partial_move_lines:
            if grouped_list.get(line[6], False):
                grouped_list[line[6]].append(line)
            else:
                grouped_list[line[6]] = [line, ]
        for key, lines in grouped_list.items():
            current_amount = 0
            lines.sort(key=lambda tup: tup[1])
            for line in lines:
                current_amount += (line[1] - line[2])
                result = line
            result = (result[0], current_amount, result[2], result[3], result[4], result[5], result[6])
            res_list.append(result)
        return res_list

    def onchange_price(self, cr, uid, ids, line_ids, partner_id=False, context=None):
        res = {
            'amount': False,
        }
        voucher_total = 0.0
        voucher_line_ids = []

        total = 0.0
        for line in line_ids:
            line_amount = 0.0
            line_amount = line[2] and line[2].get('amount', 0.0) or 0.0
            voucher_line_ids += [line[1]]
            voucher_total += line_amount

        total = voucher_total
        res.update({
            'amount': total or voucher_total
        })
        return {
            'value': res
        }

    def onchange_date(self, cr, uid, ids, date, context={}):
        period_pool = self.pool.get('account.period')
        period_id = period_pool.find(cr, uid, dt=date, context=context)
        return {'value': {'period_id': period_id and period_id[0] or None}}

    def proforma_voucher(self, cr, uid, ids, context=None):
        line_pool = self.pool.get('account.voucher.line')
        voucher_obj = self.browse(cr, uid, ids, context=context)[0]
        unused_line_ids = [line.id for line in voucher_obj.line_ids if not line.amount]
        if unused_line_ids:
            line_pool.unlink(cr, uid, unused_line_ids, context=context)
        if (abs(voucher_obj.amount) * 0.15 < abs(voucher_obj.writeoff_amount)) and voucher_obj.payment_option == 'with_writeoff':
            raise osv.except_osv('Alert!', """You cant write off more than 15% from the amount that is to be paid.

Please select the 'Keep Open' instead of 'Reconcile with write off' option from the dropdown menu and this will simply keep the difference that is not allocated to any invoices as a payment on account""")
        self.action_move_line_create(cr, uid, ids, context=context)
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for voucher_id in ids:
            wf_service.trg_create(uid, 'account.voucher', voucher_id, cr)
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def cancel_voucher(self, cr, uid, ids, context=None):
        move_line_pool = self.pool.get('account.move.line')
        reconcile_pool = self.pool.get('account.move.reconcile')
        voucher_line_pool = self.pool.get('account.voucher.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            voucher.move_id.button_cancel(context=context, check_voucher=False)
            to_reconcile = {}
            for line in voucher.move_ids:
                reconcile_ids = []
                if line.reconcile_id:
                    if to_reconcile.get(line.reconcile_id.id, False):
                        reconcile_ids = to_reconcile[line.reconcile_id.id]
                    else:
                        reconcile_ids = [aml.id for aml in line.reconcile_id.line_id]
                    reconcile_ids.remove(line.id)
                    to_reconcile[line.reconcile_id.id] = reconcile_ids
                if line.reconcile_partial_id:
                    if to_reconcile.get(line.reconcile_partial_id.id, False):
                        reconcile_ids = to_reconcile[line.reconcile_partial_id.id]
                    else:
                        reconcile_ids = [aml.id for aml in line.reconcile_partial_id.line_partial_ids]
                    reconcile_ids.remove(line.id)
                    to_reconcile[line.reconcile_partial_id.id] = reconcile_ids
            for rec_id, rec_list in to_reconcile.items():
                reconcile_pool.unlink(cr, uid, rec_id)
                if rec_list and len(rec_list) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_list, context=context)
            voucher.open_test_invoce()
            voucher.move_id.unlink()
            voucher_line_pool.unlink(cr, uid, [line.id for line in voucher.line_ids], context=context)
        self.write(cr, uid, ids, {
            'state': 'cancel',
            'move_id': False,
        }, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        for t in self.read(cr, uid, ids, ['state'], context=context):
            if t['state'] not in ('draft', 'cancel', 'open'):
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete Voucher(s) which are already opened or paid !'))
        return super(account_voucher, self).unlink(cr, uid, ids, context=context)

    def action_move_line_create(self, cr, uid, ids, context={}):
        move_pool = self.pool.get('account.move')
        for voucher in self.browse(cr, uid, ids, context=context):
            voucher.set_account_move_name()
            move_id = voucher.create_account_move()
            voucher.set_currencies()
            voucher.set_global_sign()
            voucher.make_bank_transaction(move_id)
            to_reconcile_ids = voucher.make_move_line_transactions(move_id)
            voucher.make_write_off_transaction(move_id)
            voucher.reconcile_move_lines(to_reconcile_ids)
            move_pool.post(cr, uid, [move_id], context={})
            voucher.open_test_invoce()
            voucher.write({
                'move_id': move_id,
                'state': 'posted',
                'number': self.account_move_name,
            }, context=context)
        return True

    def set_currencies(self, cr, uid, ids, context={}):
        for voucher in self.browse(cr, uid, ids, context=context):
            self.company_currency = voucher.journal_id.company_id.currency_id.id
            self.current_currency = voucher.journal_id.currency.id or self.company_currency
        return True

    def set_global_sign(self, cr, uid, ids, context={}):
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.type == 'payment':
                self.global_sign = 1
            else:
                self.global_sign = -1
            return True

    def create_account_move(self, cr, uid, ids, context={}):
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        context_multi_currency = context.copy()
        for voucher in self.browse(cr, uid, ids, context={}):
            context_multi_currency.update({'date': voucher.date})
            name = self.account_move_name
            if not voucher.reference:
                ref = name.replace('/', '')
            else:
                ref = voucher.reference

            move_dic = {
                'name': name,
                'journal_id': voucher.journal_id.id,
                'narration': voucher.narration,
                'date': voucher.date,
                'ref': ref,
                'period_id': voucher.period_id and voucher.period_id.id or False
            }
            return move_pool.create(cr, uid, move_dic)

    def set_account_move_name(self, cr, uid, ids, context={}):
        seq_pool = self.pool.get('ir.sequence')
        for voucher in self.browse(cr, uid, ids, context={}):
            if voucher.number:
                self.account_move_name = voucher.number
            elif voucher.journal_id.sequence_id:
                self.account_move_name = seq_pool.get_id(cr, uid, voucher.journal_id.sequence_id.id)
            else:
                raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal !'))

    def make_bank_transaction(self, cr, uid, ids, move_id, context={}):
        for voucher in self.browse(cr, uid, ids, context={}):
            if voucher.amount:
                return self.make_trunsaction(cr, uid, ids,
                                      voucher, move_id, self.account_move_name,
                                      -self.global_sign * voucher.amount, self.current_currency, None,
                                      voucher.journal_id.default_credit_account_id.id or voucher.journal_id.default_debit_account_id.id, None, False, context=context)
            else:
                return None

    def make_move_line_transactions(self, cr, uid, ids, move_id, context={}):
        for voucher in self.browse(cr, uid, ids, context={}):
            to_reconcile_ids = []
            for line in voucher.line_ids:
                if line.amount != 0 and line.state != 'draft' and line.move_line_id:
                    reconcile_id = []
                    exchange_line = None
                    target_move_line = self.make_trunsaction(cr, uid, ids,
                                            voucher, move_id, self.account_move_name, self.global_sign * line.amount, self.current_currency, line.move_line_id.id,
                                            line.move_line_id.account_id.id, None,
                                            True, context=context)
                    reconcile_id.extend(target_move_line)
                    if line.amount == line.amount_unreconciled:
                        exchange_line = self._create_write_off_exchage_lines(cr, uid, ids,
                                                                voucher, move_id,
                                                                reconcile_id,
                                                                context=context)
                    if exchange_line:
                        reconcile_id.append(exchange_line)
                    to_reconcile_ids.append(reconcile_id)
            return to_reconcile_ids

    def make_write_off_transaction(self, cr, uid, ids, move_id, context={}):
        move_pool = self.pool.get('account.move')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.type == 'payment':
                writeoff_account = voucher.partner_id.property_account_payable.id
            else:
                writeoff_account = voucher.partner_id.property_account_receivable.id

            writeoff_amount = sum([line.credit - line.debit for line in move_pool.browse(cr, uid, move_id, context=context).line_id])
            for line in [line for line in voucher.line_ids if line.move_line_id]:
                writeoff_amount = sum([line.credit - line.debit for line in move_pool.browse(cr, uid, move_id, context=context).line_id])
                if round(writeoff_amount, 2) != 0:
                    if voucher.payment_option == 'with_writeoff':
                        writeoff_account = voucher.writeoff_acc_id.id
                    analytic_id = voucher.analytic_id and voucher.analytic_id.id or None
                    self.make_trunsaction(cr, uid, ids, voucher, move_id, self.account_move_name,
                                writeoff_amount, self.company_currency, None,
                                writeoff_account, analytic_id, False, context=context)

            if (not voucher.line_ids or [line for line in voucher.line_ids if not line.move_line_id]) and voucher.payment_option != 'with_writeoff' and writeoff_amount != 0:

                analytic_id = voucher.analytic_id and voucher.analytic_id.id or None
                self.make_trunsaction(cr, uid, ids, voucher, move_id, self.account_move_name,
                            writeoff_amount, self.company_currency, None,
                            writeoff_account, analytic_id, False, context=context)
        return True

    def reconcile_move_lines(self, cr, uid, ids, to_reconcile_ids, context={}):
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            for reconcile_ids in to_reconcile_ids:
                if len(set([line.account_id.id for line in move_line_pool.browse(cr, uid, reconcile_ids, context=context)])) == 1:
                    move_line_pool.reconcile_partial(cr, uid, reconcile_ids, context=context)

    def open_test_invoce(self, cr, uid, ids, context={}):
        wf_service = netsvc.LocalService("workflow")
        for voucher in self.browse(cr, uid, ids, context=context):
            for line in voucher.line_ids:
                if line.move_line_id.invoice:
                    wf_service.trg_validate(uid, 'account.invoice', line.move_line_id.invoice.id, 'open_test', cr)
        return True

    def make_trunsaction(self, cr, uid, ids,
                         voucher, move_id, name, amount, currency_id, payed_line_id, account, analytic_id,  wil_be_reconciled,
                         context={}):
        move_line_pool = self.pool.get('account.move.line')
        currency_pool = self.pool.get('res.currency')
        amount_in_company_currency = currency_pool.compute_to_date(cr, uid,
                                               currency_id,
                                               self.company_currency,
                                               amount,
                                               context=context,
                                               date=voucher.date)
        if currency_id != self.current_currency != self.company_currency:
            amount_in_current_currency = currency_pool.compute_to_date(cr, uid,
                                                currency_id,
                                                self.current_currency,
                                                amount,
                                                context=context,
                                                date=voucher.date)
        else:
            amount_in_current_currency = amount
        if amount_in_company_currency > 0:
            credit = 0
            debit = amount_in_company_currency
        else:
            credit = abs(amount_in_company_currency)
            debit = 0

        move_line = {
            'name': name,
            'move_id': move_id,
            'voucher_id': voucher.id,
            'debit': debit,
            'credit': credit,
            'account_id': account,
            'analytic_account_id': analytic_id,
            'journal_id': voucher.journal_id.id,
            'period_id': voucher.period_id.id,
            'partner_id': voucher.partner_id.id,
            'currency_id': self.company_currency != self.current_currency and self.current_currency or False,
            'amount_currency': self.company_currency != self.current_currency and amount_in_current_currency or 0.0,
            'date': voucher.date,
        }
        result_line = move_line_pool.create(cr, uid, move_line)
        if wil_be_reconciled and payed_line_id:
            return [result_line, payed_line_id]
        else:
            return result_line

    def _create_write_off_exchage_lines(self, cr, uid, ids, voucher_obj,
                                        move_id, line_ids, context={}):
        move_line_pool = self.pool.get('account.move.line')
        currency_pool = self.pool.get('res.currency')
        total_debit = 0.0
        total_credit = 0.0
        move_line_account = None
        all_move_line_ids = []
        for line in move_line_pool.browse(cr, uid, line_ids, context=context):
            if line.reconcile_partial_id:
                all_move_line_ids.extend([ml.id for ml in line.reconcile_partial_id.line_partial_ids])
            else:
                all_move_line_ids.append(line.id)
        for move_line in move_line_pool.browse(cr, uid, all_move_line_ids, context=context):
            total_debit += move_line.debit
            total_credit += move_line.credit
            move_line_account = move_line.account_id.id
        difference = currency_pool.round(cr, uid, move_line.company_id.currency_id, total_debit - total_credit)
        second_move_line_id = None
        if abs(difference) > 0:
            move_line = {
                'period_id': voucher_obj.period_id.id,
                'name': 'Exchange differences on foreign currency payment',
                'move_id': move_id,
                'partner_id': voucher_obj.partner_id.id,
                'date': voucher_obj.date,
                'journal_id': voucher_obj.journal_id.id,
                'move_id': move_id,
                'currency_id': None,
                'amount_currency': None,
            }
            first_move_line = move_line.copy()
            debit = difference if difference > 0 else 0
            credit = -difference if difference < 0 else 0
            first_move_line.update({
                'debit': debit,
                'credit': credit,
                'account_id': self.get_ex_diff_account(cr, uid, ids, debit, credit, voucher_obj.journal_id.company_id.id, context=context),
            })
            move_line_pool.create(cr, uid, first_move_line, context=context)
            second_move_line = move_line.copy()
            second_move_line.update({
                'account_id': move_line_account,
                'credit': difference if difference > 0 else 0,
                'debit': -difference if difference < 0 else 0,
            })
            second_move_line_id = move_line_pool.create(cr, uid, second_move_line, context=context)
        return second_move_line_id

    def get_ex_diff_account(self, cr, uid, ids, debit, credit, company_id, context={}):
        company_pool = self.pool.get('res.company')
        company_obj = company_pool.browse(cr, uid, company_id, context=context)
        if credit:
            if company_obj.exchange_gains:
                return company_obj.exchange_gains.id
            else:
                raise osv.except_osv('Alert!', 'Define "Exchange Gains" account for current company')
        if debit:
            if company_obj.exchange_losses:
                return company_obj.exchange_losses.id
            else:
                raise osv.except_osv('Alert!', 'Define "Exchange Losses" account for current company')

    def copy(self, cr, uid, id, default={}, context={}):
        period_pool = self.pool.get('account.period')
        default.update({
            'state': 'draft',
            'number': False,
            'move_id': False,
            'line_cr_ids': False,
            'line_dr_ids': False,
            'reference': False
        })
        if 'date' not in default:
            default['date'] = time.strftime('%Y-%m-%d')
        period_id = period_pool.find(cr, uid, dt=default['date'], context=context)
        default['period_id'] = period_id[0]
        return super(account_voucher, self).copy(cr, uid, id, default, context)

    def precompute(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {}, context=context)
        for voucher in self.browse(cr, uid, ids, context=context):
            total_voucher_amount = 0
            for line in voucher.line_ids:
                if line.state != 'draft':
                    total_voucher_amount += line.amount
        self.write(cr, uid, ids, {'state': 'precomputed', 'amount': total_voucher_amount}, context=context)
        return True

    def compute(self, cr, uid, ids, context={}):
        for voucher in self.browse(cr, uid, ids, context=context):
            writeoff_account = self.get_write_off_account(cr, uid, ids, voucher.type, voucher.writeoff_amount, voucher.journal_id.company_id.id, context=context)
            self.write(cr, uid, voucher.id, {'writeoff_acc_id': writeoff_account})
        return True

    def get_write_off_account(self, cr, uid, ids, voucher_type, difference, company_id, context={}):
        company_pool = self.pool.get('res.company')
        company_obj = company_pool.browse(cr, uid, company_id, context=context)
        if voucher_type == 'payment' and difference < 0 or voucher_type == 'receipt' and difference > 0:
            if company_obj.writeoff_gains:
                return company_obj.writeoff_gains.id
            else:
                raise osv.except_osv('Alert!', 'Define "Writeoff Gains" account for current company')
        else:
            if company_obj.writeoff_losses:
                return company_obj.writeoff_losses.id
            else:
                raise osv.except_osv('Alert!', 'Define "Writeoff Losses" account for current company')

    def reselect(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'open'})
        return True

    def to_proforma(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'proforma'})
        return True

account_voucher()


class account_voucher_line(osv.osv):
    _name = 'account.voucher.line'
    _inherit = 'account.voucher.line'
    _description = 'Voucher Lines'
    _order = "move_line_id"

    def _compute_balance(self, cr, uid, ids, name, args, context={}):
        currency_pool = self.pool.get('res.currency')
        rs_data = {}
        for line in self.browse(cr, uid, ids, context=context):
            res = {}
            move_line = line.move_line_id
            if not move_line:
                res['amount_currency'] = 0
                res['amount_original'] = 0
                res['amount_unreconciled'] = 0
                rs_data[line.id] = res
                continue
            voucher_type = line.voucher_id.type
            sign = self._get_line_sign(cr, uid, voucher_type, move_line.id, context=context)
            ctx = context.copy()
            ctx.update({'date': line.voucher_id.date})
            date = line.move_line_id and line.move_line_id.date or time.strftime('%Y-%m-%d')
            company_currency = line.voucher_id.journal_id.company_id.currency_id.id
            voucher_currency = line.voucher_id.journal_id.currency.id or company_currency
            move_line = line.move_line_id
            original_amount = (move_line.credit - move_line.debit) or 0.0
            if voucher_currency == move_line.currency_id.id and move_line.amount_currency != 0:
                original_amount = move_line.amount_currency
            else:
                original_amount = currency_pool.compute_to_date(cr, uid, company_currency, voucher_currency, original_amount, date=date, context=ctx, round=False)
            res['amount_currency'] = self._get_amount_currency(cr, uid, ids, line.move_line_id, sign, context=context)
            res['amount_original'] = sign * abs(original_amount)
            res['amount_unreconciled'] = self.get_open_balance(cr, uid, voucher_type, voucher_currency, move_line.id, ctx)
            rs_data[line.id] = res
        return rs_data

    def _get_line_sign(self, cr, uid, voucher_type, move_line_id, context={}):
        move_line = self.pool.get('account.move.line').browse(cr, uid, move_line_id, context=context)
        if (voucher_type == 'payment' and move_line.credit - move_line.debit >= 0) or (voucher_type == 'receipt' and move_line.credit - move_line.debit <= 0):
            sign = 1
        else:
            sign = -1
        return sign

    def _get_amount_currency(self, cr, uid, ids, move_line_obj, sign, context={}):
        if move_line_obj.currency_id and move_line_obj.amount_currency != 0:
            return "%s %.2f" % (move_line_obj.currency_id.symbol, sign * abs(move_line_obj.amount_currency), )
        else:
            return "%s %.2f" % (move_line_obj.company_id.currency_id.symbol, sign * abs(move_line_obj.debit - move_line_obj.credit), )

    def get_open_balance(self, cr, uid, voucher_type, voucher_payment_currency_id, move_line_id, context={}):
        sign = self._get_line_sign(cr, uid, voucher_type, move_line_id, context=context)
        move_line = self.pool.get('account.move.line').browse(cr, uid, move_line_id, context=context)
        company_currency_id = move_line.company_id.currency_id.id
        amount_unreconciled = 0
        if move_line.reconcile_partial_id:
            for payment_line in move_line.reconcile_partial_id.line_partial_ids:
                amount_unreconciled += self._move_line_amount_currency(cr, uid, payment_line, voucher_payment_currency_id, company_currency_id, context=context)
            if voucher_type == 'payment':
                amount_unreconciled *= -1
            return amount_unreconciled
        else:
            amount_unreconciled += self._move_line_amount_currency(cr, uid, move_line, voucher_payment_currency_id, company_currency_id, context=context)
            return sign * abs(amount_unreconciled)

    def _move_line_amount_currency(self, cr, uid, move_line, voucher_payment_currency_id, company_currency_id, context={}):
        currency_pool = self.pool.get('res.currency')
        if company_currency_id == voucher_payment_currency_id:
            result = move_line.debit - move_line.credit
        elif move_line.currency_id.id == voucher_payment_currency_id and move_line.amount_currency != 0:
            result = move_line.amount_currency
        else:
            result = currency_pool.compute_to_date(cr, uid, company_currency_id, voucher_payment_currency_id, move_line.debit - move_line.credit, context=context, date=context['date'])
        return result

    def mass_pick_use(self, cr, uid, ids, context={}):
        """Used in right click to apply 'use' checkbox to selected records"""
        for line in self.browse(cr, uid, ids, context=context):
            if line.voucher_id.state != 'open':
                continue
            use = not line.is_used
            vals = self.onchange_is_used(cr, uid, ids, use, line.amount_unreconciled)['value']
            vals.update({'is_used': use})
            line.write(vals)
        return {'type': 'ir.actions.act_window_refresh'}

    def onchange_is_used(self, cr, uid, ids, is_used, amount_unreconciled, context={}):
        res = {}
        if is_used:
            res['state'] = 'work'
            res['amount'] = amount_unreconciled
        else:
            res['state'] = 'draft'
            res['amount'] = 0
        return {'value': res}

    _columns = {
        'voucher_id':       fields.many2one     ('account.voucher',
                                                 'Voucher',
                                                 required=True,
                                                 ondelete='cascade',
                                                ),
        'name':             fields.char         ('Description',
                                                 size=256,
                                                ),
        'account_id':       fields.related     ('move_line_id',
                                                'account_id',
                                                 type='many2one',
                                                 relation='account.account',
                                                 string='Account',
                                                 readonly=True,
                                                ),
        'partner_id':       fields.related      ('voucher_id',
                                                 'partner_id',
                                                 type='many2one',
                                                 relation='res.partner',
                                                 string='Partner',
                                                ),
        'amount':           fields.float        ('Amount',
                                                 digits_compute=dp.get_precision('Account'),
                                                ),
        'type':             fields.selection    ([('dr', 'Debit'),
                                                  ('cr', 'Credit'),
                                                 ],
                                                 'Cr/Dr',
                                                ),
        'move_line_id':     fields.many2one     ('account.move.line',
                                                 'Journal Item',
                                                ),
        'company_id':     fields.many2one       ('res.company',
                                                 'Company',
                                                ),
        'date_original':    fields.related      ('move_line_id',
                                                 'date',
                                                 type='date',
                                                 relation='account.move.line',
                                                 string='Date',
                                                 readonly=True,
                                                ),
        'date_due':         fields.related      ('move_line_id',
                                                 'date_maturity',
                                                 type='date',
                                                 relation='account.move.line',
                                                 string='Due Date',
                                                 readonly=True),
        'amount_currency':  fields.function     (_compute_balance,
                                                 string='Currency amount',
                                                 method=True,
                                                 multi='dc',
                                                 store=False,
                                                 digits_compute=dp.get_precision('Account'),
                                                 type='char'),
        'amount_original':  fields.function     (_compute_balance,
                                                 method=True,
                                                 multi='dc',
                                                 type='float',
                                                 string='Original Amount',
                                                 store=False,
                                                 digits_compute=dp.get_precision('Account'),
                                                ),
        'amount_unreconciled': fields.function  (_compute_balance,
                                                 method=True,
                                                 multi='dc',
                                                 type='float',
                                                 string='Open Balance',
                                                 store=True,
                                                 digits_compute=dp.get_precision('Account'),
                                                ),
        'state':            fields.selection    ([('draft', 'Draft'),
                                                  ('work', 'Working'),
                                                 ],
                                                 'State',
                                                ),
        'voucher_state':    fields.related      ('voucher_id',
                                                 'state',
                                                 relation='account.voucher',
                                                 string='Voucher State',
                                                 readonly=True,
                                                 type='char'
                                                ),
        'voucher_type':    fields.related      ('voucher_id',
                                                 'type',
                                                 relation='account.voucher',
                                                 string='Voucher State',
                                                 readonly=True,
                                                 type='char'
                                                ),
        'sign':     fields.integer              ('Sign',
                                                ),
        'is_used':  fields.boolean              ('Use',
                                                ),
    }
    _defaults = {
        'name': ''
    }

    def default_get(self, cr, user, fields_list, context=None):
        """
        Returns default values for fields
        @param fields_list: list of fields, for which default values are required to be read
        @param context: context arguments, like lang, time zone

        @return: Returns a dict that contains default values for fields
        """
        if context is None:
            context = {}
        journal_id = context.get('journal_id', False)
        partner_id = context.get('partner_id', False)
        journal_pool = self.pool.get('account.journal')
        partner_pool = self.pool.get('res.partner')
        values = super(account_voucher_line, self).default_get(cr, user, fields_list, context=context)
        if (not journal_id) or ('account_id' not in fields_list):
            return values
        journal = journal_pool.browse(cr, user, journal_id, context=context)
        account_id = False
        ttype = 'cr'
        if journal.type in ('sale', 'sale_refund'):
            account_id = journal.default_credit_account_id and journal.default_credit_account_id.id or False
            ttype = 'cr'
        elif journal.type in ('purchase', 'expense', 'purchase_refund'):
            account_id = journal.default_debit_account_id and journal.default_debit_account_id.id or False
            ttype = 'dr'
        elif partner_id:
            partner = partner_pool.browse(cr, user, partner_id, context=context)
            if context.get('type') == 'payment':
                ttype = 'dr'
                account_id = partner.property_account_payable.id
            elif context.get('type') == 'receipt':
                account_id = partner.property_account_receivable.id

        values.update({
            'account_id': account_id,
            'type': ttype
        })
        return values

    def to_draft(self, cr, uid, ids, context={}):
        self.fill_toggle(cr, uid, ids, context=context, unset=True)
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def to_work(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'work'}, context=context)

    def fill_toggle(self, cr, uid, ids, context={}, unset=False):
        voucher_pool = self.pool.get('account.voucher')
        voucher_line_pool = self.pool.get('account.voucher.line')
        for line in self.browse(cr, uid, ids, context=context):
            line_amount = 0
            if line.amount:
                if unset or line.amount == line.amount_unreconciled:
                    line_amount = 0
                else:
                    line_amount = line.amount
            elif not unset and not line.amount:
                line_amount = line.amount_unreconciled
            voucher_line_pool.write(cr, uid, line.id, {'amount': line_amount}, context=context)
            voucher_amount = sum([voucher_line.amount for voucher_line in voucher_pool.browse(cr, uid, line.voucher_id.id, context=context).line_ids])
            voucher_pool.write(cr, uid, line.voucher_id.id, {'amount': voucher_amount}, context=context)
            self.write(cr, uid, ids, {'state': 'work'}, context=context) #vadim over-ride - needs cleaning.
        return True

account_voucher_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
