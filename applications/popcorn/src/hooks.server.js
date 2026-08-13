import { createHash, timingSafeEqual } from 'node:crypto';
import { redirect } from '@sveltejs/kit';
import { startReminderWorker } from '$lib/server/reminder-worker.js';

startReminderWorker();

export const AUTH_COOKIE = 'popcorn_auth';
export const authToken = () => createHash('sha256').update(`popcorn:${process.env.PASSWORD || ''}`).digest('hex');

export async function handle({ event, resolve }) {
  const password = process.env.PASSWORD || '';
  if (!password || event.url.pathname === '/login' || event.url.pathname.startsWith('/login/') || event.url.pathname.startsWith('/_app/')) return resolve(event);

  const supplied = event.cookies.get(AUTH_COOKIE) || '';
  const expected = authToken();
  const valid = supplied.length === expected.length && timingSafeEqual(Buffer.from(supplied), Buffer.from(expected));
  if (!valid) redirect(303, `/login?next=${encodeURIComponent(event.url.pathname + event.url.search)}`);
  return resolve(event);
}
