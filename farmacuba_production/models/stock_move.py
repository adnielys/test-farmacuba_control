from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    supplier_id = fields.Many2one(
        'res.partner',
        string="Proveedor",
        compute='_compute_supplier_id',
        store=True,
        help="Proveedor asociado al material en la lista de materiales.",
    )

    @api.depends('product_id', 'raw_material_production_id.bom_id')
    def _compute_supplier_id(self):
        for move in self:
            supplier = False
            if move.raw_material_production_id and move.product_id:
                bom_lines = move.raw_material_production_id.bom_id.bom_line_ids
                # Buscar la línea de la BOM correspondiente al producto del movimiento
                bom_line = bom_lines.filtered(lambda line: line.product_id == move.product_id)
                if bom_line:
                    supplier = bom_line.supplier_id
            move.supplier_id = supplier
