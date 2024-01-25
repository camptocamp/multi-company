# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

from .. import post_init_hook


class TestPartnerMultiCompany(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env

        cls.company_1 = cls.env["res.company"].create({"name": "Test company 1"})
        cls.company_2 = cls.env["res.company"].create({"name": "Test company 2"})

    def test_sale_stock_warehouse_multicompany(self):
        post_init_hook(self.env.cr, self.registry)
        warehouse_1 = (
            self.env["stock.warehouse"]
            .with_company(self.company_1)
            .create(
                {
                    "name": "Base Warehouse",
                    "reception_steps": "one_step",
                    "delivery_steps": "pick_ship",
                    "code": "BWH",
                    "company_ids": [(6, 0, (self.company_2 + self.company_1).ids)],
                }
            )
        )
        self.sale_order = (
            self.env["sale.order"]
            .with_company(self.company_1)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_12").id,
                    "warehouse_id": warehouse_1.id,
                }
            )
        )
