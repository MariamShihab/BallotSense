import type { ActionFunctionArgs } from "react-router";

import { GoogleAuth } from "google-auth-library";

const apiBaseUrl = process.env.BALLOTSENSE_API_URL;

async function buildHeaders(targetUrl: string) {
  const headers = new Headers({ "Content-Type": "application/json" });

  if (!targetUrl.startsWith("http://127.0.0.1") && !targetUrl.startsWith("http://localhost")) {
    const auth = new GoogleAuth();
    const client = await auth.getIdTokenClient(new URL(targetUrl).origin);
    const authHeaders = new Headers(await client.getRequestHeaders(targetUrl));
    for (const [key, value] of authHeaders.entries()) {
      headers.set(key, value);
    }
  }

  return headers;
}

export async function action({ request }: ActionFunctionArgs) {
  if (!apiBaseUrl) {
    return Response.json(
      { detail: "BallotSense API is not configured." },
      { status: 503 },
    );
  }

  const body = await request.text();
  const targetUrl = new URL("/v1/briefs", apiBaseUrl).toString();
  const upstream = await fetch(targetUrl, {
    method: "POST",
    headers: await buildHeaders(targetUrl),
    body,
  });

  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: {
      "Content-Type": upstream.headers.get("Content-Type") ?? "application/json",
      "Cache-Control": "no-store",
    },
  });
}
