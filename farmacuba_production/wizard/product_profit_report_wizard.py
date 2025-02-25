from odoo import models, fields, api


class ProductProfitReportWizard(models.TransientModel):
    _name = 'product.profit.report.wizard'
    _description = 'Wizard for Reporting Profits by Product'

    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, 2100)],
        string="Año",
        required=True,
        default=lambda self: str(fields.Date.today().year)
    )

    def action_generate_report(self):
        # Redirigir a la vista de acción del reporte
        return {
            'type': 'ir.actions.act_window',
            'name': 'Earnings Report by Product',
            'view_mode': 'tree',
            'res_model': 'product.profit.report',
            'domain': [('year', '=', self.year)],
        }
