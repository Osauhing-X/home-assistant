# UniFi Booking

Local-first Home Assistant add-on for accommodation and facility operations. It combines room allocation, temporary access, guest credentials, turnover workflows, staff tasks and an immutable operational audit trail.

## Current implementation

- Responsive ingress-ready operations dashboard and interactive floor plan.
- Distinct ready, occupied, work-in-progress, exclusive, staff and utility spaces.
- Guarded room lifecycle transitions and turnover progress.
- Multiple rooms/doors and multiple credential types per guest: QR, PIN, licence plate and card.
- Adapter boundaries for Home Assistant, UniFi Access and Supabase.
- Multi-property Supabase schema with RLS and role-based memberships.
- Audit entries for operator state changes and task completion.
- Zero-dependency demo runtime and domain tests.

## Run locally

```sh
npm start
```

Open `http://localhost:8099`. Run `npm test` before release.

## Home Assistant installation

Place this folder in `/addons/unifi_booking`, reload the Add-on Store, install **UniFi Booking**, enable ingress and start it. Configure controller URLs and public Supabase credentials in add-on options. Secrets (UniFi API key, Resend API key, server-side Supabase secret) must be stored using the Home Assistant add-on secret mechanism or server-only environment variables; never send them to the browser.

## Production integration checklist

1. Apply `supabase/schema.sql` to the customer's Supabase project, review grants/Data API exposure, then run database advisors.
2. Replace the demo store with the Supabase adapter and authenticate every request with the user's Supabase access token.
3. Validate the UniFi Access controller version and its official developer endpoints. Credential creation/revocation is intentionally isolated in `src/adapters.js` because paths and supported credential types vary.
4. Map room door IDs to UniFi Access and light/climate entities to Home Assistant.
5. Configure Resend server-side and verify the sending domain. Send only the credential choices selected on the booking.
6. Add a remote check-in URL through a deliberately configured HTTPS endpoint (Home Assistant Cloud, VPN or reverse proxy); do not expose an unauthenticated local add-on port.

## Clarifications added to the original concept

- A room may be linked to several doors/cards; a guest may have several licence plates.
- Staff and utility rooms do not enter the guest allocation pool.
- Exclusive rooms are visible but cannot be auto-allocated.
- A forced `ready` action must capture a reason and choose whether unfinished tasks are skipped or carried to the next turnover.
- Access validity follows the booking window with a configurable arrival/departure buffer and is revoked idempotently on checkout.
- UniFi/HA calls belong in retryable workflow steps. A failed physical-access call must never be represented as a successful booking transition.
- Licence verification should use a signed offline payload containing installation ID, application ID and expiry. Customer email belongs in the vendor-side entitlement record, not in the offline licence payload.

## Not yet production-complete

Controller-tested UniFi Access provisioning, Protect events, kiosk camera scanning, Resend templates, payment/licensing backend and persistent workflow workers require real customer credentials/hardware and integration tests. The included demo is a functional product foundation, not a claim that those external systems have been certified.
