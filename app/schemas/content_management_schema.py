from pydantic import BaseModel, Field, HttpUrl, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime



class BookingPaymentPolicy(BaseModel):
    title: str = Field(default="Booking and Payment")
    points: List[str] = Field(
        default=[
            "All bookings are confirmed only after successful payment",
            "Full payment is required at the time of booking",
            "Bookings are subject to room availability",
            "You will receive a confirmation email after successful booking",
            "Check-out date must be after check-in date"
        ]
    )


class ReschedulingPolicy(BaseModel):
    title: str = Field(default="Rescheduling Policy")
    cutoff_days: int = Field(default=3, ge=1)
    max_reschedules: int = Field(default=1, ge=1)
    allowed_status: List[str] = Field(default=["confirmed"])
    points: List[str] = Field(
        default=[
            "Only confirmed bookings can be rescheduled",
            "Rescheduling must be requested at least 3 days before check-in date",
            "Each booking can be rescheduled only once",
            "New dates are subject to room availability",
            "Rescheduling requests within 3 days of check-in will be rejected"
        ]
    )


class CancellationPolicy(BaseModel):
    title: str = Field(default="Cancellation Policy")
    full_refund_days: int = Field(default=7, ge=1)
    partial_refund_days: int = Field(default=3, ge=1)
    partial_refund_percentage: int = Field(default=50, ge=0, le=100)
    points: List[str] = Field(
        default=[
            "Only confirmed bookings can be cancelled",
            "7+ days before check-in: 100% refund",
            "3-6 days before check-in: 50% refund",
            "Less than 3 days before check-in: No refund",
            "All cancellations are final and cannot be reversed"
        ]
    )


class RefundPolicy(BaseModel):
    title: str = Field(default="Refund Policy")
    processing_days: int = Field(default=2, ge=1)
    bank_processing_days: str = Field(default="5-10 additional business days")
    points: List[str] = Field(
        default=[
            "Approved refunds are processed within 2 business days",
            "Refunds are credited to your original payment method",
            "Bank processing may take 5-10 additional business days",
            "Refund status can be tracked in your booking history"
        ]
    )


class GeneralTerms(BaseModel):
    title: str = Field(default="General Terms")
    support_email: EmailStr = Field(default="support@yourhotel.com")
    points: List[str] = Field(
        default=[
            "You must provide accurate information during booking",
            "We reserve the right to modify these terms at any time",
            "Continued use of our services means you accept any changes",
            "For support, contact us at: support@yourhotel.com"
        ]
    )


class TermsAndConditions(BaseModel):
    version: str = Field(default="1.0", max_length=10)
    effective_date: datetime
    last_updated: datetime
    is_active: bool = Field(default=True)
    
    introduction: str = Field(
        default="By using our hotel booking system, you agree to these Terms and Conditions. Please read them carefully before making a booking."
    )
    
    booking_payment_policy: BookingPaymentPolicy = Field(default_factory=BookingPaymentPolicy)
    rescheduling_policy: ReschedulingPolicy = Field(default_factory=ReschedulingPolicy)
    cancellation_policy: CancellationPolicy = Field(default_factory=CancellationPolicy)
    refund_policy: RefundPolicy = Field(default_factory=RefundPolicy)
    general_terms: GeneralTerms = Field(default_factory=GeneralTerms)
    
    footer_text: str = Field(
        default="By proceeding with a booking, you agree to these Terms and Conditions."
    )

    class Config:
        json_schema_extra = {
          "example": {
              "version": "1.0",
              "effective_date": "2024-11-09T00:00:00",
              "last_updated": "2024-11-09T00:00:00",
              "is_active": 'true',
              "introduction": "By using our hotel booking system, you agree to these Terms and Conditions. Please read them carefully before making a booking.",

              "booking_payment_policy": {
                "title": "Booking and Payment",
                "points": [
                  "All bookings are confirmed only after successful payment",
                  "Full payment is required at the time of booking",
                  "Bookings are subject to room availability",
                  "You will receive a confirmation email after successful booking",
                  "Check-out date must be after check-in date"
                ]
              },

              "rescheduling_policy": {
                "title": "Rescheduling Policy",
                "cutoff_days": 3,
                "max_reschedules": 1,
                "allowed_status": ["confirmed"],
                "points": [
                  "Only confirmed bookings can be rescheduled",
                  "Rescheduling must be requested at least 3 days before check-in date",
                  "Each booking can be rescheduled only once",
                  "New dates are subject to room availability",
                  "Rescheduling requests within 3 days of check-in will be rejected"
                ]
              },

              "cancellation_policy": {
                "title": "Cancellation Policy",
                "full_refund_days": 7,
                "partial_refund_days": 3,
                "partial_refund_percentage": 50,
                "points": [
                  "Only confirmed bookings can be cancelled",
                  "7+ days before check-in: 100% refund",
                  "3-6 days before check-in: 50% refund",
                  "Less than 3 days before check-in: No refund",
                  "All cancellations are final and cannot be reversed"
                ]
              },

              "refund_policy": {
                "title": "Refund Policy",
                "processing_days": 2,
                "bank_processing_days": "5-10 additional business days",
                "points": [
                  "Approved refunds are processed within 2 business days",
                  "Refunds are credited to your original payment method",
                  "Bank processing may take 5-10 additional business days",
                  "Refund status can be tracked in your booking history"
                ]
              },

              "general_terms": {
                "title": "General Terms",
                "support_email": "support@yourhotel.com",
                "points": [
                  "You must provide accurate information during booking",
                  "We reserve the right to modify these terms at any time",
                  "Continued use of our services means you accept any changes",
                  "For support, contact us at: support@yourhotel.com"
                ]
              },

              "footer_text": "By proceeding with a booking, you agree to these Terms and Conditions."
              }

        }
