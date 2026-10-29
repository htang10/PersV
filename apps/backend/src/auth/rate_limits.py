from limits import parse_many

from src.auth.config import auth_settings
from src.core.rate_limiter import RateLimiter


# Naming convention: {action}_{scope}_{role}
otp_email_burst, otp_email_sustained, otp_ip = parse_many(
    auth_settings.OTP_GENERATION_THROTTLE
)
login_email_burst, login_email_sustained, login_ip = parse_many(
    auth_settings.LOGIN_THROTTLE
)
anon_id_ip_burst, anon_id_ip_sustained = parse_many(auth_settings.ANON_ID_THROTTLE)


otp_rt = RateLimiter(
    "otp",
    email=[otp_email_burst, otp_email_sustained],
    ip=[otp_ip],
)
login_rt = RateLimiter(
    "login",
    email=[login_email_burst, login_email_sustained],
    ip=[login_ip],
)
anon_id_rt = RateLimiter(
    "anon_conn",
    ip=[anon_id_ip_burst, anon_id_ip_sustained],
)
