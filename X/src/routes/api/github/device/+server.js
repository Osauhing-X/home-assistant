import { error, json } from '@sveltejs/kit';
import { audit, getConfig, saveConfig } from '$lib/server/store.js';

async function githubResponse(response, fallback) {
  const result = await response.json().catch(() => ({}));
  if (!response.ok || result.error) {
    const detail = result.error_description || result.message || result.error || fallback;
    error(response.ok ? 400 : response.status, detail);
  }
  return result;
}

export async function POST({ request, fetch }) {
  const input = await request.json();
  const config = await getConfig();
  const clientId = config.githubOAuthClientId;
  if (!clientId) error(400, 'Configure the GitHub OAuth App client ID first.');

  if (input.action === 'start') {
    const response = await fetch('https://github.com/login/device/code', {
      method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ client_id: clientId, scope: 'repo read:org' })
    });
    return json(await githubResponse(response, 'GitHub Device Login could not be started.'));
  }

  if (input.action === 'poll' && input.deviceCode) {
    const response = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ client_id: clientId, device_code: input.deviceCode, grant_type: 'urn:ietf:params:oauth:grant-type:device_code' })
    });
    const result = await response.json();
    if (!response.ok) {
      const detail = result.error_description || result.message || result.error || 'GitHub Device Login polling failed.';
      error(response.status, detail);
    }
    if (!result.access_token) return json(result);
    const profileResponse = await fetch('https://api.github.com/user', { headers: { Authorization: `Bearer ${result.access_token}`, Accept: 'application/vnd.github+json' } });
    if (!profileResponse.ok) error(profileResponse.status, 'Could not read the GitHub profile.');
    const profile = await profileResponse.json();
    const account = { id: `github-${profile.id}`, login: profile.login, avatarUrl: profile.avatar_url, type: 'oauth', token: result.access_token };
    config.githubAccounts = [...(config.githubAccounts || []).filter((item) => item.id !== account.id), account];
    await saveConfig(config);
    await audit('portal', profile.login, 'github_oauth_connected');
    return json({ connected: true, account: { ...account, token: undefined } });
  }
  error(400, 'Invalid Device Login action.');
}
