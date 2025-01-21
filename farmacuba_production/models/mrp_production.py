from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.constrains('product_qty')
    def _check_minimum_production_qty(self):
        for record in self:
            if record.product_qty < 5:
                raise ValidationError(_("No se puede producir menos de 5 unidades de ningún producto."))

    @api.onchange('product_qty')
    def _onchange_check_material_availability(self):
        for line in self.move_raw_ids:
            if line.product_id.qty_available < line.product_uom_qty:
                raise ValidationError(
                    f"No hay suficiente cantidad del material {line.product_id.name} en el inventario."
                )
