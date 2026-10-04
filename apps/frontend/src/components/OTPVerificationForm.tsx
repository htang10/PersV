import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useNavigateNotice } from "@/hooks/useNavigateNotice";
import { login, sendOTP } from "@/services/auth";

interface VerificationFormProps {
	targetEmail: string;
	onBackToLogin: () => void;
}

export function OTPVerificationForm({
	targetEmail,
	onBackToLogin,
}: VerificationFormProps) {
	const navigateNotice = useNavigateNotice();
	const { setAccessToken, setIsAuthenticated } = useAuth();

	const [resendCooldown, setResendCooldown] = useState<number>(0);
	const [otp, setOTP] = useState<string[]>(Array(6).fill(""));
	const [otpError, setOTPError] = useState<string | null>(null);

	const formRef = useRef<HTMLFormElement>(null);
	const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
	const cooldownID = useRef<NodeJS.Timeout | null>(null);

	useEffect(() => {
		// Focus the leftmost empty cell initially
		const firstEmptyIndex = otp.findIndex((digit) => digit === "");
		const targetIndex =
			firstEmptyIndex === -1 ? otp.length - 1 : firstEmptyIndex;
		inputRefs.current[targetIndex]?.focus();

		// Start the count down until next resend
		startResendCooldown();

		return () => {
			cooldownID.current && clearInterval(cooldownID.current);
		};
	}, []);

	const startResendCooldown = () => {
		setResendCooldown(30);
		cooldownID.current = setInterval(() => {
			setResendCooldown((cooldown) => {
				if (cooldown <= 1) {
					cooldownID.current && clearInterval(cooldownID.current);
					return 0;
				}
				return cooldown - 1;
			});
		}, 1000);
	};

	const updateOTPDigit = (inputDigit: string, position: number) => {
		if (!/^\d?$/.test(inputDigit)) return; // Reject non-digit characters

		setOTP((otp) =>
			otp.map((currentDigit, index) =>
				position === index ? inputDigit : currentDigit,
			),
		);
	};

	const clearOTPInputs = () => {
		setOTP(Array(6).fill(""));
	};

	const handleOTPDigitChange = (value: string, index: number) => {
		const digit = value.replace(/[^0-9]/g, "").slice(-1); // keep only the last typed digit, strip non-numeric
		updateOTPDigit(digit, index);

		if (digit && index < otp.length - 1) {
			inputRefs.current[index + 1]?.focus(); // move to next cell
		}

		const nextOtp = [...otp];
		nextOtp[index] = digit;
		if (digit && index === otp.length - 1 && nextOtp.every((d) => d !== "")) {
			// last digit just entered AND all cells are now filled — auto-submit
			formRef.current?.requestSubmit();
		}
	};

	const handleOTPPaste = (event: React.ClipboardEvent<HTMLInputElement>) => {
		event.preventDefault();
		const pasted = event.clipboardData.getData("text").replace(/[^0-9]/g, "");
		if (!pasted) return;

		const digits = pasted.slice(0, otp.length).split("");
		const nextOtp = Array(otp.length).fill("");
		digits.forEach((digit, i) => {
			nextOtp[i] = digit;
		});
		setOTP(nextOtp);

		const lastFilledIndex = digits.length - 1;
		const focusIndex = Math.min(lastFilledIndex + 1, otp.length - 1);
		inputRefs.current[focusIndex]?.focus();

		if (digits.length === otp.length) {
			// Auto submit when the full code is pasted, same as typing the last digit
			setTimeout(() => formRef.current?.requestSubmit(), 1000);
		}
	};

	const handleLogin = async (event: React.SubmitEvent<HTMLFormElement>) => {
		event.preventDefault();
		const code = otp.join("");
		try {
			const response = await login(targetEmail, code);
			setAccessToken(response.token);
			setIsAuthenticated(true);
			setOTPError(null);
			navigateNotice("/connect", {
				type: "info",
				message: "Logged in successfully.",
			});
		} catch (_error) {
			setOTPError("Invallid or expired code");
			clearOTPInputs();
			inputRefs.current[0]?.focus();
		}
	};

	const handleOTPResend = async () => {
		await sendOTP(targetEmail);
		startResendCooldown();
	};

	const handleEmailChange = async () => {
		cooldownID.current && clearInterval(cooldownID.current);
		setResendCooldown(0);
		clearOTPInputs();
		onBackToLogin();
	};

	return (
		<div>
			<span>Enter the code sent to {targetEmail}</span>
			<form ref={formRef} onSubmit={handleLogin}>
				<div>
					{otp.map((digit, index) => (
						<div key={index}>
							<input
								ref={(el) => {
									inputRefs.current[index] = el;
								}}
								type="text"
								inputMode="numeric"
								pattern="[0-9]"
								maxLength={1}
								value={digit}
								onChange={(e) => handleOTPDigitChange(e.target.value, index)}
								onKeyDown={(e) => {
									if (e.key === "Backspace" && !digit && index > 0) {
										inputRefs.current[index - 1]?.focus(); // backspace on empty cell moves back
									}
								}}
								onPaste={handleOTPPaste}
								required
							/>
						</div>
					))}
				</div>
				<button type="submit">Verify email address</button>
			</form>
			{otpError && <span>{otpError}</span>}
			<p>Didn't receive a code?</p>
			{resendCooldown > 0 ? (
				<span>You can request a new one in {resendCooldown}s</span>
			) : (
				<button type="button" onClick={handleOTPResend}>
					Resend code
				</button>
			)}
			<br />
			<button type="button" onClick={handleEmailChange}>
				Change email address
			</button>
		</div>
	);
}
