export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      const target = new URL(url.pathname.replace(/^\/api/, "") + url.search, env.BACKEND_URL);

      const headers = new Headers(request.headers);
      headers.set("X-Real-IP", request.headers.get("CF-Connecting-IP") ?? "");
      headers.set("X-Proxy-Secret", env.PROXY_SECRET ?? "");

      const upstream = await fetch(
        new Request(target, {
          method: request.method,
          headers,
          body: request.body,
          redirect: "manual",
        }),
      );

      // Return the backend's response as-is (status, headers, cookies, body)
      return new Response(upstream.body, upstream);
    } catch (err) {
      console.error("Proxy error:", err);
      return Response.json({ proxyError: String(err) }, { status: 502 });
    }
  },
};
