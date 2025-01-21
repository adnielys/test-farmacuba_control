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
                        "The quantity requested for product '%s' exceeds the available stock considering reservations in manufacturing (%s units available). "
                        "Please adjust the quantity or check reservations."
                        % (product.name, line.free_qty_today)
                    ))