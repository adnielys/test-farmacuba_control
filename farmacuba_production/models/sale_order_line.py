from odoo import models, fields, api, exceptions, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains('product_id', 'product_uom_qty')
    def _check_stock_availability_with_manufacturing(self):
        for line in self:
            product = line.product_id

            if product.type == 'product':  # Aplica solo a productos almacenables
                if line.product_uom_qty > line.free_qty_today:
                    raise exceptions.ValidationError(_(
                        "La cantidad solicitada para el producto '%s' excede el stock disponible considerando reservas en fabricación (%s unidades disponibles). "
                        "Por favor, ajuste la cantidad o verifique las reservas."
                        % (product.name, line.free_qty_today)
                    ))