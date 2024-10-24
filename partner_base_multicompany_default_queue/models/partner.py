# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class Partner(models.Model):

    _inherit = "res.partner"

    def _propagate_property_fields(self):
        # Adding a call with_delay() make an aync propagation of the property fields
        if (
            self.env.context.get("force_property_propagation")
            and not self.env.context.get("property_propagation") == "enqueued"
        ):
            # changing the context to avoid infinite loop
            self_enqueued = self.with_context(property_propagation="enqueued")
            return (
                super(Partner, self_enqueued).with_delay()._propagate_property_fields()
            )
        else:
            return super()._propagate_property_fields()
