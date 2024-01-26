# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Warehouse(models.Model):
    _inherit = ["multi.company.abstract", "stock.warehouse"]
    _name = "stock.warehouse"

    def _check_multiwarehouse_group(self):
        # Disable the method as company_id is not stored anymore.
        # Also we won't rely on this method to configure user groups properly.
        pass
