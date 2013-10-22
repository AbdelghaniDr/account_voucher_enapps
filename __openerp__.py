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

{
    "name" : "Enapps Accounting Voucher",
    "version" : "1.0",
    "author" : 'Enapps LTD',
    "description": """account_voucher module by Enapps is a full rewrite of the original account_voucher with clean code and improved functionality. This module is to be used to record single payment transactions to suppliers or from customers. This functionality will be very familiar to Quickbooks and Oracle users. The module fully supports multicurrency. For enhancements and further customisations please contact Enapps: openerp@enapps.co.uk

This module is compatible with OpenERP v6.0 and v6.1
    
This module can be installed on top of the OpenERP standard account_voucher and will replace all standard functionality.
        
Note: Uninstall of this module is not supported - test first in your development system.
        
Configuration:
1) Installing this module will add 4 configurable write-off accounts against your company record.  Assign your default accounts for Exchange rate gains and losses, and write-off gains and losses under Menu --> Administration --> Companies --> Companies

Usage:
1) Open either Customer or Supplier Payment
2) Select the account you would like to use to pay from/into
3) Enter the payment date
4) Select the Customer/Supplier record
5) Click on 'Get Open Entries' - all open invoices and credits will load in the Outstanding Transactions list.
6) Tick the 'Use' check-box to allocate payment to a line.  Alternatively you can enter in an amount manually.
7) Click on the 'Compute' button.
8) Enter your payment reference
9) If necessary you can choose to 'Keep Open' or 'Reconcile with Write-Off' for your payment.
* If you have chosen 'Reconcile with Write-Off' and modify the 'Amount to pay' so the total is either higher or lower than the amount allocated in 'Outstanding Transactions', the difference will be automatically written off to your configured write-off gains or losses account.
* When modifying the 'Amount to pay' click on 'Re-compute' to show the 'Payment diff' calculation under 'Payment Options'.
* If you are processing a payment in a currency other than your base currency, the exchange rate difference will be automatically written off to your configured exchange rate gain/loss accounts using the exchange rate at or closest to the payment date.
10) If you would like to modify your payment selection, click 'Reselect lines to pay' to re-open the 'Outstanding Transactions' list.
11) Lastly, click 'Confirm Payment'.
12) Review your Journal Entries under the Journal Items tab.

Usage from 'Pay Invoice' within account.invoice:
1) Click 'Pay Invoice' from the Invoice screen
2) Select the account you would like to use to pay from/into
3) Click on 'Get Open Entries'
* the invoice you were previously viewing will be automatically selected

Other information:
* When you select 'Get Open Entries' you will be retrieving all uncleared Invoices and Credits.  If you would like to reconcile an Invoice against a Credit, simply tick the 'Use' box for each line and then click 'Compute'.

    """,
    "category": 'Accounting & Finance',
    "website" : "http://www.enapps.co.uk",
    "depends" : ["account","account_voucher"],
    "init_xml" : [],

    "demo_xml" : [],

    "update_xml" : [
        "security/ir.model.access.csv",
        "account_voucher_sequence.xml",
        "wizard/account_voucher_unreconcile_view.xml",
        "voucher_payment_receipt_view.xml",
        "account_voucher_view.xml",
        "account_voucher_pay_invoice.xml",
        "account_move_line_view.xml",
        "company_view.xml",
        "security/account_voucher_security.xml",
        "account_voucher_installer.xml",
        'data/ir_actions_object.xml',
    ],
    "active": False,
    "installable": True,
    'images': ['images/supplier_payment.png','images/supplier_payment_web.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
