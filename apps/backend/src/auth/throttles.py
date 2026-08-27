from limits import parse_many

from src.auth.config import auth_settings

otp_10m_email, otp_1h_email, otp_10m_ip = parse_many(
    auth_settings.OTP_GENERATION_THROTTLE
)
login_5m_email, login_1h_email, login_10m_ip = parse_many(auth_settings.LOGIN_THROTTLE)
