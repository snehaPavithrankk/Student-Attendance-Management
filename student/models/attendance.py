from odoo import models, fields, api, exceptions,_



class StudentAttendance(models.Model):
    _name = 'student.attendance'

    student_id = fields.Many2one('student.registration', string='Student')
    current_status = fields.Char(string='Current Status', compute='_compute_current_status', store=True)

    show_check_in_button = fields.Boolean(compute='_compute_show_buttons')
    show_check_out_button = fields.Boolean(compute='_compute_show_buttons')

    @api.model
    def action_view_attendance_records(self):
        # Open the attendance record tree view
        action = self.env.ref('your_module.action_view_attendance_records').read()[0]
        return action


    @api.depends('student_id.attendance_status')
    def _compute_show_buttons(self):
        for record in self:
            record.show_check_in_button = record.student_id.attendance_status == 'checked_out'
            record.show_check_out_button = record.student_id.attendance_status == 'checked_in'


    @api.depends('student_id.attendance_status', 'student_id.attendance_records')
    def _compute_current_status(self):
        for record in self:
            if record.student_id:
                status = record.student_id.attendance_status
                if status == 'checked_in':
                    record.current_status = f'{record.student_id.name}, Click to Checked Out'
                elif status == 'checked_out':
                    record.current_status = f'Welcome {record.student_id.name}, Click to Checked In'
                else:
                    record.current_status = ''
            else:
                record.current_status = ''



    def action_checkin(self):
        if not self.student_id:
            raise exceptions.UserError(_('Please select a student for check-in.'))

        student = self.student_id
        if student.attendance_status == 'checked_out':
            # Perform check-in action
            self.with_context(force_checkin=True).action_student_checkin(student.id)

            self.student_id = False

            # Create attendance record
            self.env['student.attendance.record'].create({
                'student_id': student.id,
                'checkin_time': fields.Datetime.now(),


            })

    def action_checkout(self):
        if not self.student_id:
            raise exceptions.UserError(_('Please select a student for check-out.'))

        student = self.student_id
        if student.attendance_status == 'checked_in':
            # Perform check-out action
            student.with_context(force_checkout=True).action_student_checkout()

            self.student_id = False

            # Update the corresponding attendance record with checkout time
            attendance_record = self.env['student.attendance.record'].search(
                [('student_id', '=', student.id), ('checkout_time', '=', False)],
                order='checkin_time desc',
                limit=1
            )
            if attendance_record:
                attendance_record.write({'checkout_time': fields.Datetime.now()})

    @api.model
    def action_student_checkin(self, student_id):
        student = self.env['student.registration'].browse(student_id)
        if student.attendance_status == 'checked_out':
            student.write({
                'checkin_time': fields.Datetime.now(),
                'attendance_status': 'checked_in'
            })












