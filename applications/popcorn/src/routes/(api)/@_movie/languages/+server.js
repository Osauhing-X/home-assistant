import { error, json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export async function GET() {
  return new Response('Not found', { status: 404 });
}

/** @type {import('./$types').RequestHandler} */
export async function POST({ request }) {
  const { value, lang } = await request.json();

  let res = await fetch('https://api.themoviedb.org/3/configuration/languages?api_key='+env.THEMOVIEDB_API);
      res = await res.json()
  return json( res.map(lang => lang.iso_639_1) )
}
