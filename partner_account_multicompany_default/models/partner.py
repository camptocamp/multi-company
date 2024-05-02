# Copyright 2023 Moduon Team S.L.
# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
import logging
from collections import defaultdict
from functools import reduce
from itertools import groupby
from operator import itemgetter, or_

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    def _propagate_multicompany_account(self, field):
        companies = self._get_alien_companies()
        # Map alien accounts by company and code
        alien_accounts = self.env["account.account"].search(
            [
                ("company_id", "in", companies.ids),
                (
                    "code",
                    "in",
                    self[field].mapped("code"),
                ),
            ]
        )
        # Gain access to all companies of current user
        self = self.with_context(
            allowed_company_ids=self.env.company.ids + companies.ids
        )
        accounts_map = defaultdict(dict)
        for account in alien_accounts:
            accounts_map[account.company_id.id][account.code] = account.id
        # Group partner by account
        for good_account, partners_grouper in groupby(self, itemgetter(field)):
            partners = reduce(or_, partners_grouper)
            # Propagate account to alien companies if possible
            target_code = good_account.code
            for alien_company in companies:
                try:
                    # False is a valid value, if you want to remove the account
                    target_account_id = (
                        target_code and accounts_map[alien_company.id][target_code]
                    )
                except KeyError:
                    _logger.warning(
                        "Not propagating account to company because it does "
                        "not exist there: partners=%s, company=%s, account=%s",
                        partners,
                        alien_company,
                        target_code,
                    )
                    continue
                partners.with_company(alien_company)[field] = target_account_id

    def _propagate_multicompany_value(self, field):
        """Set the same value accross all companies"""
        companies = self._get_alien_companies()
        # Gain access to all companies of current user
        self = self.with_context(
            allowed_company_ids=self.env.company.ids + companies.ids
        )
        # Group partner by account
        for value, partners_grouper in groupby(self, itemgetter(field)):
            partners = reduce(or_, partners_grouper)
            # Propagate value to alien companies
            for alien_company in companies:
                partners.with_company(alien_company)[field] = value

    def _get_alien_companies(self):
        alien_companies = self.env.user.company_ids - self.env.company
        if not alien_companies:
            raise UserError(
                _(
                    "There are no other companies to propagate to. "
                    "Make sure you have access to other companies."
                )
            )
        return alien_companies

    def _propagate_multicompany_field(self, field):
        """Set the same account for all companies.

        Args:
            field (str):
                The field to propagate. E.g. "property_account_payable_id"
                or "property_account_receivable_id".
        """
        sorted_partners = (self - self.filtered("company_id")).sorted(field)
        if self and not sorted_partners:
            raise UserError(
                _("Only multi-company partner can be propagated to other companies.")
            )
        if self._fields[field].comodel_name == "account.account":
            sorted_partners._propagate_multicompany_account(field)
        else:
            sorted_partners._propagate_multicompany_value(field)

    def propagate_multicompany_account_payable(self):
        self._propagate_multicompany_field("property_account_payable_id")

    def propagate_multicompany_account_receivable(self):
        self._propagate_multicompany_field("property_account_receivable_id")

    def propagate_multicompany_account_position(self):
        self._propagate_multicompany_field("property_account_position_id")

    @api.model_create_multi
    def create(self, vals_list):
        """Propagate accounts to other companies always, on creation."""
        res = super().create(vals_list)
        multicompany_partners = res - res.filtered("company_id")
        payable_partners = multicompany_partners.filtered("property_account_payable_id")
        receivable_partners = multicompany_partners.filtered(
            "property_account_receivable_id"
        )
        position_partners = multicompany_partners.filtered(
            "property_account_position_id"
        )
        # Skip if no account was selected
        if not payable_partners and not receivable_partners and not position_partners:
            return res
        # Skip if user has access to only one company
        alien_user_companies = self.env.user.company_ids - self.env.company
        if not alien_user_companies:
            return res
        # Propagate account to other companies by default
        payable_partners.propagate_multicompany_account_payable()
        receivable_partners.propagate_multicompany_account_receivable()
        position_partners.propagate_multicompany_account_position()
        return res
