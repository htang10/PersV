import { useState } from "react";
import { login, sendOTP } from "@/services/auth";

export default function Login() {
	const [email, setEmail] = useState("");
	const [emailSent, setEmailSent] = useState(false);
	const [resendCooldown, setResendCooldown] = useState(0);
	const [otp, setOTP] = useState<string[]>(Array(6).fill(""));
	let cooldownID: NodeJS.Timeout;

	function startResendCooldown() {
		setResendCooldown(30);
		cooldownID = setInterval(() => {
			setResendCooldown((cooldown) => {
				if (cooldown <= 1) {
					clearInterval(cooldownID);
					return 0;
				}
				return cooldown - 1;
			});
		}, 1000);
	}

	function updateOTPDigit(inputDigit: string, position: number) {
		if (!/^\d?$/.test(inputDigit)) return; // Reject non-digit characters

		setOTP((otp) =>
			otp.map((currentDigit, index) =>
				position === index ? inputDigit : currentDigit,
			),
		);
	}

	function clearOTPInputs() {
		setOTP(Array(6).fill(""));
	}

	return (
		<div>
			{!emailSent ? (
				<form
					onSubmit={async (e) => {
						e.preventDefault();
						try {
							const response = await sendOTP(e.target.email.value);
							// Email address is normalized upon successful request, hence we only update the final state of email
							setEmail(response.data.to);
							setEmailSent(true);
							startResendCooldown();
						} catch (error) {
							return;
						}
					}}
					method="post"
				>
					<label htmlFor="email">Email: </label>
					<br />
					<input
						type="email"
						id="email"
						placeholder="Your email address"
						defaultValue={email}
						required
					/>
					<br />
					<button type="submit">Continue with email</button>
				</form>
			) : (
				<>
					<span>Enter the code sent to {email}</span>
					<form
						onSubmit={async (e) => {
							e.preventDefault();
							const code = otp.join("");
							try {
								const response = await login(email, code);
								console.log(response);
							} catch (error) {
								return;
							}
						}}
						method="post"
					>
						<div>
							{otp.map((digit, index) => (
								<div key={index}>
									<input
										type="text"
										inputMode="numeric"
										pattern="[0-9]"
										maxLength={1}
										value={digit}
										onChange={(e) => updateOTPDigit(e.target.value, index)}
										required
									/>
								</div>
							))}
						</div>
						<button type="submit">Verify email address</button>
					</form>
					<form
						onSubmit={async (e) => {
							e.preventDefault();
							await sendOTP(email);
							startResendCooldown();
						}}
						method="post"
					>
						<span>Didn't receive a code?</span>
						<br />
						{resendCooldown > 0 ? (
							<span>You can request a new one in {resendCooldown}s</span>
						) : (
							<button type="submit">Resend code</button>
						)}
					</form>
					<button
						type="button"
						onClick={() => {
							clearInterval(cooldownID);
							setEmailSent(false);
							setResendCooldown(0);
							clearOTPInputs();
						}}
					>
						Change email address
					</button>
				</>
			)}
		</div>
	);
}
