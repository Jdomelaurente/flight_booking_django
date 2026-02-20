# flightapp/services/pdf_service.py

from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import code128
from io import BytesIO
from django.http import HttpResponse
from decimal import Decimal
import os


class BoardingPassPDFService:
    """
    Professional boarding pass and itinerary PDF generation service
    """
    
    # Refined color palette - professional navy/cyan theme
    PRIMARY_DARK = HexColor('#0f172a')      # Navy header
    PRIMARY_ACCENT = HexColor('#3b82f6')    # Blue accent
    SECONDARY_ACCENT = HexColor('#06b6d4')  # Cyan accent
    TEXT_PRIMARY = HexColor('#1e293b')      # Dark slate text
    TEXT_SECONDARY = HexColor('#64748b')    # Gray text
    BACKGROUND_LIGHT = HexColor('#f8fafc')  # Light gray background
    BORDER_COLOR = HexColor('#e2e8f0')      # Border gray
    WHITE = HexColor('#ffffff')
    
    @staticmethod
    def generate_boarding_pass(booking_detail, return_flight=False):
        """
        Generate a professional boarding pass PDF
        
        Args:
            booking_detail: BookingDetail model instance
            return_flight: Boolean indicating if this is a return flight
        
        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        
        # Standard IATA boarding pass size (8.27 x 3.15 inches / 210 x 80mm)
        width = 8.27 * inch
        height = 3.15 * inch
        
        c = canvas.Canvas(buffer, pagesize=(width, height))
        
        # Get data
        passenger = booking_detail.passenger
        schedule = booking_detail.schedule
        flight = schedule.flight if schedule else None
        route = flight.route if flight else None
        seat = booking_detail.seat
        
        passenger_name = passenger.get_full_name().upper() if passenger else "PASSENGER"
        flight_number = flight.flight_number if flight else "FL000"
        origin = route.origin_airport.code if route else "XXX"
        destination = route.destination_airport.code if route else "XXX"
        origin_city = route.origin_airport.city if route else "Origin"
        destination_city = route.destination_airport.city if route else "Destination"
        
        departure_time = schedule.departure_time.strftime("%H:%M") if schedule else "00:00"
        boarding_time = (schedule.departure_time - __import__('datetime').timedelta(minutes=40)).strftime("%H:%M") if schedule else "00:00"
        departure_date = schedule.departure_time.strftime("%d %b %Y").upper() if schedule else "00 JAN 0000"
        
        seat_number = seat.seat_number if seat else "--"
        gate = getattr(schedule, 'gate', 'TBA')
        group = "A" if seat and seat.seat_number and int(''.join(filter(str.isdigit, seat.seat_number))) <= 10 else "B"
        
        # Colors
        primary = BoardingPassPDFService.PRIMARY_DARK
        accent = BoardingPassPDFService.SECONDARY_ACCENT if return_flight else BoardingPassPDFService.PRIMARY_ACCENT
        text = BoardingPassPDFService.TEXT_PRIMARY
        text_secondary = BoardingPassPDFService.TEXT_SECONDARY
        bg_light = BoardingPassPDFService.BACKGROUND_LIGHT
        border = BoardingPassPDFService.BORDER_COLOR
        
        # === BACKGROUND ===
        c.setFillColor(bg_light)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        
        # === LEFT SECTION (Main Pass - 60%) ===
        left_width = width * 0.58
        
        # Header bar with accent color
        c.setFillColor(accent)
        c.rect(0, height - 0.5*inch, left_width - 0.1*inch, 0.5*inch, fill=1, stroke=0)
        
        # Flight type indicator
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        flight_label = "RETURN" if return_flight else "OUTBOUND"
        c.drawString(0.25*inch, height - 0.32*inch, flight_label)
        
        # Airline name on header
        c.setFont("Helvetica", 9)
        airline_name = getattr(flight.airline, 'name', 'AIRLINE') if flight else 'AIRLINE'
        c.drawRightString(left_width - 0.35*inch, height - 0.32*inch, airline_name.upper())
        
        # === MAIN CONTENT AREA ===
        content_top = height - 0.7*inch
        
        # Passenger Name (prominent)
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 8)
        c.drawString(0.25*inch, content_top, "PASSENGER NAME")
        
        c.setFillColor(text)
        c.setFont("Helvetica-Bold", 16)
        # Truncate if too long
        display_name = passenger_name[:25] + "..." if len(passenger_name) > 25 else passenger_name
        c.drawString(0.25*inch, content_top - 0.22*inch, display_name)
        
        # Horizontal divider
        c.setStrokeColor(border)
        c.setLineWidth(0.5)
        c.line(0.25*inch, content_top - 0.35*inch, left_width - 0.35*inch, content_top - 0.35*inch)
        
        # === FLIGHT INFO GRID ===
        grid_y = content_top - 0.55*inch
        col_width = (left_width - 0.6*inch) / 3
        
        # Row 1: Flight, Date, Gate
        labels = ["FLIGHT", "DATE", "GATE"]
        values = [flight_number, departure_date, gate]
        
        for i, (label, value) in enumerate(zip(labels, values)):
            x = 0.25*inch + (i * col_width)
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 7)
            c.drawString(x, grid_y, label)
            
            c.setFillColor(text)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x, grid_y - 0.18*inch, str(value))
        
        # Row 2: Boarding Time, Seat, Group
        grid_y2 = grid_y - 0.45*inch
        labels2 = ["BOARDING TIME", "SEAT", "GROUP"]
        values2 = [boarding_time, seat_number, group]
        
        for i, (label, value) in enumerate(zip(labels2, values2)):
            x = 0.25*inch + (i * col_width)
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 7)
            c.drawString(x, grid_y2, label)
            
            c.setFillColor(text)
            # Seat gets larger font
            if label == "SEAT":
                c.setFont("Helvetica-Bold", 18)
                c.setFillColor(accent)
            else:
                c.setFont("Helvetica-Bold", 12)
                c.setFillColor(text)
            c.drawString(x, grid_y2 - 0.2*inch, str(value))
        
        # === ROUTE DISPLAY ===
        route_y = 0.65*inch
        
        # Origin
        c.setFillColor(text)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(0.25*inch, route_y, origin)
        
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 8)
        c.drawString(0.25*inch, route_y - 0.15*inch, origin_city.upper())
        
        # Arrow/plane icon
        c.setStrokeColor(accent)
        c.setLineWidth(2)
        arrow_y = route_y + 0.08*inch
        # Draw simple arrow
        c.line(1.3*inch, arrow_y, 2.2*inch, arrow_y)
        # Arrowhead
        c.line(2.0*inch, arrow_y + 0.08*inch, 2.2*inch, arrow_y)
        c.line(2.0*inch, arrow_y - 0.08*inch, 2.2*inch, arrow_y)
        
        # Destination
        c.setFillColor(text)
        c.setFont("Helvetica-Bold", 24)
        c.drawRightString(left_width - 0.35*inch, route_y, destination)
        
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 8)
        c.drawRightString(left_width - 0.35*inch, route_y - 0.15*inch, destination_city.upper())
        
        # Departure time large
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(left_width/2 - 0.05*inch, route_y + 0.35*inch, departure_time)
        
        # === RIGHT SECTION (Stub - 40%) ===
        stub_x = left_width + 0.05*inch
        stub_width = width - stub_x - 0.25*inch
        
        # Stub header
        c.setFillColor(primary)
        c.rect(stub_x, height - 0.5*inch, stub_width, 0.5*inch, fill=1, stroke=0)
        
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(stub_x + stub_width/2, height - 0.32*inch, "BOARDING PASS")
        
        # Stub content background
        c.setFillColor(white)
        c.rect(stub_x, 0.25*inch, stub_width, height - 0.75*inch, fill=1, stroke=0)
        
        # Stub info
        stub_content_y = height - 0.75*inch
        
        # Passenger name (stub)
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 7)
        c.drawString(stub_x + 0.15*inch, stub_content_y, "PASSENGER")
        
        c.setFillColor(text)
        c.setFont("Helvetica-Bold", 10)
        stub_name = passenger_name[:20] + "..." if len(passenger_name) > 20 else passenger_name
        c.drawString(stub_x + 0.15*inch, stub_content_y - 0.16*inch, stub_name)
        
        # Stub flight info - compact grid
        info_y = stub_content_y - 0.45*inch
        c.setFont("Helvetica", 7)
        c.setFillColor(text_secondary)
        c.drawString(stub_x + 0.15*inch, info_y, "FLIGHT")
        c.drawString(stub_x + 0.15*inch + stub_width*0.35, info_y, "SEAT")
        c.drawString(stub_x + 0.15*inch + stub_width*0.7, info_y, "GATE")
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(text)
        c.drawString(stub_x + 0.15*inch, info_y - 0.16*inch, flight_number)
        c.setFillColor(accent)
        c.drawString(stub_x + 0.15*inch + stub_width*0.35, info_y - 0.16*inch, seat_number)
        c.setFillColor(text)
        c.drawString(stub_x + 0.15*inch + stub_width*0.7, info_y - 0.16*inch, str(gate))
        
        # Route (stub)
        route_stub_y = info_y - 0.45*inch
        c.setFont("Helvetica", 7)
        c.setFillColor(text_secondary)
        c.drawString(stub_x + 0.15*inch, route_stub_y, "FROM")
        c.drawRightString(stub_x + stub_width - 0.15*inch, route_stub_y, "TO")
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(text)
        c.drawString(stub_x + 0.15*inch, route_stub_y - 0.16*inch, origin)
        c.drawRightString(stub_x + stub_width - 0.15*inch, route_stub_y - 0.16*inch, destination)
        
        # === BARCODE ===
        barcode_y = 0.45*inch
        barcode_height = 0.55*inch
        
        # Generate barcode
        barcode_value = f"{booking_detail.id}{flight_number}{origin}{destination}{seat_number}"
        barcode = code128.Code128(barcode_value, barHeight=barcode_height, barWidth=0.01*inch)
        
        # Draw barcode
        barcode.drawOn(c, stub_x + 0.1*inch, barcode_y - 0.1*inch)
        
        # Barcode number below
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 7)
        c.drawCentredString(stub_x + stub_width/2, barcode_y - 0.2*inch, barcode_value[:20])
        
        # === PERFORATION LINE ===
        perf_x = left_width
        c.setDash(3, 3)
        c.setStrokeColor(border)
        c.setLineWidth(1)
        c.line(perf_x, 0.25*inch, perf_x, height - 0.25*inch)
        c.setDash()
        
        # Scissor icons at perforation
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 8)
        c.drawCentredString(perf_x, height - 0.15*inch, "?")
        c.drawCentredString(perf_x, 0.15*inch, "?")
        
        # === SECURITY FOOTER ===
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 6)
        c.drawString(0.25*inch, 0.15*inch, "This document is subject to verification. Present valid ID at gate.")
        
        c.save()
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_itinerary_pdf(booking):
        """
        Generate professional itinerary PDF
        
        Args:
            booking: Booking model instance
        
        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Colors
        primary = BoardingPassPDFService.PRIMARY_DARK
        accent = BoardingPassPDFService.PRIMARY_ACCENT
        text = BoardingPassPDFService.TEXT_PRIMARY
        text_secondary = BoardingPassPDFService.TEXT_SECONDARY
        bg_light = BoardingPassPDFService.BACKGROUND_LIGHT
        border = BoardingPassPDFService.BORDER_COLOR
        white = BoardingPassPDFService.WHITE
        
        # === HEADER ===
        # Dark header background
        c.setFillColor(primary)
        c.rect(0, height - 1.4*inch, width, 1.4*inch, fill=1, stroke=0)
        
        # Accent line
        c.setFillColor(accent)
        c.rect(0, height - 1.4*inch, width, 0.08*inch, fill=1, stroke=0)
        
        # Logo area (left)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(0.8*inch, height - 0.85*inch, "TRAVEL ITINERARY")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor('#94a3b8'))
        c.drawString(0.8*inch, height - 1.1*inch, "E-TICKET / BOOKING CONFIRMATION")
        
        # Booking reference box (right)
        ref_x = width - 3.2*inch
        c.setFillColor(HexColor('#1e293b'))
        c.roundRect(ref_x, height - 1.2*inch, 2.4*inch, 0.9*inch, 4, fill=1, stroke=0)
        
        c.setFillColor(HexColor('#94a3b8'))
        c.setFont("Helvetica", 9)
        c.drawString(ref_x + 0.15*inch, height - 0.55*inch, "BOOKING REFERENCE")
        
        booking_ref = f"BK{booking.id:08d}"
        c.setFillColor(white)
        c.setFont("Courier-Bold", 16)
        c.drawString(ref_x + 0.15*inch, height - 0.85*inch, booking_ref)
        
        # === BOOKING INFO SECTION ===
        y_pos = height - 1.8*inch
        
        # Section title
        c.setFillColor(text)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.8*inch, y_pos, "BOOKING DETAILS")
        
        # Info card
        y_pos -= 0.2*inch
        card_height = 1.3*inch
        
        c.setFillColor(white)
        c.roundRect(0.6*inch, y_pos - card_height, width - 1.2*inch, card_height, 6, fill=1, stroke=0)
        c.setStrokeColor(border)
        c.setLineWidth(0.5)
        c.roundRect(0.6*inch, y_pos - card_height, width - 1.2*inch, card_height, 6, fill=0, stroke=1)
        
        # Contact info
        contact = booking.contact
        c.setFillColor(text)
        c.setFont("Helvetica-Bold", 10)
        
        info_items = [
            ("Primary Contact", f"{contact.first_name} {contact.last_name}" if contact else "N/A"),
            ("Email Address", contact.email if contact else "N/A"),
            ("Phone Number", contact.phone if contact else "N/A"),
            ("Booking Date", booking.created_at.strftime("%d %b %Y") if booking.created_at else "N/A"),
            ("Trip Type", "Round Trip" if booking.trip_type == 'round_trip' else "One Way"),
        ]
        
        col1_x = 0.9*inch
        col2_x = width/2 + 0.2*inch
        line_height = 0.22*inch
        
        for i, (label, value) in enumerate(info_items):
            x = col1_x if i < 3 else col2_x
            y = y_pos - 0.25*inch - ((i % 3) * line_height)
            
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 8)
            c.drawString(x, y, label.upper())
            
            c.setFillColor(text)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y - 0.14*inch, str(value))
        
        # === FLIGHT SEGMENTS ===
        y_pos -= 1.6*inch
        
        c.setFillColor(text)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.8*inch, y_pos, "FLIGHT DETAILS")
        
        # Get booking details
        details = booking.details.select_related(
            'passenger', 'schedule__flight__airline',
            'schedule__flight__route__origin_airport',
            'schedule__flight__route__destination_airport',
            'seat'
        ).all()
        
        y_pos -= 0.3*inch
        
        for idx, detail in enumerate(details):
            if y_pos < 2.5*inch:
                c.showPage()
                y_pos = height - 1*inch
            
            schedule = detail.schedule
            flight = schedule.flight if schedule else None
            route = flight.route if flight else None
            
            is_return = idx > 0 and booking.trip_type == 'round_trip'
            segment_color = BoardingPassPDFService.SECONDARY_ACCENT if is_return else accent
            
            # Flight card
            card_h = 2.2*inch
            
            # Card shadow effect
            c.setFillColor(HexColor('#e2e8f0'))
            c.roundRect(0.65*inch, y_pos - card_h - 0.02*inch, width - 1.3*inch, card_h, 6, fill=1, stroke=0)
            
            # Card background
            c.setFillColor(white)
            c.roundRect(0.6*inch, y_pos - card_h, width - 1.2*inch, card_h, 6, fill=1, stroke=0)
            
            # Left accent bar
            c.setFillColor(segment_color)
            c.roundRect(0.6*inch, y_pos - card_h, 0.08*inch, card_h, 3, fill=1, stroke=0)
            
            # Flight type badge
            badge_y = y_pos - 0.25*inch
            c.setFillColor(segment_color)
            c.roundRect(0.9*inch, badge_y - 0.02*inch, 0.9*inch, 0.24*inch, 3, fill=1, stroke=0)
            
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 8)
            flight_type = "RETURN" if is_return else "OUTBOUND"
            c.drawCentredString(0.9*inch + 0.45*inch, badge_y + 0.05*inch, flight_type)
            
            # Flight number
            c.setFillColor(text)
            c.setFont("Courier-Bold", 14)
            c.drawRightString(width - 0.9*inch, badge_y + 0.05*inch, flight.flight_number if flight else "N/A")
            
            # Route display
            route_y = y_pos - 0.9*inch
            
            # Origin
            c.setFillColor(text)
            c.setFont("Helvetica-Bold", 28)
            origin_code = route.origin_airport.code if route else "XXX"
            c.drawString(0.9*inch, route_y, origin_code)
            
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 9)
            origin_city = route.origin_airport.city if route else "Origin"
            c.drawString(0.9*inch, route_y - 0.18*inch, origin_city)
            
            # Arrow
            c.setStrokeColor(segment_color)
            c.setLineWidth(2)
            arrow_y = route_y + 0.12*inch
            c.line(2.4*inch, arrow_y, 3.6*inch, arrow_y)
            # Arrowhead
            c.line(3.4*inch, arrow_y + 0.1*inch, 3.6*inch, arrow_y)
            c.line(3.4*inch, arrow_y - 0.1*inch, 3.6*inch, arrow_y)
            
            # Duration
            duration = "2h 30m"  # Calculate from schedule
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 8)
            c.drawCentredString(3.0*inch, route_y + 0.25*inch, duration)
            
            # Destination
            c.setFillColor(text)
            c.setFont("Helvetica-Bold", 28)
            dest_code = route.destination_airport.code if route else "XXX"
            c.drawRightString(width - 0.9*inch, route_y, dest_code)
            
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 9)
            dest_city = route.destination_airport.city if route else "Destination"
            c.drawRightString(width - 0.9*inch, route_y - 0.18*inch, dest_city)
            
            # Times row
            times_y = y_pos - 1.5*inch
            
            # Departure
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 8)
            c.drawString(0.9*inch, times_y, "DEPARTURE")
            
            c.setFillColor(text)
            c.setFont("Helvetica-Bold", 12)
            dep_time = schedule.departure_time.strftime("%H:%M") if schedule else "--:--"
            dep_date = schedule.departure_time.strftime("%d %b %Y") if schedule else "---"
            c.drawString(0.9*inch, times_y - 0.18*inch, dep_time)
            c.setFont("Helvetica", 9)
            c.drawString(0.9*inch, times_y - 0.32*inch, dep_date)
            
            # Arrival
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 8)
            c.drawString(width/2 - 0.3*inch, times_y, "ARRIVAL")
            
            c.setFillColor(text)
            c.setFont("Helvetica-Bold", 12)
            arr_time = schedule.arrival_time.strftime("%H:%M") if schedule else "--:--"
            arr_date = schedule.arrival_time.strftime("%d %b %Y") if schedule else "---"
            c.drawString(width/2 - 0.3*inch, times_y - 0.18*inch, arr_time)
            c.setFont("Helvetica", 9)
            c.drawString(width/2 - 0.3*inch, times_y - 0.32*inch, arr_date)
            
            # Passenger & Seat
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 8)
            c.drawRightString(width - 0.9*inch, times_y, "PASSENGER")
            
            c.setFillColor(text)
            c.setFont("Helvetica-Bold", 11)
            passenger_name = detail.passenger.get_full_name() if detail.passenger else "N/A"
            c.drawRightString(width - 0.9*inch, times_y - 0.18*inch, passenger_name)
            
            seat_num = detail.seat.seat_number if detail.seat else "TBA"
            c.setFillColor(segment_color)
            c.setFont("Helvetica-Bold", 14)
            c.drawRightString(width - 0.9*inch, times_y - 0.38*inch, f"Seat {seat_num}")
            
            y_pos -= card_h + 0.3*inch
        
        # === PAYMENT SUMMARY ===
        if y_pos < 2.2*inch:
            c.showPage()
            y_pos = height - 1*inch
        
        y_pos -= 0.2*inch
        c.setFillColor(text)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.8*inch, y_pos, "PAYMENT SUMMARY")
        
        # Summary card
        y_pos -= 0.25*inch
        summary_h = 1.6*inch
        
        c.setFillColor(white)
        c.roundRect(0.6*inch, y_pos - summary_h, width - 1.2*inch, summary_h, 6, fill=1, stroke=0)
        c.setStrokeColor(border)
        c.roundRect(0.6*inch, y_pos - summary_h, width - 1.2*inch, summary_h, 6, fill=0, stroke=1)
        
        # Summary items
        summary_items = [
            ("Base Fare", f"?{booking.base_fare_total:,.2f}" if booking.base_fare_total else "?0.00"),
            ("Taxes & Fees", f"?{booking.tax_total:,.2f}" if booking.tax_total else "?0.00"),
        ]
        
        if booking.insurance_total:
            summary_items.append(("Travel Insurance", f"?{booking.insurance_total:,.2f}"))
        
        item_y = y_pos - 0.3*inch
        c.setFont("Helvetica", 10)
        
        for label, value in summary_items:
            c.setFillColor(text_secondary)
            c.drawString(0.9*inch, item_y, label)
            
            c.setFillColor(text)
            c.drawRightString(width - 0.9*inch, item_y, value)
            item_y -= 0.25*inch
        
        # Total line
        c.setStrokeColor(border)
        c.line(0.9*inch, item_y + 0.05*inch, width - 0.9*inch, item_y + 0.05*inch)
        
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.9*inch, item_y - 0.15*inch, "TOTAL PAID")
        c.drawRightString(width - 0.9*inch, item_y - 0.15*inch, f"?{booking.total_amount:,.2f}" if booking.total_amount else "?0.00")
        
        # Payment method
        payment = booking.payments.filter(status='Completed').first()
        if payment:
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 9)
            c.drawString(0.9*inch, item_y - 0.45*inch, f"Paid via {payment.method}")
            c.setFont("Helvetica", 8)
            c.drawString(0.9*inch, item_y - 0.6*inch, f"Transaction ID: {payment.transaction_id or 'N/A'}")
        
        # === FOOTER ===
        c.setFillColor(primary)
        c.rect(0, 0, width, 0.6*inch, fill=1, stroke=0)
        
        c.setFillColor(HexColor('#94a3b8'))
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, 0.35*inch, "Thank you for choosing us. Have a pleasant flight!")
        
        c.setFont("Helvetica", 7)
        c.drawCentredString(width/2, 0.15*inch, "For assistance: support@airline.com | (02) 8855-8888")
        
        c.save()
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def download_boarding_pass(booking_detail_id):
        """Download boarding pass view helper"""
        from app.models import BookingDetail
        
        try:
            detail = BookingDetail.objects.select_related(
                'passenger', 'schedule__flight__route__origin_airport',
                'schedule__flight__route__destination_airport', 'seat'
            ).get(id=booking_detail_id)
            
            buffer = BoardingPassPDFService.generate_boarding_pass(detail)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            filename = f"boarding_pass_{detail.passenger.last_name}_{detail.schedule.flight.flight_number if detail.schedule else 'FL'}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except BookingDetail.DoesNotExist:
            return None
    
    @staticmethod
    def download_itinerary(booking_id):
        """Download itinerary view helper"""
        from app.models import Booking
        
        try:
            booking = Booking.objects.select_related('contact').prefetch_related(
                'details', 'payments'
            ).get(id=booking_id)
            
            buffer = BoardingPassPDFService.generate_itinerary_pdf(booking)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            filename = f"itinerary_BK{booking.id:08d}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Booking.DoesNotExist:
            return None