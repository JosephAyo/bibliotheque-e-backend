from datetime import datetime
from sqlalchemy import Column


def get_verification_email(first_name: str, code: str):
    return f"""<html>
                <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
                    <p>Hello, {first_name},</p>
                    <p>Verify your email with this code: <strong>{code}</strong></p>
                </body>
            </html>"""


def get_reset_password_email(first_name: str, code: str):
    return f"""<html>
                <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
                    <p>Hello, {first_name},</p>
                    <p>Reset your password with this code: <strong>{code}</strong></p>
                </body>
            </html>"""


def get_book_due_soon_email(first_name: str, book_title: str, due_at: Column[datetime]):
    return f"""<html>
                <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
                    <p>Hello, {first_name}.</p>
                    <p>Your book, '{book_title}', is due on {due_at.strftime('%Y-%m-%d')}</p>
                    <p>Best regards,</p>
                    <p>Library Team</p>
                </body>
            </html>"""
