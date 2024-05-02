# Copyright 2023 Moduon Team S.L.
# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class ProductDefaultAccountsCase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # An payable account with same code on both companies
        cls.account_payable_a1 = cls.env["account.account"].create(
            {
                "name": "Payable A1",
                "code": "PAY.A",
                "account_type": "liability_payable",
                "company_id": cls.company_data["company"].id,
            }
        )
        cls.account_payable_a2 = cls.env["account.account"].create(
            {
                "name": "Payable A2",
                "code": "PAY.A",
                "account_type": "liability_payable",
                "company_id": cls.company_data_2["company"].id,
            }
        )
        # An payable account available only on company 1
        cls.account_payable_b1 = cls.env["account.account"].create(
            {
                "name": "Payable B1",
                "code": "PAY.B",
                "account_type": "liability_payable",
                "company_id": cls.company_data["company"].id,
            }
        )
        # An receivable account with same code on both companies
        cls.account_receivable_a1 = cls.env["account.account"].create(
            {
                "name": "Receivable A1",
                "code": "REC.A",
                "account_type": "asset_receivable",
                "company_id": cls.company_data["company"].id,
            }
        )
        cls.account_receivable_a2 = cls.env["account.account"].create(
            {
                "name": "Receivable A2",
                "code": "REC.A",
                "account_type": "asset_receivable",
                "company_id": cls.company_data_2["company"].id,
            }
        )
        # An receivable account available only on company 1
        cls.account_receivable_b1 = cls.env["account.account"].create(
            {
                "name": "Receivable B1",
                "code": "REC.B",
                "account_type": "asset_receivable",
                "company_id": cls.company_data["company"].id,
            }
        )

        cls.fiscal_position_a = cls.env["account.fiscal.position"].create(
            {
                "name": "Fiscal Pos A",
            }
        )

    def test_creation_propagation(self):
        """Accounts and fiscal position are propagated on creation."""
        env = self.env.user.with_company(self.company_data["company"].id).env
        partner = env["res.partner"].create(
            {
                "name": "Test Partner",
                "property_account_payable_id": self.account_payable_a1.id,
                "property_account_receivable_id": self.account_receivable_a1.id,
                "property_account_position_id": self.fiscal_position_a.id,
            }
        )
        partner_cp2 = partner.with_company(self.company_data_2["company"].id)
        self.assertEqual(
            partner_cp2.property_account_payable_id, self.account_payable_a2
        )
        self.assertEqual(
            partner_cp2.property_account_receivable_id, self.account_receivable_a2
        )
        self.assertEqual(
            partner_cp2.property_account_position_id, self.fiscal_position_a
        )

    def test_creation_no_propagation(self):
        """Accounts are not propagated on creation if they don't exist.
        (Fiscal positions are shared so it doesn't apply to it)
        """
        env = self.env.user.with_company(self.company_data["company"].id).env
        partner = env["res.partner"].create(
            {
                "name": "Test Partner",
                "property_account_payable_id": self.account_payable_b1.id,
                "property_account_receivable_id": self.account_receivable_b1.id,
            }
        )
        partner_cp2 = partner.with_company(self.company_data_2["company"].id)
        test_codes = ["PAY.A", "PAY.B", "REC.A"]
        # We expect account set by default but not modified
        self.assertNotIn(partner_cp2.property_account_payable_id.code, test_codes)
        self.assertNotIn(partner_cp2.property_account_receivable_id.code, test_codes)

    def test_action_button_propagation(self):
        """Accounts and fiscal position are propagated when user chooses to."""
        env = self.env.user.with_company(self.company_data["company"].id).env
        # A product created without accounts
        partner = env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        test_codes = ["PAY.A", "PAY.B", "REC.A"]
        self.assertNotIn(partner.property_account_payable_id.code, test_codes)
        self.assertNotIn(partner.property_account_receivable_id.code, test_codes)
        partner_cp2 = partner.with_company(self.company_data_2["company"].id)
        # After writing accounts, they are still not propagated
        partner.write(
            {
                "property_account_payable_id": self.account_payable_a1.id,
                "property_account_receivable_id": self.account_receivable_a1.id,
                "property_account_position_id": self.fiscal_position_a.id,
            }
        )
        self.assertNotEqual(
            partner_cp2.property_account_payable_id.code, self.account_payable_a1.code
        )
        self.assertNotIn(
            partner_cp2.property_account_receivable_id.code,
            self.account_receivable_a1.code,
        )
        self.assertFalse(partner_cp2.property_account_position_id)
        # Propagating payable account
        partner.propagate_multicompany_account_payable()
        self.assertEqual(
            partner_cp2.property_account_payable_id, self.account_payable_a2
        )
        self.assertNotIn(
            partner_cp2.property_account_receivable_id.code,
            self.account_receivable_a1.code,
        )
        # Propagating receivable account
        partner.propagate_multicompany_account_receivable()
        self.assertEqual(
            partner_cp2.property_account_payable_id, self.account_payable_a2
        )
        self.assertEqual(
            partner_cp2.property_account_receivable_id, self.account_receivable_a2
        )
        # Propagating fiscal position
        partner.propagate_multicompany_account_position()
        self.assertEqual(
            partner_cp2.property_account_position_id, self.fiscal_position_a
        )
