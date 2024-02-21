# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    company_id = fields.Many2one(
        compute="_compute_company_id", store=True, precompute=True
    )

    @api.depends("partner_id.sale_company_id")
    def _compute_company_id(self):
        for sale in self:
            if sale.partner_id.sale_company_id:
                sale.company_id = sale.partner_id.sale_company_id
            else:
                sale.company_id = self.env.company
