import { redirect } from '@sveltejs/kit';
import { AUTH_COOKIE, authToken } from '../../../hooks.server.js';

export async function POST({ request, cookies, url }) {
  const form = await request.formData();
  const password = String(form.get('password') || '');
  const requestedNext = String(form.get('next') || '/');
  const next = requestedNext.startsWith('/') && !requestedNext.startsWith('//') ? requestedNext : '/';
  if (!process.env.PASSWORD || password !== process.env.PASSWORD) redirect(303, `/login?invalid=1&next=${encodeURIComponent(next)}`);
  cookies.set(AUTH_COOKIE, authToken(), {
    path: '/', httpOnly: true, sameSite: 'lax', secure: url.protocol === 'https:', maxAge: 60 * 60 * 24 * 7
  });
  redirect(303, next);
}
