# Extaas Connect account linking

Implemented source and synthetic acceptance: 2026-10-27. This is not an
announcement that the standalone addon or production paid access is live.

## Owner flow

Account linking is opt-in with the server setting `RTSP_CONNECT_ENABLED=true`.
The camera page then offers **Extaas Connect**, opening `/connect` inside the
authenticated relay UI. Start a connection, open Iseteenindus, compare the code
and approve it while signed in to the intended account. The relay checks every
five seconds. It displays the connected email and a management link afterwards.
No licence key, device secret or connection token is copied by the user.

The issuer origin is fixed to `https://iseteenindus.oux.ee`; redirects are refused.
Only the `rtsp-to-onvif` service is accepted. A successful account link is not a
paid entitlement and does not activate a subscription or unlock production access.
Paid access enforcement and the separate addon package remain unfinished.

## Private persistent state

`connect.json` and `.connect-key` live in the existing RTSP private data directory,
normally `/data/application-data/rtsp-to-onvif`. The first connection generates a
stable local installation label. Retain it when moving this installation; a
different label may create a separate registration at the account service.

The state is encrypted with AES-256-GCM using a local random 32-byte key. Files
use mode 0600 and the directory 0700 on Unix; Windows ACLs are not managed here.
Back up both files securely. Keeping the key beside encrypted data does not
protect against a compromised host or an attacker who can read the full directory.
Missing keys, tampered state and malformed JSON fail closed instead of replacing
an existing link. Restore the original key and file from a verified backup.

The browser receives only connection status, email, installation ID, confirmation
code and approved HTTPS links. Device codes, verifier and credentials remain on
the server. Revocation in Iseteenindus is detected with **Check connection**.
It removes the local credential, while retaining the local installation label.

## Local API

`GET /api/connect` returns the safe view. `POST /api/connect` accepts only
`{"action":"begin"}`, `{"action":"poll"}` or `{"action":"refresh"}`. Both
require the relay's GUI session. Mutations also require same-origin browser
requests. Bodies are capped at 1 KiB, issuer responses at 16 KiB and outgoing
requests at ten seconds. Responses are private and uncached. These endpoints
are for this UI, not public module APIs or a replacement for issuer credentials.

## Verified scope

- Client tests cover encrypted persistence/restart, polling interval, fixed issuer,
  response service validation, revocation, corrupt state and missing keys.
- A separate synthetic test used the built Iseteenindus issuer, a fake authenticated
  customer and temporary vaults: approval, account overview and revocation passed.
  No Stripe requests or production accounts were used.
- Desktop and 390-pixel mobile UI states passed automated axe WCAG A/AA checks:
  disconnected, awaiting confirmation and connected. No horizontal overflow was
  found. This does not establish accessibility of every camera-management screen.
- Actual production HTTPS linking, paid-period enforcement, Home Assistant
  installation and real camera/NVR compatibility still require acceptance.
