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
