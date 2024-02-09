# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id, view_type, **options)
        if view_type == "form":
            order_xml = etree.XML(res["arch"])
            product_id_fields = order_xml.xpath("//field[@name='product_template_id']")
            if product_id_fields:
                product_id_field = product_id_fields[0]
                domain = product_id_field.get("domain", "[]")
                domain = domain.replace(
                    "('sale_ok', '=', True)",
                    "('sale_ok', '=', True), '|', "
                    "('sale_ok_company_ids', 'in', parent.company_id), "
                    "('sale_ok_company_ids', '=', False)",
                )
                product_id_field.attrib["domain"] = domain
                res["arch"] = etree.tostring(order_xml)
        return res
