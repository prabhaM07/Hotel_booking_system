from app.core.dependency import get_db
from app.crud.backup_restore import take_backup, take_backup_mongo
from app.models.Enum import BookingStatusEnum, RefundStatusEnum
from app.models.bookings import Bookings
from app.models.otps import OTPModel
from app.models.refund import Refunds
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

scheduler = AsyncIOScheduler()

async def update_status_job():

    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        now = datetime.now(timezone.utc)
        
        refund_rows = db.query(Refunds).filter(
            Refunds.status == RefundStatusEnum.APPROVED.value
        ).all()

        refund_updated = 0
        for row in refund_rows:

            created_at = row.created_at
            
            completed_date = (created_at + timedelta(days = 2)).date()
            if completed_date <= now.date():
                row.status = RefundStatusEnum.COMPLETED.value
                refund_updated += 1
        
        if refund_updated > 0:
            db.commit()
            print(f"Updated {refund_updated} refunds to COMPLETED")

        booked_rows = db.query(Bookings).filter(
            Bookings.booking_status == BookingStatusEnum.CONFIRMED.value
        ).all()
        
        booking_updated = 0
        for row in booked_rows:
            check_out = row.check_out
            
            if check_out <= now.date():
                row.booking_status = BookingStatusEnum.COMPLETED.value
                booking_updated += 1
        
        if booking_updated > 0:
            db.commit()
            print(f"Updated {booking_updated} bookings to COMPLETED")

        otp_rows = db.query(OTPModel).filter().all()
        
        otp_deleted = 0
        for row in otp_rows:
            expiry = row.expiry
            
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            
            if now > expiry:
                db.delete(row)
                otp_deleted += 1
        
        if otp_deleted > 0:
            db.commit()
            print(f"Deleted {otp_deleted} expired OTPs")
            
    except Exception as e:
        db.rollback()
        print(f"Error in update_status_job: {str(e)}")
    finally:
        db.close()
        try:
            next(db_gen)
        except StopIteration:
            pass



async def daily_backup_job():
    try:
        print("Starting daily backups...")

        pg_backup = take_backup()
        mongo_backup = take_backup_mongo()

        print(f"PostgreSQL backup created: {pg_backup}")
        print(f"MongoDB backup created: {mongo_backup}")

    except Exception as e:
        print(f"Daily backup failed: {str(e)}")



scheduler.add_job(update_status_job, 'interval', minutes=1)


scheduler.add_job(daily_backup_job, 'cron', hour=2, minute=0)