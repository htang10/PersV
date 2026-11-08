import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { OTPLoginForm, OTPVerificationForm } from "@/components";
import { useAuth } from "@/context/AuthContext";

export function meta() {
  return [{ title: "Log in - PersV" }];
}

export default function Login() {
  const navigate = useNavigate();

  const { isAuthenticated } = useAuth();
  const [email, setEmail] = useState<string>("");
  const [emailSent, setEmailSent] = useState<boolean>(false);

  // Don't render login page if user is already logged in. Redirect to connect page
  useEffect(() => {
    if (isAuthenticated) {
      void navigate("/connect");
    }
  }, [isAuthenticated]);

  if (isAuthenticated) return null;

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
        <OTPVerificationForm targetEmail={email} onBackToLogin={() => setEmailSent(false)} />
      )}
    </div>
  );
}
