import type {
  ClientServerConnectionConfig,
  PostConnectionCustomSqliteData,
  PostConnectionCustomSqliteResponse,
  DeleteConnectionData,
  GetConnectionStatusData,
  GetConnectionStatusResponse,
  PostConnectionCustomData,
  PostConnectionCustomResponse,
  PostConnectionDemoData,
  PostConnectionDemoResponse,
  PostConnectionQueryData,
  PostConnectionQueryResponse,
} from "@/client";
import { fetchAPI } from "./api";

export async function connectDemo(): Promise<PostConnectionDemoResponse> {
  return await fetchAPI<PostConnectionDemoData, PostConnectionDemoResponse>(
    "POST",
    "/connection/demo",
  );
}

export async function connectCustom(
  config: ClientServerConnectionConfig,
): Promise<PostConnectionCustomResponse> {
  return await fetchAPI<PostConnectionCustomData, PostConnectionCustomResponse>(
    "POST",
    "/connection/custom",
    {
      body: config,
    },
  );
}

export async function connectSQLite(file: File): Promise<PostConnectionCustomSqliteResponse> {
  return await fetchAPI<PostConnectionCustomSqliteData, PostConnectionCustomSqliteResponse>(
    "POST",
    "/connection/custom/sqlite",
    {
      body: { file },
    },
  );
}

export async function checkConnStatus(): Promise<GetConnectionStatusResponse> {
  return await fetchAPI<GetConnectionStatusData, GetConnectionStatusResponse>(
    "GET",
    "/connection/status",
  );
}

export async function disconnect(): Promise<void> {
  // API returns 204 No Content on successful disconnect
  await fetchAPI<DeleteConnectionData, void>("DELETE", "/connection");
}

export async function query(prompt: string): Promise<PostConnectionQueryResponse> {
  return await fetchAPI<PostConnectionQueryData, PostConnectionQueryResponse>(
    "POST",
    "/connection/query",
    {
      body: {
        prompt: prompt,
      },
    },
  );
}
