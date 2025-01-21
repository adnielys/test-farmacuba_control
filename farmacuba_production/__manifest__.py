# -*- coding: utf-8 -*-

{
    'name': 'Farmacuba Production Control',
    'version': '1.0',
    'sequence': 10,
    "author": "Adnielys Abday",
    'contributors': [
        'Adnielys Abday Rojas Tadeo <adnielys.rojas89@gmail.com>',
    ],
    'description': """
     
    """,
    'depends': ['mrp', 'stock', 'sale_management', 'account', 'purchase'],
    "data": [
        'security/ir.model.access.csv',
        'views/mrp_bom_inherit_views.xml',
        'views/stock_move_form_with_supplier_view.xml',
        'wizard/product_profit_report_wizard_view.xml',
        'wizard/top_sales_excel_wizard_view.xml',
        'report/product_profit_report_view.xml',
    ],

    'assets': {
        'web.assets_backend': [


        ]
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
