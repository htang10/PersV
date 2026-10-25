import { useState } from "react";
import { errorMessage } from "@/errors/error-message";
import { sendOTP } from "@/services/auth";

interface OTPLoginProps {
  initialEmail?: string;
  onEmailSent: (email: string) => void;
}

export function OTPLoginForm({ initialEmail = "", onEmailSent }: OTPLoginProps) {
  const [emailInput, setEmailInput] = useState(initialEmail);
  const [emailError, setEmailError] = useState<string | null>(null);

  const handleOTPEmail = async (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const response = await sendOTP(event.target.email.value);
      // Email address is normalized upon successful request, hence we only update the final state of email
      onEmailSent(response.to);
    } catch (error) {
      setEmailError(errorMessage(error));
    }
  };

  return (
    <>
      <form onSubmit={handleOTPEmail}>
        <label htmlFor="email">Email: </label>
        <br />
        <input
          type="email"
          id="email"
          placeholder="Your email address"
          value={emailInput}
          onChange={(event) => setEmailInput(event.target.value)}
          required
        />
        <br />
        <button type="submit">Continue with email</button>
      </form>

      {emailError && <span>{emailError}</span>}
    </>
  );
}
