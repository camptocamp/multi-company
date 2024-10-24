# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import api, models


class Base(models.AbstractModel):

    _inherit = "base"

    @api.model
    def _job_prepare_context_before_enqueue_keys(self):
        """Keys to keep in context of stored jobs
        Empty by default for backward compatibility.
        """
        return super()._job_prepare_context_before_enqueue_keys() + (
            "property_propagation",
        )
