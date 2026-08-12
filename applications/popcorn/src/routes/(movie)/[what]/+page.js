import { redirect } from '@sveltejs/kit';
import { base } from '$app/paths';

/** @type {import('./$types').PageLoad} */
export function load({ params }) {
  if (params.what !== 'favorite') {
    throw redirect(302, `${base}/?view=saved`);
  }
}
