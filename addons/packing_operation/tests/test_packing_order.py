from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestPackingOrder(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PackingOrder = self.env['packing.order']
        self.PackingOrderLine = self.env['packing.order.line']

    def test_create_order(self):
        """Проверяем создание заказа, автогенерацию имени"""
        order = self.PackingOrder.create({})
        self.assertTrue(order.name.startswith("PO") or order.name != 'New')

    def test_barcode_onchange_scans_line(self):
        """Проверяем сканирование: packed_qty увеличивается по штрихкоду"""
        product = self.env['product.product'].create({'name': 'Тестовый продукт'})
        order = self.PackingOrder.create({
            'line_ids': [(0, 0, {'product_id': product.id, 'product_qty': 2, 'packed_qty': 0})]
        })
        order.barcode_scanner = str(product.id)
        order._onchange_barcode_scanner()
        self.assertEqual(order.line_ids[0].packed_qty, 1)

    def test_action_mark_done_success(self):
        """Можно завершить заказ, если всё упаковано"""
        product = self.env['product.product'].create({'name': 'Товар'})
        order = self.PackingOrder.create({
            'line_ids': [(0, 0, {'product_id': product.id, 'product_qty': 2, 'packed_qty': 2})]
        })
        order.action_mark_done()
        self.assertEqual(order.state, 'done')

    def test_action_mark_done_fail(self):
        """Ошибка при попытке завершить, если что-то не упаковано"""
        product = self.env['product.product'].create({'name': 'Товар2'})
        order = self.PackingOrder.create({
            'line_ids': [(0, 0, {'product_id': product.id, 'product_qty': 2, 'packed_qty': 1})]
        })
        with self.assertRaises(UserError):
            order.action_mark_done()

    def test_action_cancel_order(self):
        """Проверяем действие для отмены заказа (wizard открывается)"""
        order = self.PackingOrder.create({})
        res = order.action_cancel_order()
        self.assertEqual(res['res_model'], 'packing.order.cancel.reason.wizard')
        self.assertEqual(res['type'], 'ir.actions.act_window')
        self.assertEqual(res['target'], 'new')
