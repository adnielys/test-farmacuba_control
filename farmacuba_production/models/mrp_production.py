from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.constrains('product_qty')
    def _check_minimum_production_qty(self):
        for record in self:
            if record.product_qty < 5:
                raise ValidationError(_("No less than 5 units of any product can be produced."))

    @api.onchange('product_qty')
    def _onchange_check_material_availability(self):
        for line in self.move_raw_ids:
            if line.product_id.qty_available < line.product_uom_qty:
                raise ValidationError(
                    f"There is not enough quantity of the material {line.product_id.name} in inventory."
                )
