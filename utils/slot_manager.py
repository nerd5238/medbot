# utils/slot_manager.py

from datetime import datetime, timedelta, time as dtime
from models import Appointment, db


class SlotManager:
    """
    Timeline-based scheduler:
    - doctor work: 09:00–13:00 and 14:00–18:00
    - lunch break: 13:00–14:00
    - base step: 15 minutes
    - avoids overlaps using Appointment table
    """

    def __init__(self,
                 start_time="09:00",
                 lunch_start="13:00",
                 lunch_end="14:00",
                 end_time="18:00",
                 step_minutes=15):
        self.start_time_str = start_time
        self.lunch_start_str = lunch_start
        self.lunch_end_str = lunch_end
        self.end_time_str = end_time
        self.step_minutes = step_minutes

    # -----------------------------
    # Internal helpers
    # -----------------------------
    def _to_dt(self, date_str, time_str):
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

    def _parse_time(self, time_str):
        return datetime.strptime(time_str, "%H:%M").time()

    # -----------------------------
    # Main: find available starts
    # -----------------------------
    def get_available_start_times(self, date_str, duration_minutes):
        """
        Returns list of start times (HH:MM) on a given date where a block of
        `duration_minutes` can fit:
        - inside working hours
        - not crossing lunch
        - not overlapping existing appointments (pending/approved)
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        day_start_dt = self._to_dt(date_str, self.start_time_str)
        day_end_dt = self._to_dt(date_str, self.end_time_str)

        lunch_start_dt = self._to_dt(date_str, self.lunch_start_str)
        lunch_end_dt = self._to_dt(date_str, self.lunch_end_str)

        # Load existing appointments for that date
        existing = Appointment.query.filter_by(appointment_date=date_obj).filter(
            Appointment.status.in_(["pending", "approved"])
        ).all()

        existing_blocks = []
        for appt in existing:
            start_dt = datetime.combine(date_obj, appt.appointment_time)
            end_dt = start_dt + timedelta(minutes=appt.duration_minutes or 30)
            existing_blocks.append((start_dt, end_dt))

        available_starts = []
        step = timedelta(minutes=self.step_minutes)

        current = day_start_dt
        while True:
            end_candidate = current + timedelta(minutes=duration_minutes)

            # Stop if beyond day end
            if end_candidate > day_end_dt:
                break

            # Skip if inside or crossing lunch
            if current < lunch_end_dt and end_candidate > lunch_start_dt:
                current = lunch_end_dt
                continue

            # Check overlap with existing appointments
            conflict = False
            for (s, e) in existing_blocks:
                # overlap if NOT (end <= s or current >= e)
                if not (end_candidate <= s or current >= e):
                    conflict = True
                    break

            if not conflict:
                # valid starting time
                available_starts.append(current.strftime("%H:%M"))

            current += step

        return available_starts
