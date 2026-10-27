# Management login

Implemented and synthetically checked on 2026-10-27. The management password is
local to this relay installation and is separate from camera ONVIF credentials
and the optional Extaas Connect account connection.

The `/login` form uses a server action, with ordinary HTML form fallback and
progressive enhancement. Successful login issues a signed, random HttpOnly,
SameSite=Lax session; HTTPS adds Secure. The server enforces its seven-day expiry.
Changing the configured password invalidates existing signatures. Passwords are
not returned in action data, validation errors, URLs or logs.

## Failed attempts

Eight incorrect passwords from one resolved client address trigger a 60-second
block. The server also caps failures at 100 per minute across addresses. At most
1,024 client records are retained, expiring after 15 minutes; saturation refuses
new clients rather than evicting active restrictions. The table and global
counter are process-local and reset when the process restarts. They are not a
distributed limiter for multiple replicas.

The application uses `getClientAddress()` from the server adapter, not an
independently trusted browser X-Forwarded-For field. Operators behind a proxy
must configure the adapter's trusted address-header boundary correctly; otherwise
clients may share a proxy address. Existing authenticated sessions remain usable
during a block. A correct password does not bypass a currently active block.

Blocked native/enhanced form submissions receive HTTP 429, Retry-After and an
accessible in-page message. The compatibility `/login/session` endpoint shares
the same limiter, while retaining its redirect to the login page. It cannot be
used to bypass an active block.

Both URL-encoded and multipart forms are supported, with a 16 KiB body limit.
Malformed/oversized forms receive validation failure without returning their
contents. The return path remains same-origin; double slashes, backslashes and
control characters cannot redirect the user to another site.

## Verified scope

- Unit checks cover per-address recovery, the global cap, bounded client records,
  form encodings and absence of credentials from failure results.
- Built HTTP checks cover successful login, native failed/blocked submissions,
  Retry-After, compatibility-path enforcement, oversized forms and continued
  access through an already established session.
- Real browser checks cover enhanced submission and the normal/error/limited
  desktop/mobile view states. Automated axe WCAG A/AA checks found no violations
  or unresolved checks in the final tested states; no horizontal overflow occurred.
- Production proxy deployments, all camera UI screens and actual Home Assistant
  login acceptance are not established by those synthetic checks.
