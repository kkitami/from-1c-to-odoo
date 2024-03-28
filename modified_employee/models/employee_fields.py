from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    passport_data = fields.Char(string='Passport details')
    snils = fields.Char(string='SNILS')
    inn = fields.Char(string='INN')
    citizenship = fields.Char(string='Citizenship')
    def import_data(self):
        return {
            'name': 'HR Import Button',
            'type': 'ir.actions.act_window',
            'res_model': 'import.button',
            'view_mode': 'form',
            'target': 'new',
            'context': {},
        }
