from odoo import models, fields
import base64, csv
from io import StringIO


class ImportPackingCsvWizard(models.TransientModel):
    _name = 'import.packing.csv.wizard'
    _description = 'Wizard: Импорт CSV для заказов на упаковку'

    csv_file = fields.Binary(string='CSV-файл', required=True)
    filename = fields.Char()

    def action_import_csv(self):
        if not self.csv_file:
            return
        csv_data = base64.b64decode(self.csv_file)
        data_file = StringIO(csv_data.decode('utf-8'))
        reader = csv.DictReader(data_file, delimiter=',')

        orders_dict = {}
        for row in reader:
            order_name = row.get('Order Name')
            # Соберите нужные поля по вашему формату CSV!
            if order_name not in orders_dict:
                orders_dict[order_name] = {
                    'name': order_name,
                    'full_packing_date': row.get('Order Date'),
                    'line_ids': []
                }
            orders_dict[order_name]['line_ids'].append((0, 0, {
                'product_id': int(row.get('Product ID')),
                'product_qty': float(row.get('Product Qty')),
                'packed_qty': float(row.get('Packed Qty')),
                'dimensions': row.get('Dimensions'),
                'packing_date': row.get('Order Date'),
            }))

        # Создаём заказы и линии упакоки
        for order in orders_dict.values():
            self.env['packing.order'].create(order)
