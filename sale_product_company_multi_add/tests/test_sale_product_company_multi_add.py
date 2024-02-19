# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests import common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSaleProductCompanyMultiAdd(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env

    def test_sale_product_company(self):
        result = self.env["sale.order"].get_view(
            self.env.ref("sale_product_multi_add.view_import_product_to_sale").id,
            "form",
        )
        doc = etree.XML(result["arch"])
        field = doc.xpath("//field[@name='products']")
        domain = field[0].get("domain")
        self.assertTrue(
            "'|', ('sale_ok_company_ids', 'in', sale_company_id), "
            "('sale_ok_company_ids', '=', False)" in domain
        )
