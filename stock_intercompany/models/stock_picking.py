from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"


    #override of method from stock module
    def button_validate(self):

        companies = self.env['res.company'].sudo().search([])
        partners = {cp.partner_id: cp for cp in companies}

        for picking in self:
            if picking.partner_id in partners.keys():
                company = partners[picking.partner_id]
                warehouse = self.env["stock.warehouse"].search([('company_id','=',company.id)], limit=1)
                vals = {
                    'company_id': company.id,
                    'picking_type_id': company.intercompany_in_type_id or warehouse.in_type_id.id,
                    'state':'draft',
                    'location_id': False, # readonly
                    'location_dest_id': False, #readonly
                }

                new_move_vals = picking.copy_data(default=vals)
                for move in picking.move_ids_without_package:
                    self.env['stock.move'].create(
                        {
                        'name': move.product_id.name,
                        'product_id': move.product_id.id,
                        'product_uom_qty': move.product_uom_qty,
                        'product_uom': move.product_id.uom_id.id,
                        }
                    )

                    