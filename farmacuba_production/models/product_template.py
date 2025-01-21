from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(
        'Cost',
        compute='_compute_standard_price',
        inverse='_set_standard_price',
        search='_search_standard_price',
        store=True,  # Almacena el valor en la base de datos
        digits='Product Price',
        groups="base.group_user",
        help="""Value of the product (automatically computed in AVCO).
           Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
           Used to compute margins on sale orders."""
    )
