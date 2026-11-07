import type {
  GetAuthSessionData,
  GetAuthSessionResponse,
  PostAuthLoginData,
  PostAuthLoginResponse,
  PostAuthLogoutData,
  PostAuthLogoutResponse,
  PostAuthOtpData,
  PostAuthOtpResponse,
  PostAuthLogoutAllData,
  PostAuthLogoutAllResponse,
  PutAuthEmailData,
  PutAuthEmailResponse,
} from "@/client";
import type { OTPRequest, LoginRequest, UpdateEmailRequest } from "@/types/auth";
import { fetchAPI } from "./api";

export async function sendOTP({ email, purpose }: OTPRequest): Promise<PostAuthOtpResponse> {
  return await fetchAPI<PostAuthOtpData, PostAuthOtpResponse>("POST", "/auth/otp", {
    body: {
      email: email,
      purpose: purpose,
    },
  });
}

export async function login({ email, otp }: LoginRequest): Promise<PostAuthLoginResponse> {
  return await fetchAPI<PostAuthLoginData, PostAuthLoginResponse>("POST", "/auth/login", {
    body: {
      email: email,
      code: otp,
    },
  });
}

export async function validateCurrentSession(): Promise<GetAuthSessionResponse> {
  return await fetchAPI<GetAuthSessionData, GetAuthSessionResponse>("GET", "/auth/session");
}

export async function logout(): Promise<PostAuthLogoutResponse> {
  return await fetchAPI<PostAuthLogoutData, PostAuthLogoutResponse>("POST", "/auth/logout");
}

export async function logoutAllSessions(): Promise<PostAuthLogoutAllResponse> {
  return await fetchAPI<PostAuthLogoutAllData, PostAuthLogoutAllResponse>(
    "POST",
    "/auth/logout-all",
  );
}

export async function updateEmail({
  newEmail,
  newEmailCode,
  currentEmailCode,
}: UpdateEmailRequest): Promise<PutAuthEmailResponse> {
  return await fetchAPI<PutAuthEmailData, PutAuthEmailResponse>("PUT", "/auth/email", {
    body: {
      new_email: newEmail,
      new_email_code: newEmailCode,
      current_email_code: currentEmailCode,
    },
  });
}
