import { error, json } from '@sveltejs/kit';
import { getConfig, tokenFor } from '$lib/server/store.js';

export async function GET({ fetch, url }) {
  const config = await getConfig();
  const accountId = url.searchParams.get('account') || '';
  const token = tokenFor(config, accountId);
  if (!token) error(400, 'Connect a GitHub account first.');
  const response = await fetch('https://api.github.com/user/repos?per_page=100&sort=updated&affiliation=owner,collaborator,organization_member', {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' }
  });
  if (!response.ok) error(response.status, `GitHub returned ${response.status}.`);
  const repos = (await response.json()).map((repo) => ({
    fullName: repo.full_name,
    private: repo.private,
    description: repo.description || '',
    defaultBranch: repo.default_branch,
    updatedAt: repo.updated_at
  }));
  return json(repos);
}
