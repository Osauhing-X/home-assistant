# ONVIF authentication behavior

Source implementation and synthetic HTTP acceptance: 2026-10-27. This is not
ONVIF certification or proof of compatibility with every recorder.

Configure a nonempty ONVIF username/password for each camera. These credentials
are separate from the management GUI password. Blank legacy camera credentials
are refused by authentication and must be corrected before migration.

The common WS-Security UsernameToken form is accepted inside the SOAP Header.
Username/password fields outside a single header token, duplicate credential
fields, unknown declared password types and XML entity declarations are refused.
This implementation handles the supported token shape; it is not a general XML
schema validator or a complete WS-Security implementation.

## PasswordDigest

The digest uses the OASIS UsernameToken SHA-1 formula over decoded nonce bytes,
the exact Created text and the configured password. Declared types must use the
standard OASIS URI. The nonce must be canonical Base64. Both Nonce and Created
are required for a digest; incomplete pairs fail authentication. A missing type
is retained for clients that already use the nonce/digest form without a Type.

Created must include an explicit timezone. A request may be at most five minutes
old or one minute ahead of the relay clock. Recorders should synchronize their
clocks and may use the existing unauthenticated GetSystemDateAndTime response.
Each authenticated request needs a fresh nonce, including calls to other camera
endpoints that share the same credentials.

Successful nonce use is cached for the token's remaining validity period. The
cache is scoped by credentials rather than just camera ID, so a captured token
cannot be reused on another camera with the same username/password. Invalid
signatures never consume a nonce. The bounded in-memory cache holds 16,384 entries;
when full, it refuses additional digest requests until entries expire rather than
evicting still-valid replay protection. The cache does not survive process restart.

Internal generic-to-camera routing checks a token once for the actual request;
route selection alone does not consume it. The acceptance test covers both generic
and camera-specific Device and Media endpoints, with fresh, replayed and stale
requests. The nonce mechanism does not sign the SOAP body or secure the transport.

## PasswordText compatibility

Nonempty PasswordText remains supported for existing clients, with no Nonce or
Created. Its password is transmitted in the SOAP message; it does not gain nonce
replay protection. Use the appropriate trusted network/transport boundary. Do not
describe this compatibility path as encrypted, one-time or replay-proof.

## Request limits

SOAP POST bodies are read with a 64 KiB application limit before route logging or
authentication. Oversized/unreadable bodies receive 413 and close the connection
after the response. The request stream is not cancelled before responding,
because adapter-node would destroy the connection before sending the HTTP status.

The profile reference is the [OASIS UsernameToken Profile 1.1](https://docs.oasis-open.org/wss/v1.1/wss-v1.1-spec-os-UsernameTokenProfile.pdf).
Actual NVR interoperability, clock behavior and restart scenarios remain part of
hardware acceptance before deployment.
