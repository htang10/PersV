from src.auth.config import auth_settings
from src.core.rate_limiter import RateLimiter

otp_rl = RateLimiter("otp", auth_settings.OTP_LIMITS)
login_rl = RateLimiter("login", auth_settings.EMAIL_VERIFICATION_LIMITS)
anon_id_rl = RateLimiter("anon", auth_settings.ANON_ID_LIMITS)
email_change_verification_rl = RateLimiter(
    "email-change/verification", auth_settings.EMAIL_VERIFICATION_LIMITS
)
email_change_rl = RateLimiter(
    "email-change/attempts", auth_settings.EMAIL_CHANGE_LIMITS
)
