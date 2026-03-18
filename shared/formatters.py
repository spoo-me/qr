"""
Data format functions for structured QR code content.

Each formatter takes keyword arguments and returns the formatted string
ready to be encoded in a QR code.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from schemas.enums import DataFormat


def format_contact(
    name: str,
    phone: str,
    email: Optional[str] = None,
    address: Optional[str] = None,
    company: Optional[str] = None,
    website: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """Format contact data as vCard 3.0."""
    data = f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\n"
    if company:
        data += f"ORG:{company}\n"
    if address:
        data += f"ADR:;;{address};;;;\n"
    data += f"TEL;TYPE=work,voice;VALUE=uri:tel:{phone}\n"
    if email:
        data += f"EMAIL;TYPE=INTERNET;TYPE=WORK;TYPE=PREF:{email}\n"
    if website:
        data += f"URL;TYPE=Homepage:{website}"
    data += "END:VCARD"
    return data


def format_event(
    title: str,
    start: Any = None,
    end: Any = None,
    location: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """Format event data as iCalendar VEVENT."""
    data = f"BEGIN:VEVENT\nSUMMARY:{title}\n"
    try:
        start_str = start.strftime("%Y%m%dT%H%M%SZ")
        end_str = end.strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        start_str = end_str = ""

    if start_str:
        data += f"DTSTART:{start_str}\n"
    if end_str:
        data += f"DTEND:{end_str}\n"
    if location:
        data += f"LOCATION:{location}\n"
    if description:
        data += f"DESCRIPTION:{description}\n"
    data += "END:VEVENT"
    return data


def format_bookmark(title: str, url: str, **kwargs: Any) -> str:
    """Format bookmark data as MEBKM."""
    return f"MEBKM:URL:{url};TITLE:{title};;"


def format_wifi(ssid: str, password: Optional[str] = None, **kwargs: Any) -> str:
    """Format WiFi connection data."""
    if password:
        return f"WIFI:T:WPA;S:{ssid};P:{password};;"
    return f"WIFI:T:nopass;S:{ssid};;"


def format_bitcoin(
    address: str, amount: Any, message: Optional[str] = None, **kwargs: Any
) -> str:
    """Format Bitcoin payment URI."""
    data = f"bitcoin:{address}?amount={amount}"
    if message:
        data += f"&message={message}"
    return data


def format_location(latitude: Any, longitude: Any, **kwargs: Any) -> str:
    """Format geographic coordinates as geo URI."""
    return f"geo:{latitude},{longitude}"


def format_sms(phone: str, message: str, **kwargs: Any) -> str:
    """Format SMS URI."""
    if "+" not in phone:
        phone += "+1"
    return f"sms:{phone}:{message}"


def format_email(email: str, subject: str, message: str, **kwargs: Any) -> str:
    """Format mailto URI."""
    return f"mailto:{email}?subject={subject}&body={message}"


def format_tel(number: str, **kwargs: Any) -> str:
    """Format tel URI."""
    if not number.startswith("+"):
        number += "+1"
    return f"tel:{number}"


FORMAT_REGISTRY: dict[DataFormat, Callable[..., str]] = {
    DataFormat.CONTACT: format_contact,
    DataFormat.EVENT: format_event,
    DataFormat.BOOKMARK: format_bookmark,
    DataFormat.WIFI: format_wifi,
    DataFormat.BITCOIN: format_bitcoin,
    DataFormat.LOCATION: format_location,
    DataFormat.SMS: format_sms,
    DataFormat.EMAIL: format_email,
    DataFormat.TEL: format_tel,
}
