import { error, json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

/** @type {import('./$types').RequestHandler} */
export async function POST({ request }) {

  const { what, id } = await request.json();

  let res = await fetch(`https://api.themoviedb.org/3/${what}/${id}?api_key=${env.THEMOVIEDB_API}`);
  if (res.ok) {
    res = await res.json()
    res.media_type = what
    return json( res ) }
    
}