import type { MailingPurpose } from "@/client";

export type OTPRequest = {
  email: string;
  purpose: MailingPurpose;
};

export type LoginRequest = {
  email: string;
  otp: string;
};

export type UpdateEmailRequest = {
  newEmail: string;
  newEmailCode: string;
  currentEmailCode: string;
};
