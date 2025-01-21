import base64

from odoo import models, fields, api
import io
import xlsxwriter
from datetime import datetime


class TopSalesExcelWizard(models.TransientModel):
    _name = 'top.sales.excel.wizard'
    _description = 'Top 5 Best Sellers Wizard'

    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, 2100)],
        string="Año",
        required=True,
        default=lambda self: str(fields.Date.today().year)
    )

    def export_top_sales(self):
        # Lógica para generar el Excel
        sales_data = self._get_top_sales()
        return self._generate_excel_file(sales_data)

    def _get_top_sales(self):
        # Obtener las 5 mejores ventas del año seleccionado
        query = """
            SELECT so.id AS order_id, so.name AS order_name, 
                   so.date_order, rp.name AS customer_name,
                   SUM(sol.price_total) AS total_sales
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            JOIN res_partner rp ON so.partner_id = rp.id
            WHERE EXTRACT(YEAR FROM so.date_order) = %s
              AND so.state = 'sale'
            GROUP BY so.id, so.name, so.date_order, rp.name
            ORDER BY total_sales DESC
            LIMIT 5
        """
        self.env.cr.execute(query, (int(self.year),))
        return self.env.cr.dictfetchall()

    def _generate_excel_file(self, sales_data):
        # Crear el archivo Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Top 5 Ventas")

        # Configurar estilos
        bold = workbook.add_format(
            {'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#F2F2F2', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
        currency = workbook.add_format({'num_format': '$#,##0.00'})

        # Agregar el encabezado del reporte
        report_title = f"Top 5 Sales Report - {self.year}"
        worksheet.merge_range('A1:D1', report_title, header_format)

        # Ajustar ancho de columnas
        worksheet.set_column('A:A', 15)  # Orden
        worksheet.set_column('B:B', 30)  # Cliente
        worksheet.set_column('C:C', 15)  # Fecha
        worksheet.set_column('D:D', 20)  # Total de Venta

        # Escribir encabezados de columnas
        headers = ["Order", "Customer", "Date", "Total Sales"]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, bold)  # Escribir en la fila 3 (índice 2)

        # Escribir datos
        for row, sale in enumerate(sales_data, start=3):  # Comenzar en la fila 4
            worksheet.write(row, 0, sale['order_name'])
            worksheet.write(row, 1, sale['customer_name'])
            worksheet.write(row, 2, sale['date_order'].strftime('%Y-%m-%d'))
            worksheet.write(row, 3, sale['total_sales'], currency)

        # Cerrar el workbook
        workbook.close()
        output.seek(0)

        # Devolver el archivo como attachment
        file_name = f"Top_5_Sales_{self.year}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'top.sales.excel.wizard',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        output.close()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
