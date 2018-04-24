# Copyright 2013-Today Odoo SA
# Copyright 2016 Chafique DELLI @ Akretion
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def inter_company_create_invoice(
            self, dest_company, dest_inv_type, dest_journal_type):
        res = super(AccountInvoice, self).inter_company_create_invoice(
            dest_company, dest_inv_type, dest_journal_type)
        if dest_inv_type == 'in_invoice':
            # Link intercompany purchase order with intercompany invoice
            self._link_invoice_purchase(res['dest_invoice'])
        return res

    @api.multi
    def _link_invoice_purchase(self, dest_invoice):
        self.ensure_one()
        vals = {}
        if dest_invoice.state not in ['draft', 'cancel']:
            vals['invoiced'] = True
        for line in dest_invoice.invoice_line_ids:
            vals['invoice_lines'] = [(4, line.id)]
            line.auto_invoice_line_id.sale_line_ids.mapped(
                'auto_purchase_line_id').update(vals)
