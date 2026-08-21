import { error, json } from '@sveltejs/kit';
import { getConfig, tokenFor } from '$lib/server/store.js';

export async function GET({ fetch, url }) {
  const config = await getConfig();
  const accountId = url.searchParams.get('account') || '';
  const token = tokenFor(config, accountId);
  if (!token) error(400, 'Connect a GitHub account first.');
  const headers = { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };
  const allRepositories = [];
  for (let page = 1; page <= 20; page += 1) {
    const response = await fetch(`https://api.github.com/user/repos?per_page=100&page=${page}&sort=updated&visibility=all`, { headers });
    if (!response.ok) {
      const result = await response.json().catch(() => ({}));
      error(response.status, result.message || `GitHub returned ${response.status}.`);
    }
    const repositories = await response.json();
    allRepositories.push(...repositories);
    if (repositories.length < 100) break;
  }
  const repos = [...new Map(allRepositories.map((repo) => [repo.id, repo])).values()].map((repo) => ({
    fullName: repo.full_name,
    private: repo.private,
    description: repo.description || '',
    defaultBranch: repo.default_branch,
    updatedAt: repo.updated_at
  }));
  return json(repos);
}
