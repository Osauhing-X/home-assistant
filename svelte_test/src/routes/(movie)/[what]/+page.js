import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageLoad} */
export function load({ params }) {
  if (params.what !== 'favorite') {
    throw redirect(302, '/discover/favorite');
  }
}