# from odoo import models, fields, api, exceptions, _
#
#
# class StudentAttendance(models.Model):
#     _name = 'student.attendance'
#
#     student_name = fields.Many2one('student.registration', string='Student Name',ondelete='cascade', index=True)
#     check_in_time = fields.Datetime(string='Check In Time')
#     check_out_time = fields.Datetime(string='Check Out Time')
#     worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
#
#     last_check_in_time = fields.Datetime(string='Last Check In Time', compute='_compute_last_check_in', store=True,
#                                          readonly=True)
#     last_check_out_time = fields.Datetime(string='Last Check Out Time', compute='_compute_last_check_out', store=True,
#                                           readonly=True)
#
#     def action_check_in_out(self):
#         """ Check In/Out action based on the current status """
#         if self.check_out_time:
#             self.action_check_in()
#         else:
#             self.action_check_out()
#
#     status = fields.Selection([('checked_in', 'Checked In'), ('checked_out', 'Checked Out')],
#                               string='Status', compute='_compute_status', store=True)
#
#     @api.depends('student_name', 'check_in_time')
#     def _compute_last_check_in(self):
#         for attendance in self:
#             last_check_in = self.env['student.attendance'].search([
#                 ('student_name', '=', attendance.student_name.id),
#                 ('check_in_time', '!=', False),
#                 ('id', '!=', attendance.id)], order='check_in_time desc', limit=1)
#             attendance.last_check_in_time = last_check_in.check_in_time if last_check_in else False
#
#     @api.depends('student_name', 'check_out_time')
#     def _compute_last_check_out(self):
#         for attendance in self:
#             last_check_out = self.env['student.attendance'].search([
#                 ('student_name', '=', attendance.student_name.id),
#                 ('check_out_time', '!=', False),
#                 ('id', '!=', attendance.id)], order='check_out_time desc', limit=1)
#             attendance.last_check_out_time = last_check_out.check_out_time if last_check_out else False
#
#     @api.depends('check_in_time', 'check_out_time')
#     def _compute_status(self):
#         """ Compute the status (checked in or checked out) """
#         for attendance in self:
#             if not attendance.check_in_time:
#                 attendance.status = 'checked_out'
#                 attendance.last_check_in_time = False
#             else:
#                 last_attendance = self.env['student.attendance'].search([
#                     ('student_name', '=', attendance.student_name.id),
#                 ], order='check_in_time desc', limit=1)
#
#                 if last_attendance:
#                     attendance.last_check_in_time = last_attendance.check_in_time
#                     attendance.status = 'checked_in'
#                 else:
#                     attendance.last_check_in_time = False
#                     attendance.status = 'checked_out'
#
#     def action_check_in(self):
#         # Set the check-in time for the selected student
#         self.check_in_time = fields.Datetime.now()
#
#     def action_check_out(self):
#         # Set the check-out time for the selected student
#         self.check_out_time = fields.Datetime.now()
#
#     @api.depends('check_in_time', 'check_out_time')
#     def _compute_worked_hours(self):
#         for attendance in self:
#             if attendance.check_out_time:
#                 delta = attendance.check_out_time - attendance.check_in_time
#                 attendance.worked_hours = delta.total_seconds() / 3600.0
#             else:
#                 attendance.worked_hours = False
#
#     @api.constrains('check_in_time', 'check_out_time', 'student_name')
#     def _check_validity(self):
#         """ Verifies the validity of the attendance record compared to the others for the same student.
#             For the same student, we must have:
#                 * maximum 1 "open" attendance record (without check_out)
#                 * no overlapping time slices with previous student records
#         """
#         for attendance in self:
#             # we take the latest attendance before our check_in time and check it doesn't overlap with ours
#             last_attendance_before_check_in = self.env['student.attendance'].search([
#                 ('student_name', '=', attendance.student_name.id),
#                 ('check_in_time', '<=', attendance.check_in_time),
#                 ('id', '!=', attendance.id),
#             ], order='check_in_time desc', limit=1)
#             if last_attendance_before_check_in and last_attendance_before_check_in.check_out_time and last_attendance_before_check_in.check_out_time > attendance.check_in_time:
#                 raise exceptions.ValidationError(
#                     _("Cannot create new attendance record for %(stud_name)s, the student was already checked in on %(datetime)s") % {
#                         'stud_name': attendance.student_name.name,
#                         'datetime': fields.Datetime.to_string(attendance.check_in_time),
#                     })
#
#             if not attendance.check_out_time:
#                 # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
#                 no_check_out_attendances = self.env['student.attendance'].search([
#                     ('student_name', '=', attendance.student_name.id),
#                     ('check_out_time', '=', False),
#                     ('id', '!=', attendance.id),
#                 ], order='check_in_time desc', limit=1)
#                 if no_check_out_attendances:
#                     raise exceptions.ValidationError(
#                         _("Cannot create new attendance record for %(stud_name)s, the student hasn't checked out since %(datetime)s") % {
#                             'stud_name': attendance.student_name.name,
#                             'datetime': fields.Datetime.to_string(no_check_out_attendances.check_in_time),
#                         })
#             else:
#                 # we verify that the latest attendance with check_in time before our check_out time
#                 # is the same as the one before our check_in time computed before, otherwise, it overlaps
#                 last_attendance_before_check_out = self.env['student.attendance'].search([
#                     ('student_name', '=', attendance.student_name.id),
#                     ('check_in_time', '<', attendance.check_out_time),
#                     ('id', '!=', attendance.id),
#                 ], order='check_in_time desc', limit=1)
#                 if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
#                     raise exceptions.ValidationError(
#                         _("Cannot create new attendance record for %(stud_name)s, the student was already checked in on %(datetime)s") % {
#                             'stud_name': attendance.student_name.name,
#                             'datetime': fields.Datetime.to_string(last_attendance_before_check_out.check_in_time),
#           })