# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import SUPERUSER_ID, api

from odoo.addons.base_multi_company.hooks import set_security_rule


def post_init_hook(cr, registry, vals=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    set_security_rule(env, "stock.stock_warehouse_comp_rule")
    # Copy company values
    model = env["stock.warehouse"]
    table_name = model._fields["company_ids"].relation
    column1 = model._fields["company_ids"].column1
    column2 = model._fields["company_ids"].column2
    SQL = """
        INSERT INTO {}
        ({}, {})
        SELECT id, company_id FROM {} WHERE company_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """.format(
        table_name,
        column1,
        column2,
        model._table,
    )
    env.cr.execute(SQL)
