import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { OTPLoginForm, OTPVerificationForm } from "@/components";
import { useAuth } from "@/context/AuthContext";

export default function Login() {
	const navigate = useNavigate();
	const { isAuthenticated } = useAuth();

	useEffect(() => {
		if (isAuthenticated) {
			navigate("/connect");
		}
	}, [isAuthenticated, navigate]);

	if (isAuthenticated) return null;

	const [email, setEmail] = useState<string>("");
	const [emailSent, setEmailSent] = useState<boolean>(false);

	return (
		<div>
			{!emailSent ? (
				<OTPLoginForm
					initialEmail={email}
					onEmailSent={(sentTo) => {
						setEmail(sentTo);
						setEmailSent(true);
					}}
				/>
			) : (
				<OTPVerificationForm
					targetEmail={email}
					onBackToLogin={() => setEmailSent(false)}
				/>
			)}
		</div>
	);
}
