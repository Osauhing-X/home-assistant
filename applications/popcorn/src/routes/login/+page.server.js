import { fail, redirect } from '@sveltejs/kit';
import { AUTH_COOKIE, authToken } from '../../hooks.server.js';

export const actions = {
  default: async ({ request, cookies, url }) => {
    const form = await request.formData();
    const password = String(form.get('password') || '');
    if (!process.env.PASSWORD || password !== process.env.PASSWORD) return fail(400, { invalid: true });
    cookies.set(AUTH_COOKIE, authToken(), {
      path: '/', httpOnly: true, sameSite: 'lax', secure: url.protocol === 'https:', maxAge: 60 * 60 * 24 * 7
    });
    const next = url.searchParams.get('next');
    redirect(303, next?.startsWith('/') && !next.startsWith('//') ? next : '/');
  }
};
