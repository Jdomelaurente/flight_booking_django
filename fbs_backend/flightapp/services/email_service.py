# flightapp/services/email_service.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import logging
from email.mime.application import MIMEApplication
from io import BytesIO

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending booking confirmation emails with itinerary PDF attachment
    """
    
    @staticmethod
    def send_booking_confirmation(booking, payment=None, attach_pdf=True):
        """
        Send booking confirmation email with PDF attachment
        
        Args:
            booking: Booking model instance
            payment: Payment model instance (optional)
            attach_pdf: Boolean to attach itinerary PDF
        """
        try:
            # Get contact email from booking
            contact = booking.contact
            if not contact or not contact.email:
                logger.error(f"No contact email found for booking {booking.id}")
                return False
            
            recipient_email = contact.email
            booking_reference = booking.pnr or f"BK{booking.id:08d}"
            
            logger.info(f"? Preparing email for {recipient_email}, booking {booking_reference}")
            
            # Prepare email context
            context = EmailService._prepare_email_context(booking, payment, booking_reference)
            
            # Render email templates
            subject = f"?? Your Booking Confirmation - {booking_reference}"
            text_content = render_to_string('emails/booking_confirmation.txt', context)
            html_content = render_to_string('emails/booking_confirmation.html', context)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
                reply_to=[settings.SUPPORT_EMAIL] if hasattr(settings, 'SUPPORT_EMAIL') else None
            )
            email.attach_alternative(html_content, "text/html")
            
            # Attach itinerary PDF
            if attach_pdf:
                try:
                    # Import here to avoid circular imports
                    from .pdf_service import BoardingPassPDFService
                    
                    logger.info(f"? Generating itinerary PDF for booking {booking.id}...")
                    
                    # Generate PDF
                    pdf_buffer = BoardingPassPDFService.generate_itinerary_pdf(booking)
                    
                    # Create MIME attachment
                    pdf_attachment = MIMEApplication(
                        pdf_buffer.getvalue(),
                        _subtype="pdf"
                    )
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=f"itinerary_{booking_reference}.pdf"
                    )
                    
                    # Attach to email
                    email.attach(pdf_attachment)
                    
                    logger.info(f"? PDF attached successfully: itinerary_{booking_reference}.pdf")
                    
                    # Also attach individual boarding passes for each flight
                    details = booking.details.select_related('passenger', 'schedule__flight').all()
                    for detail in details:
                        if detail.schedule:
                            try:
                                bp_buffer = BoardingPassPDFService.generate_boarding_pass(detail)
                                bp_attachment = MIMEApplication(
                                    bp_buffer.getvalue(),
                                    _subtype="pdf"
                                )
                                passenger_name = detail.passenger.last_name if detail.passenger else "Passenger"
                                flight_num = detail.schedule.flight.flight_number if detail.schedule.flight else "FL"
                                bp_attachment.add_header(
                                    'Content-Disposition',
                                    'attachment',
                                    filename=f"boarding_pass_{passenger_name}_{flight_num}.pdf"
                                )
                                email.attach(bp_attachment)
                                logger.info(f"? Boarding pass attached for {passenger_name}")
                            except Exception as bp_error:
                                logger.warning(f"?? Could not attach boarding pass for detail {detail.id}: {bp_error}")
                    
                except Exception as e:
                    logger.error(f"? Failed to generate/attach PDF: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue sending email even if PDF attachment fails
            
            # Send email
            logger.info(f"? Sending email to {recipient_email}...")
            email.send(fail_silently=False)
            
            logger.info(f"? Booking confirmation email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"? Failed to send booking confirmation email: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _prepare_email_context(booking, payment, booking_reference):
        """
        Prepare context data for email templates
        """
        # Import models here to avoid circular imports
        from app.models import BookingDetail
        
        # Get booking details with related data
        details = booking.details.select_related(
            'passenger', 
            'schedule__flight__airline',
            'schedule__flight__route__origin_airport',
            'schedule__flight__route__destination_airport',
            'seat'
        ).all()
        
        # Separate outbound and return flights
        outbound_details = []
        return_details = []
        
        seen_flights = set()
        for detail in details:
            if detail.schedule:
                flight_id = detail.schedule.flight.id
                if flight_id not in seen_flights:
                    seen_flights.add(flight_id)
                    outbound_details.append(detail)
                else:
                    return_details.append(detail)
        
        # If no clear separation, put all in outbound
        if not return_details and outbound_details:
            return_details = []
        
        # Calculate totals
        total_passengers = len(set([d.passenger.id for d in details if d.passenger]))
        
        # Get add-ons summary
        addons_summary = []
        for detail in details:
            for addon in detail.addons.all():
                addons_summary.append({
                    'passenger': detail.passenger.get_full_name() if detail.passenger else "Unknown",
                    'item': addon.name,
                    'price': float(addon.price) if addon.price else 0
                })
        
        # Get contact info
        contact = booking.contact
        contact_name = f"{contact.first_name} {contact.last_name}" if contact else "N/A"
        contact_email = contact.email if contact else "N/A"
        contact_phone = contact.phone if contact else "N/A"
        
        # Get airline info from first flight
        first_detail = details[0] if details else None
        airline_name = "Philippine Airlines"
        if first_detail and first_detail.schedule and first_detail.schedule.flight.airline:
            airline_name = first_detail.schedule.flight.airline.name
        
        return {
            'booking_reference': booking_reference,
            'booking_id': booking.id,
            'booking_date': booking.created_at,
            'trip_type': booking.get_trip_type_display() if hasattr(booking, 'get_trip_type_display') else booking.trip_type,
            'status': booking.status,
            
            # Contact info
            'contact_name': contact_name,
            'contact_email': contact_email,
            'contact_phone': contact_phone,
            
            # Flight details
            'outbound_details': outbound_details,
            'return_details': return_details,
            'is_round_trip': booking.trip_type == 'round_trip',
            
            # Financial summary
            'base_fare': float(booking.base_fare_total) if booking.base_fare_total else 0,
            'tax_total': float(booking.tax_total) if booking.tax_total else 0,
            'insurance_total': float(booking.insurance_total) if booking.insurance_total else 0,
            'total_amount': float(booking.total_amount) if booking.total_amount else 0,
            'amount_paid': float(payment.amount) if payment else float(booking.total_amount) if booking.total_amount else 0,
            'payment_method': payment.method if payment else 'Online Payment',
            'payment_date': payment.payment_date if payment else timezone.now(),
            'transaction_id': payment.transaction_id if payment else 'N/A',
            
            # Passengers and add-ons
            'total_passengers': total_passengers,
            'passengers': [detail.passenger for detail in details if detail.passenger],
            'addons_summary': addons_summary,
            
            # Airline info
            'airline_name': airline_name,
            
            # Support info
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@philippineairlines.com'),
            'support_phone': getattr(settings, 'SUPPORT_PHONE', '(02) 8855-8888'),
            'website_url': getattr(settings, 'WEBSITE_URL', 'http://localhost:5173/'),
            'api_url': getattr(settings, 'API_URL', 'http://localhost:8000/flightapp'),
        }