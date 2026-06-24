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
            contact = getattr(booking, 'contact', None)
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
                    
                    logger.info(f"✅ PDF attached successfully: itinerary_{booking_reference}.pdf")
                    
                    # NOTE: Boarding passes are NOT attached at this stage.
                    # In the real-world workflow, boarding passes are only issued
                    # AFTER the passenger completes check-in at the airport counter.
                    # Students must go through the DCS Check-in Simulator to receive their boarding pass.
                    
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
            logger.error(f"❌ Failed to send booking confirmation email: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def send_checkin_confirmation(booking_detail, attach_pdf=True):
        """
        Send check-in confirmation email with boarding pass PDF attachment
        """
        try:
            # Get passenger and their contact email
            passenger = booking_detail.passenger
            booking = booking_detail.booking
            
            # Use passenger email if available, else fallback to booking contact email
            recipient_email = getattr(passenger, 'email', None)
            if not recipient_email:
                contact = getattr(booking, 'contact', None)
                recipient_email = contact.email if contact else None
                
            if not recipient_email:
                logger.error(f"No recipient email found for checkin {booking_detail.id}")
                return False
            
            p_name = passenger.get_full_name() if passenger else "Passenger"
            pnr = booking.pnr or f"BK{booking.id:08d}"
            flight_num = booking_detail.schedule.flight.flight_number if booking_detail.schedule else "N/A"
            
            logger.info(f"📧 Preparing check-in email for {recipient_email}, {p_name}")
            
            # Prepare context
            context = {
                'passenger_name': p_name,
                'booking_reference': pnr,
                'flight_number': flight_num,
                'seat_number': booking_detail.seat.seat_number if booking_detail.seat else "TBA",
                'origin': booking_detail.schedule.flight.route.origin_airport.code,
                'destination': booking_detail.schedule.flight.route.destination_airport.code,
                'airline_name': booking_detail.schedule.flight.airline.name if booking_detail.schedule.flight.airline else "Philippine Airlines",
            }
            
            # Render templates
            subject = f"✈️ Your Boarding Pass is Ready - {flight_num} / {pnr}"
            text_content = render_to_string('emails/checkin_confirmation.txt', context)
            html_content = render_to_string('emails/checkin_confirmation.html', context)
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            
            # Attach Boarding Pass PDF
            if attach_pdf:
                try:
                    from .pdf_service import BoardingPassPDFService
                    pdf_buffer = BoardingPassPDFService.generate_boarding_pass(booking_detail)
                    
                    pdf_attachment = MIMEApplication(pdf_buffer.getvalue(), _subtype="pdf")
                    filename = f"boarding_pass_{pnr}_{p_name.replace(' ', '_')}.pdf"
                    pdf_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                    email.attach(pdf_attachment)
                    
                    logger.info(f"✅ Boarding pass attached: {filename}")
                except Exception as e:
                    logger.error(f"⚠️ Failed to attach boarding pass: {e}")
            
            # Send
            email.send(fail_silently=False)
            logger.info(f"🚀 Check-in confirmation sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send checkin email: {str(e)}")
            return False

    @staticmethod
    def send_group_checkin_confirmation(booking_details, attach_pdfs=True):
        """
        Send a single check-in confirmation email for a group of passengers
        """
        if not booking_details:
            return False
            
        try:
            # Use the first booking detail to get common info
            first_detail = booking_details[0]
            booking = first_detail.booking
            contact = getattr(booking, 'contact', None)
            
            if not contact or not contact.email:
                logger.error(f"No contact email for group checkin {booking.id}")
                return False
                
            recipient_email = contact.email
            pnr = booking.pnr or f"BK{booking.id:08d}"
            flight_num = first_detail.schedule.flight.flight_number if first_detail.schedule else "N/A"
            airline_name = first_detail.schedule.flight.airline.name if first_detail.schedule and first_detail.schedule.flight.airline else "Philippine Airlines"
            
            logger.info(f"📧 Preparing BUNDLED check-in email for {recipient_email}, {len(booking_details)} passengers")
            
            # Prepare context
            passengers_list = []
            for det in booking_details:
                passengers_list.append({
                    'name': det.passenger.get_full_name() if det.passenger else "Passenger",
                    'seat': det.seat.seat_number if det.seat else "TBA",
                    'type': det.passenger_type or (det.passenger.passenger_type if det.passenger else "Adult")
                })
            
            context = {
                'is_group': True,
                'passengers': passengers_list,
                'booking_reference': pnr,
                'flight_number': flight_num,
                'origin': first_detail.schedule.flight.route.origin_airport.code if first_detail.schedule else "N/A",
                'destination': first_detail.schedule.flight.route.destination_airport.code if first_detail.schedule else "N/A",
                'airline_name': airline_name,
            }
            
            # Use a slightly different subject for groups
            subject = f"✈️ Group Boarding Passes Ready ({len(booking_details)} passengers) - {flight_num} / {pnr}"
            
            # Render templates
            text_content = render_to_string('emails/checkin_confirmation.txt', context)
            html_content = render_to_string('emails/checkin_confirmation.html', context)
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            
            # Attach all PDFs
            if attach_pdfs:
                from .pdf_service import BoardingPassPDFService
                for det in booking_details:
                    try:
                        p_name = det.passenger.get_full_name() if det.passenger else "Passenger"
                        pdf_buffer = BoardingPassPDFService.generate_boarding_pass(det)
                        
                        pdf_attachment = MIMEApplication(pdf_buffer.getvalue(), _subtype="pdf")
                        filename = f"boarding_pass_{pnr}_{p_name.replace(' ', '_')}.pdf"
                        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                        email.attach(pdf_attachment)
                    except Exception as pdf_err:
                        logger.error(f"⚠️ Failed to attach pass for {det.id}: {pdf_err}")
            
            # Send
            email.send(fail_silently=False)
            logger.info(f"🚀 Bundled check-in confirmation sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send group checkin email: {str(e)}")
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
        contact = getattr(booking, 'contact', None)
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