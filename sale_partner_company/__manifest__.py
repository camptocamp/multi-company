# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "sale partner companyy",
    "summary": "Set sale company from partner",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sale Management",
    "website": "https://github.com/OCA/multi-company",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "data": [
        "views/partner_view.xml",
    ],
    "depends": [
        "sale_stock",
        "delivery",
    ],
}
