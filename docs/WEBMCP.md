# QuaNThoR WebMCP source contract

`GET /webmcp/manifest` exposes exactly twelve descriptors before login: ten
QuaNThoR tools plus `securedme_companion_context` and
`securedme_qbit_plan_handoff`.  Discovery is public; execution is not.

The Flask app denies invocation unless a trusted Gateway session authorizer is
installed in `app.config["SECUREDME_WEBMCP_AUTHORIZER"]`. Formal verification is
classified `READ` because it does not create durable state. The generic `/route` endpoint
is deliberately absent from the manifest because it can choose and execute a
branch implicitly.

The source-to-tool mapping is embedded in each descriptor's `handler` field.
Unknown or unavailable capabilities return an explicit error; no shell, browser,
provider secret, `.env`, provisioning, or autonomous proof authority is exposed.
The drafting wrapper uses QuaNThoR's deterministic school heuristic; it never
selects any legacy local or cloud model route.

Theme provenance is the product-specific Stitch handoff at
`securedme-site/assets/landing/secureme.ca-product/education/QuaNThoR/desing/stitch_quanthor_landing_page_design_system/stitch_quanthor_landing_page_design_system/desing.md`
with `sourceStatus: verified-product-stitch`.
The page consumes its navy, electric-blue, violet, gold, paper-white, and focus
tokens. System fonts, visible focus, and text labels are the accessible fallback.
