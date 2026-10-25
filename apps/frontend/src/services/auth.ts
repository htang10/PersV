import type {
  GetAuthSessionData,
  GetAuthSessionResponse,
  PostAuthLoginData,
  PostAuthLoginResponse,
  PostAuthLogoutData,
  PostAuthOtpData,
  PostAuthOtpResponse,
} from "@/client";
import { fetchAPI } from "./api";

export async function sendOTP(email: string): Promise<PostAuthOtpResponse> {
  return await fetchAPI<PostAuthOtpData, PostAuthOtpResponse>("POST", "/auth/otp", {
    body: {
      email: email,
    },
  });
}

export async function login(email: string, otp: string): Promise<PostAuthLoginResponse> {
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

export async function logout(): Promise<void> {
  return await fetchAPI<PostAuthLogoutData, void>("POST", "/auth/logout");
}
