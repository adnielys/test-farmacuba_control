from odoo import models, fields, tools


class ProductProfitReport(models.Model):
    _name = 'product.profit.report'
    _description = 'Earnings Report by Product'
    _auto = False

    product_id = fields.Many2one('product.product', string="Product")
    year = fields.Char(string="Año")
    total_sales = fields.Float(string="Quantity Sold")
    total_revenue = fields.Float(string="Total Revenue")
    total_cost = fields.Float(string="Total Cost")
    profit_margin = fields.Float(string="Profit Margin (%)")

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = """
            CREATE OR REPLACE VIEW product_profit_report AS (
                SELECT
                    row_number() OVER () AS id,
                    sol.product_id AS product_id,
                    EXTRACT(YEAR FROM so.date_order)::TEXT AS year,
                    SUM(sol.product_uom_qty) AS total_sales,
                    SUM(sol.price_total) AS total_revenue,
                    SUM(sol.product_uom_qty * pt.standard_price) AS total_cost,
                    CASE 
                        WHEN SUM(sol.price_total) > 0 THEN 
                            ((SUM(sol.price_total) - SUM(sol.product_uom_qty * pt.standard_price)) / 
                            SUM(sol.price_total)) * 100
                        ELSE 0
                    END AS profit_margin
                FROM
                    sale_order_line sol
                JOIN
                    sale_order so ON sol.order_id = so.id
                JOIN
                    product_template pt ON sol.product_id = pt.id
               
                WHERE
                    so.state = 'sale'
                GROUP BY
                    sol.product_id, EXTRACT(YEAR FROM so.date_order)
            )
        """
        self._cr.execute(query)
