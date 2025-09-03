from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    length = fields.Integer(string="Длина (мм)")
    width = fields.Integer(string="Ширина (мм)")
    height = fields.Integer(string="Высота (мм)")
