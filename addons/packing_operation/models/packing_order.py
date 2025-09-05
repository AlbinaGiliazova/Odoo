from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PackingOrder(models.Model):
    """Модель задания на упаковку."""

    _name = "packing.order"
    _description = "Packing Order"

    name = fields.Char(string="Номер задания",
                       required=True,
                       copy=False,
                       default="New",
    )

    user_id = fields.Many2one("res.users", string="Оператор")
    cancellation_reason = fields.Text(string="Причина отмены")
    line_ids = fields.One2many("packing.order.line",
                               "order_id",
                               string="Строки заказа",
                               )
    full_packing_date = fields.Datetime(
        string="Дата полной упаковки", readonly=True
    )
    barcode_scanner = fields.Char(string="Сканер (ID продукта)")

    state = fields.Selection([
    ('waiting', 'Ожидает'),
    ('in_progress', 'В процессе'),
    ('done', 'Упаковано'),
    ('cancel', 'Отмена'),
    ], string="Статус", compute='_compute_state', store=True)

    @api.model
    def create(self, vals):
        """Создание заказа."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('packing.order') or _('New')
        return super().create(vals)

    def action_start_packing(self):
        """Запустить упаковку"""
        self.write({'state': 'in_progress'})

    def action_mark_done(self):
        """Завершить упаковку"""
        for order in self:
            # Проверяем, что по всем строкам packed_qty >= product_qty
            not_ready = order.line_ids.filtered(lambda l: l.packed_qty < l.product_qty)
            if not_ready:
                raise UserError(_("Не все количества упакованы. Проверьте строки заказа!"))
            order.write({
                'state': 'done',
                'full_packing_date': fields.Datetime.now()
            })

    def action_print_label_dummy(self):
        """Заглушка."""
        return True
    
    def action_cancel_order(self):
        """Отменить заказ и запросить причину"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'packing.order.cancel.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    def reset_packing(self):
        """Сбросить упаковку (обнулить packed_qty для всех строк)"""
        for order in self:
            order.line_ids.write({'packed_qty': 0})
        # Опционально возвращаем статус в начальный
        self.write({'state': 'waiting'})

    @api.onchange('barcode_scanner')
    def _onchange_barcode_scanner(self):
        """Обработка сканера."""
        if self.barcode_scanner:
            for line in self.line_ids:
                if str(line.product_id.id) == self.barcode_scanner:
                    if line.packed_qty < line.product_qty:
                        line.packed_qty += 1
                        # line.state вычисляется автоматом через compute, вручную ставить не нужно
                        self.barcode_scanner = ''
                    break

    @api.depends('line_ids.state')
    def _compute_state(self):
        """Вычисление статуса."""
        for order in self:
            line_states = order.line_ids.mapped('state')
            if not line_states:
                order.state = 'waiting'
            elif all(s == 'done' for s in line_states):
                order.state = 'done'
            elif any(s == 'in_progress' or s == 'done' for s in line_states):
                order.state = 'in_progress'
            else:
                order.state = 'waiting'

    def action_open_packing_process(self):
       """Начало процесса упаковки."""
       # self – конкретный заказ
       return {
           'type': 'ir.actions.act_window',
           'res_model': 'packing.order',
           'view_mode': 'form',
           'view_id': self.env.ref('packing_operation.view_packing_process_form').id,
           'target': 'current',
           'res_id': self.id,
           # можно добавить дополнительные параметры в context
       }
        
    def process_barcode_scan(self, product_id):
        """Увеличить счетчик packed_qty в строке заказа по product_id и записать последнего оператора"""
        self.ensure_one()
        line = self.line_ids.filtered(lambda l: l.product_id.id == product_id)
        if not line:
            raise UserError("В этом заказе нет строки с указанным продуктом (ID: %s)" % product_id)
        if line.packed_qty >= line.product_qty:
            raise UserError("Все детали этого типа уже упакованы!")
        line.packed_qty += 1
        line.packing_date = fields.Datetime.now()
        # Записываем пользователя, который упаковал деталь последним
        self.user_id = self.env.user.id
        return {'status': 'success', 'packed_qty': line.packed_qty}

    def _update_full_packing_date(self):
        """Обновляет дату полной упаковки при изменении packed_qty в строках заказа."""
        self.ensure_one()
        lines = self.line_ids.filtered(lambda l: l.packing_date)
        if lines:
            # Берём максимальную дату упаковки по всем строкам
            self.full_packing_date = max(lines.mapped('packing_date'))
        else:
            # Если ни одной строки не упаковано, очищаем поле
            self.full_packing_date = False

    def _compute_label_info(self):
        """Формирует текст этикетки."""
        for rec in self:
            rec.label_info = f"packing.order: {rec.name}\nID: {rec.id}" if rec.state == 'done' else ""