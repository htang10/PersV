import type {
  GetUsersMeData,
  GetUsersMeResponse,
  PatchUsersMeData,
  PatchUsersMeResponse,
  UserProfileUpdate,
} from "@/client";
import { fetchAPI } from "./api";

export async function getUserProfile(): Promise<GetUsersMeResponse> {
  return await fetchAPI<GetUsersMeData, GetUsersMeResponse>("GET", "/users/me");
}

export async function updateUserProfile(data: UserProfileUpdate): Promise<PatchUsersMeResponse> {
  return await fetchAPI<PatchUsersMeData, PatchUsersMeResponse>("PATCH", "/users/me", {
    body: data,
  });
}
