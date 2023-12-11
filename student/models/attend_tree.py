from odoo import models, fields, api


class StudentAttendanceRecord(models.Model):
    _name = 'student.attendance.record'
    _description = 'Student Attendance Record'

    student_id = fields.Many2one('student.registration', string='Student', required=True)
    checkin_time = fields.Datetime(string='Check-in Time')
    checkout_time = fields.Datetime(string='Check-out Time')
    work_hours = fields.Float(string='Work Hours', compute='_compute_work_hours', store=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)

    @api.depends('checkin_time', 'checkout_time')
    def _compute_work_hours(self):
        for record in self:
            if record.checkin_time and record.checkout_time:
                # Calculate work hours based on your business logic
                # Example: You can use the 'datetime' module to calculate the time difference
                work_hours = (record.checkout_time - record.checkin_time).total_seconds() / 3600.0
                record.work_hours=work_hours

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Check if the search is being performed from the tree view
            if self._context.get('search_default_today'):
                # Add a domain to filter records based on the current date
                  args.append(('date', '=', fields.Date.today()))
                  return super(StudentAttendanceRecord, self).search(args, offset=offset, limit=limit,
                                                                       order=order,count = count)