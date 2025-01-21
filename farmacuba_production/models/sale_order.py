import xlsxwriter
import base64
from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _check_all_lines_inventory(self):
        for order in self:
            for line in order.order_line:
                if line.product_id.type == 'product':  # Solo aplica para productos almacenables
                    available_qty = line.product_id.qty_available
                    if line.product_uom_qty > available_qty:
                        raise ValidationError(
                            f"No se puede confirmar el pedido porque el producto {line.product_id.name} "
                            f"no tiene suficiente stock. Disponible: {available_qty}, Solicitado: {line.product_uom_qty}."
                        )

    def export_top_sales_to_excel(self):
        # Obtener las 5 mejores ventas del año
        top_sales = self.env['sale.order.line'].read_group(
            [('order_id.state', '=', 'sale'),
             ('order_id.date_order', '>=', fields.Date.today().replace(month=1, day=1)),
             ('order_id.date_order', '<=', fields.Date.today())],
            ['order_id', 'product_id', 'price_subtotal:sum'],
            ['product_id'],
            limit=5,
            orderby='price_subtotal desc'
        )

        # Crear archivo Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet('Top Sales')

        # Encabezados
        headers = ['Producto', 'Cantidad Vendida', 'Total Venta']
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        # Datos
        for row, sale in enumerate(top_sales, start=1):
            product = self.env['product.product'].browse(sale['product_id'][0])
            sheet.write(row, 0, product.name)
            sheet.write(row, 1, sale['__count'])  # Cantidad vendida
            sheet.write(row, 2, sale['price_subtotal'])  # Total venta

        workbook.close()
        output.seek(0)

        # Guardar como adjunto
        attachment = self.env['ir.attachment'].create({
            'name': 'Top_Sales.xlsx',
            'datas': base64.b64encode(output.read()),
            'type': 'binary',
            'res_model': 'sale.order',
        })
        output.close()

        return attachment
