import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("/api/v1/briefs", "routes/api.v1.briefs.ts"),
  route("/api/v1/corrections", "routes/api.v1.corrections.ts"),
  route("/api/v1/ballots/resolve-address", "routes/api.v1.ballots.resolve-address.ts"),
] satisfies RouteConfig;
