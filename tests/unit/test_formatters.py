"""Unit tests for shared.formatters — data format functions."""

from shared.formatters import (
    format_bitcoin,
    format_bookmark,
    format_contact,
    format_email,
    format_event,
    format_location,
    format_sms,
    format_tel,
    format_wifi,
    FORMAT_REGISTRY,
)
from schemas.enums import DataFormat


class TestFormatContact:
    def test_minimal_contact(self):
        result = format_contact(name="John Doe", phone="1234567890")
        assert "BEGIN:VCARD" in result
        assert "FN:John Doe" in result
        assert "tel:1234567890" in result
        assert "END:VCARD" in result

    def test_full_contact(self):
        result = format_contact(
            name="Jane",
            phone="555",
            email="jane@example.com",
            address="123 Main St",
            company="Acme",
            website="https://example.com",
        )
        assert "ORG:Acme" in result
        assert "ADR:;;123 Main St" in result
        assert "EMAIL" in result
        assert "URL;TYPE=Homepage:https://example.com" in result


class TestFormatEvent:
    def test_minimal_event(self):
        result = format_event(title="Meeting")
        assert "BEGIN:VEVENT" in result
        assert "SUMMARY:Meeting" in result
        assert "END:VEVENT" in result

    def test_event_with_location(self):
        result = format_event(title="Lunch", location="Cafe")
        assert "LOCATION:Cafe" in result


class TestFormatBookmark:
    def test_bookmark(self):
        result = format_bookmark(title="Google", url="https://google.com")
        assert result == "MEBKM:URL:https://google.com;TITLE:Google;;"


class TestFormatWifi:
    def test_wifi_with_password(self):
        result = format_wifi(ssid="MyNetwork", password="secret123")
        assert result == "WIFI:T:WPA;S:MyNetwork;P:secret123;;"

    def test_wifi_without_password(self):
        result = format_wifi(ssid="OpenNet")
        assert result == "WIFI:T:nopass;S:OpenNet;;"


class TestFormatBitcoin:
    def test_bitcoin_minimal(self):
        result = format_bitcoin(address="1Abc", amount=0.001)
        assert result == "bitcoin:1Abc?amount=0.001"

    def test_bitcoin_with_message(self):
        result = format_bitcoin(address="1Abc", amount=0.01, message="Donation")
        assert "&message=Donation" in result


class TestFormatLocation:
    def test_location(self):
        result = format_location(latitude=40.7128, longitude=-74.0060)
        assert result == "geo:40.7128,-74.006"


class TestFormatSms:
    def test_sms_with_country_code(self):
        result = format_sms(phone="+1234567890", message="Hello")
        assert result == "sms:+1234567890:Hello"

    def test_sms_without_country_code(self):
        result = format_sms(phone="1234567890", message="Hi")
        assert "+1" in result


class TestFormatEmail:
    def test_email(self):
        result = format_email(email="test@example.com", subject="Hi", message="Hello")
        assert result == "mailto:test@example.com?subject=Hi&body=Hello"


class TestFormatTel:
    def test_tel_with_plus(self):
        result = format_tel(number="+15551234567")
        assert result == "tel:+15551234567"

    def test_tel_without_plus(self):
        result = format_tel(number="5551234567")
        assert "+1" in result


class TestFormatRegistry:
    def test_all_formats_registered(self):
        for fmt in DataFormat:
            assert fmt in FORMAT_REGISTRY, f"{fmt} not in FORMAT_REGISTRY"

    def test_registry_size(self):
        assert len(FORMAT_REGISTRY) == len(DataFormat)
