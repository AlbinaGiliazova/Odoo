from odoo import models, fields


class CancelReasonWizard(models.TransientModel):
    _name = 'packing.order.cancel.reason.wizard'
    _description = 'Причина отмены задания на упаковку'

    reason = fields.Text(string='Причина отмены', required=True)

    def action_confirm(self):
        """Подтвержение отмены. Передаём активный заказ в контексте"""
        order = self.env['packing.order'].browse(self.env.context.get('active_id'))
        order.write({
            'state': 'cancel',
            'cancellation_reason': self.reason
        })
        return {'type': 'ir.actions.act_window_close'}
