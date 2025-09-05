{
    "name": "Packing Operation",
    "version": "1.0",
    "summary": "Управление заданиями на упаковку",
    "description": """
        Модуль для сканирования и упаковки деталей
    """,
    "category": "Inventory",
    "author": "Альбина Гилязова",
    "depends": ["stock", "product"],
    'assets': {
    'web.assets_backend': [
        'static/src/js/barcode_scanner.js',
        'static/src/js/packing_label.js',
    ],},
    "data": [
        "security/packing_security.xml",
        "security/ir.model.access.csv",
        "security/packing_record_rules.xml",
        "data/packing_order_sequence.xml",
        "views/import_packing_csv_wizard_view.xml",
        "views/packing_order_views.xml",
        "views/cancel_reason_wizard_view.xml",
        "views/cancel_reason_wizard_action.xml",
        "views/actions.xml", 
        "views/packing_order_canceled.xml",  
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}