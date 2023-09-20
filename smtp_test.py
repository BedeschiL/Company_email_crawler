import smtplib
import unittest
from unittest.mock import patch
from smtp_verify import SMTPVerify

class TestGetSpecificRecordsByPriority(unittest.TestCase):
    def test_get_specific_records_by_priority(self):
        smtp_verify = SMTPVerify()
        # Mock the DNS resolver for testing
        with patch("dns.resolver.resolve") as mock_resolve:
            mock_resolve.return_value = [
                "10 mail.example.com",
                "20 mail2.example.com",
            ]
            records = smtp_verify.get_specific_records_by_priority("example.com", "MX")
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["priority"], "10")
            self.assertEqual(records[1]["value"], "mail2.example.com")


class TestCheckCatchAll(unittest.TestCase):
    def test_check_catch_all_detected(self):
        smtp_verify = SMTPVerify()
        servers = ["mail1.example.com", "mail2.example.com"]
        with patch("smtp_verify.SMTPVerify.send_rcpto") as mock_send_mail:
            mock_send_mail.return_value = True
            status, result = smtp_verify.check_catch_all(servers, "example.com")
            self.assertTrue(status)
            self.assertEqual(
                result["status"], "[Catch-all] detected or any other countermeasure"
            )

    def test_check_catch_all_not_detected(self):
        smtp_verify = SMTPVerify()
        servers = ["mail1.example.com", "mail2.example.com"]
        with patch("smtp_verify.SMTPVerify.send_rcpto") as mock_send_mail:
            mock_send_mail.return_value = False
            status, result = smtp_verify.check_catch_all(servers, "example.com")
            self.assertFalse(status)
            self.assertEqual(result["status"], "[Catch-all] not detected")


class TestRandomChar(unittest.TestCase):
    def test_random_char(self):
        smtp_verify = SMTPVerify()
        result = smtp_verify.random_char(5)
        self.assertEqual(len(result), 5)
        self.assertTrue(result.isalpha())


class TestSendMail(unittest.TestCase):
    @patch("smtplib.SMTP")
    def test_send_mail_valid(self, mock_smtp):
        smtp_verify = SMTPVerify()

        mock_server = mock_smtp.return_value
        mock_server.connect.return_value = (220, "Connection established")
        mock_server.ehlo.return_value = (250, "Hello")
        mock_server.mail.return_value = (250, "OK")
        mock_server.rcpt.return_value = (250, "OK")
        ret = smtp_verify.send_rcpto(["mail.example.com"], "test@example.com")
        self.assertTrue(ret)

    @patch("smtplib.SMTP")
    def test_send_mail_invalid(self, mock_smtp):
        smtp_verify = SMTPVerify()

        mock_server = mock_smtp.return_value
        mock_server.connect.return_value = (220, "Connection established")
        mock_server.ehlo.return_value = (250, "Hello")
        mock_server.mail.return_value = (250, "OK")
        mock_server.rcpt.return_value = (550, "User not found")
        ret = smtp_verify.send_rcpto(["mail.example.com"], "test@example.com")
        self.assertFalse(ret)


class TestValidateEmail(unittest.TestCase):
    def test_validate_email_valid(self):
        smtp_verify = SMTPVerify()

        valid_emails = ["test@example.com", "user.name@example.co.uk"]
        for email in valid_emails:
            self.assertTrue(smtp_verify.validate_email(email))

    def test_validate_email_invalid(self):
        smtp_verify = SMTPVerify()

        invalid_emails = ["invalid", "user@domain", "@example.com"]
        for email in invalid_emails:
            self.assertFalse(smtp_verify.validate_email(email))


class TestGetServerInfo(unittest.TestCase):
    @patch("smtplib.SMTP")
    def test_get_server_info_valid(self, mock_smtp):
        smtp_verify = SMTPVerify()
        mock_server = mock_smtp.return_value
        mock_server.connect.return_value = (220, "Connection established")
        code, msg = smtp_verify.get_server_info(mock_server, "mail.example.com")
        self.assertEqual(code, 220)
        self.assertEqual(msg, "Connection established")

    def test_get_server_info_invalid(self):
        smtp_verify = SMTPVerify()


        mock_server = smtplib.SMTP()
        code, msg = smtp_verify.get_server_info(mock_server, "invalidserver")
        self.assertEqual(code, False)
        self.assertEqual(
            "Server not found or unreachable", "Server not found or unreachable"
        )


class TestVerify(unittest.TestCase):
    @patch("builtins.print")
    @patch("smtp_verify.SMTPVerify.validate_email")
    @patch("smtp_verify.SMTPVerify.check_catch_all")
    @patch("smtp_verify.SMTPVerify.get_specific_records_by_priority")
    def test_verify_valid(
        self, mock_records, mock_catch_all, mock_validate_email, mock_print
    ):
        smtp_verify = SMTPVerify()

        mock_records.return_value = [{"priority": "10", "value": "mail.example.com"}]
        mock_catch_all.return_value = (
            True,
            "[Catch-all] detected or any other countermeasure",
        )
        mock_validate_email.return_value = True
        smtp_verify.verify("test@example.com", debug_level=0)
        mock_print.assert_called_with(
            "t is not a valid email\n"
        )

    @patch("builtins.print")
    @patch("smtp_verify.SMTPVerify.validate_email")
    @patch("smtp_verify.SMTPVerify.check_catch_all")
    @patch("smtp_verify.SMTPVerify.get_specific_records_by_priority")
    def test_verify_invalid(
        self, mock_records, mock_catch_all, mock_validate_email, mock_print
    ):
        smtp_verify = SMTPVerify()

        mock_records.return_value = [{"priority": "10", "value": "mail.example.com"}]
        mock_catch_all.return_value = (False, {"status": "[Catch-all] not detected"})
        mock_validate_email.return_value = False
        smtp_verify.verify("invalid", debug_level=0)
        mock_print.assert_called_with("i is not a valid email\n")


if __name__ == "__main__":
    unittest.main()