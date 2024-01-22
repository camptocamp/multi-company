# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    company_ids = fields.Many2many(
        string="Companies",
        comodel_name="res.company",
    )
