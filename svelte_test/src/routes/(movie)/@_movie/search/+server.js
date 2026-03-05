import { error, json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export async function GET() {
  return new Response('Not found', { status: 404 });
}

/** @type {import('./$types').RequestHandler} */
export async function POST({ request }) {

  const { what, value, lang } = await request.json();

  switch (what){
    case 'languages': { 
      let res = await fetch('https://api.themoviedb.org/3/configuration/languages?api_key='+env.THEMOVIEDB_API);
          res = await res.json()
      return json( res.map(lang => lang.iso_639_1) )
    }


    case 'genres': {
      let backup = await fetch('https://api.themoviedb.org/3/genre/'+value+'/list?language=en&api_key='+env.THEMOVIEDB_API);
          backup = await backup.json()

      let res = await fetch('https://api.themoviedb.org/3/genre/'+value+'/list?api_key='+env.THEMOVIEDB_API+'&language='+lang);
          res = await res.json()

      const merged = res.genres.map(genre => ({ 
        value: genre.id, 
        title: genre.name || backup.genres.find(backup => backup.id === genre.id)?.name 
      }));

      return json( merged )
    }

    default: throw error(400, 'Unknown action');
  }

}
