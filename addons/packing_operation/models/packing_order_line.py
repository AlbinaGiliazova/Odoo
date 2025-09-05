from odoo import models, fields, api


def _update_full_packing_date(self):
    for order in self:
        all_packed = all(
            line.packed_qty >= line.product_qty
            for line in order.packing_order_line_ids
        )
        if all_packed and not order.full_packing_date:
            order.full_packing_date = fields.Datetime.now()
        elif not all_packed:
            order.full_packing_date = False  # если хотя бы одна строка не упакована
        

class PackingOrderLine(models.Model):
    _name = "packing.order.line"
    _description = "Packing Order Line"

    order_id = fields.Many2one(
        "packing.order", string="Задание", ondelete="cascade"
    )
    product_id = fields.Many2one(
        "product.product", string="Деталь", required=True
    )
    product_id_int = fields.Integer(
        related='product_id.id', string="ID детали", store=False
    )
    product_qty = fields.Integer(string="Количество", required=True)
    packed_qty = fields.Integer(string="Упаковано", default=0)

    # Подтягиваем габариты из товара (readonly, не редактируются вручную)
    product_length = fields.Integer(
        string="Длина (мм)", related="product_id.length", store=False, readonly=True
    )
    product_width = fields.Integer(
        string="Ширина (мм)", related="product_id.width", store=False, readonly=True
    )
    product_height = fields.Integer(
        string="Высота (мм)", related="product_id.height", store=False, readonly=True
    )

    # Сводное поле для отображения габаритов
    dimensions = fields.Char(
        string="Габариты", compute="_compute_dimensions", store=False, readonly=True
    )

    packing_date = fields.Datetime(string="Дата упаковки", readonly=True)

    state = fields.Selection([
    ('waiting', 'Ожидает'),
    ('in_progress', 'В процессе'),
    ('done', 'Упаковано'),
    ('cancel', 'Отмена'),
    ], string="Статус", compute='_compute_state', store=True)

    @api.onchange('packed_qty')
    def _onchange_packed_qty(self):
        for line in self:
            if line.product_qty and line.packed_qty >= line.product_qty and not line.packing_date:
                line.packing_date = fields.Datetime.now()

    @api.depends("product_id.length", "product_id.width", "product_id.height")
    def _compute_dimensions(self):
        for line in self:
            if line.product_id:
                l = int(line.product_id.length or 0)
                w = int(line.product_id.width or 0)
                h = int(line.product_id.height or 0)
                line.dimensions = f"{l}×{w}×{h} мм"
            else:
                line.dimensions = "--"

    @api.model
    def write(self, vals):
        res = super().write(vals)
        if 'packed_qty' in vals:
            for line in self:
                if line.order_id:
                    line.order_id._update_full_packing_date()
        return res

    @api.depends('packed_qty', 'product_qty')
    def _compute_state(self):
        for line in self:
            if line.packed_qty >= line.product_qty:
                line.state = 'done'
            elif line.packed_qty > 0:
                line.state = 'in_progress'
            else:
                line.state = 'waiting'

    
    @api.model
    def increase_counter(self, value):
        product = self.env['product.product'].browse(int(value))
        if product:
            product.packed_count += 1  # замените на нужное поле
