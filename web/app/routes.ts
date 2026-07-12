import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("/api/v1/briefs", "routes/api.v1.briefs.ts"),
] satisfies RouteConfig;
