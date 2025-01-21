from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def create(self, vals):
        bom = super(MrpBom, self).create(vals)
        for line in bom.bom_line_ids:
            if not line.supplier_id:
                raise exceptions.ValidationError(
                    f"La línea del producto {line.product_id.display_name} no tiene un proveedor asignado."
                )
        return bom

    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        for bom in self:
            for line in bom.bom_line_ids:
                if not line.supplier_id:
                    raise exceptions.ValidationError(
                        f"La línea del producto {line.product_id.display_name} no tiene un proveedor asignado."
                    )
        return res


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    supplier_id = fields.Many2one(
        'res.partner',
        string="Proveedor",
        default=lambda self: self._default_supplier_id(),
        domain="[('id', 'in', product_supplier_ids)]",
        help="Proveedor predeterminado asociado al producto de esta línea de materiales.",
    )

    product_supplier_ids = fields.Many2many(
        'res.partner',
        compute="_compute_product_supplier_ids",
        string="Proveedores del Producto",
        help="Lista de proveedores asociados al producto.",
    )

    @api.constrains('product_id')
    def _check_supplier_defined(self):
        for line in self:
            if not line.product_id.seller_ids:
                raise UserError(f"The product {line.product_id.name} has no suppliers defined.")

    @api.depends('product_id')
    def _compute_product_supplier_ids(self):
        for line in self:
            if line.product_id:
                line.product_supplier_ids = line.product_id.seller_ids.mapped('partner_id')
            else:
                line.product_supplier_ids = self.env['res.partner']

    @api.model
    def _default_supplier_id(self):
        product_id = self.env.context.get('default_product_id')
        if product_id:
            product = self.env['product.product'].browse(product_id)
            suppliers = product.seller_ids.sorted(key=lambda s: (s.sequence, s.price))
            return suppliers[:1].partner_id.id if suppliers else None
        return None
