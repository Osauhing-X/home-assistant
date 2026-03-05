import { error } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export async function load({ params, url }) {
  let language = url.searchParams.get('language') || 'en';
  const api = '?api_key=' + env.THEMOVIEDB_API;
  let data = null;

  // Põhiandmete laadimine
  if (['tv', 'movie', 'person'].includes(params.what)) {
   // Has translation
    let translation = (await (await fetch(`https://api.themoviedb.org/3/${params.what}/${params.where}/translations${api}`))
      .json()).translations
      .map(lang => lang.iso_639_1)
      .includes(language)
    language = translation ? language : 'en'


   // Main content
    const baseUrl = `https://api.themoviedb.org/3/${params.what}/${params.where}${api}&language=${language}`;
    data = await (await fetch(baseUrl)).json();


   // Override data (empty)
    if (Object.values(data).some(value => value === "") && language !== 'en') {
      data.override = 50;
      const fallback = await (await fetch(`https://api.themoviedb.org/3/${params.what}/${params.where}${api}`)).json();

      for (const key in fallback) {
        if (data[key] === "" || data[key] === undefined) {
          data[key] = fallback[key]; } } }

    if(!translation) data.override = 100; }

  else throw error(404, 'Invalid "what" parameter');


  // Lülitu toimingute järgi
  switch (['tv', 'movie'].includes(params.what) ? 'movie-tv' : params.what) {
    case 'movie-tv': {
      const res = await Promise.all([
        fetch(`https://api.themoviedb.org/3/${params.what}/${params.where}/videos${api}&language=${language}`),
        fetch(`https://api.themoviedb.org/3/${params.what}/${params.where}/recommendations${api}&language=${language}&page=1`),
        fetch(`https://api.themoviedb.org/3/${params.what}/${params.where}/watch/providers${api}&language=${language}`),
        fetch(`https://api.themoviedb.org/3/${params.what}/${params.where}/credits${api}`)
      ]);

      if (!res.every(response => response.ok)) throw error(404, 'Failed to fetch related movie data');

      let [videos, similar, providers, credits] = await Promise.all(res.map(r => r.json()));

      if(credits?.cast.length > 0) data.persons = credits.cast
        .map(({ id, name, character, profile_path }) => ({
          id, name, character, media_type: 'person', profile_path: profile_path ? profile_path : null }))

      // Lisa collection
      if (data?.belongs_to_collection?.id) {
        const collectionRes = await fetch(`https://api.themoviedb.org/3/collection/${data.belongs_to_collection.id}${api}&language=${language}`);
        data.collection = await collectionRes.json();
        delete data.belongs_to_collection;
      }

      // Formateeri runtime
      if (data.runtime) {
        data.runtime = `${Math.floor(data.runtime / 60)}h ${data.runtime % 60}min`;
      }

      // Väljalaske kuupäev -> päevade arv
      if (data.release_date) {
        data.release = {
          date: data.release_date,
          days: Math.floor((new Date() - new Date(data.release_date)) / (1000 * 60 * 60 * 24))
        };
        delete data.release_date;
      }

      // Leia YouTube trailer
      if (videos.results?.length > 0) {
        const trailerKey =
          videos.results.find(v => v.name.toLowerCase().includes("official") && v.name.toLowerCase().includes("trailer") && v.site === "YouTube")?.key ||
          videos.results.find(v => v.name.toLowerCase().includes("trailer") && v.site === "YouTube")?.key ||
          videos.results[0]?.key;

        if (trailerKey) {
          data.trailer = `https://youtube.com/embed/${trailerKey}`;
        }
      }

      // Watch providers
      const result = [];
      if (providers?.results) {
        for (const [country, providerData] of Object.entries(providers.results)) {
          for (const [type, entries] of Object.entries(providerData)) {
            if (type === "link") continue;
            entries.forEach(provider => {
              const existing = result.find(p => p.name === provider.provider_name);
              if (!existing) {
                result.push({ name: provider.provider_name, lang: [country] });
              } else if (!existing.lang.includes(country)) {
                existing.lang.push(country);
              }
            });
          }
        }
        data.providers = {
          languages: Object.keys(providers.results),
          providers: result
        };
      }

      // Lisa soovitatud filmid
      data.similar = similar.results;
      break;
    }

    case 'person': {
      const res = await Promise.all([
        fetch(`https://api.themoviedb.org/3/person/${params.where}/movie_credits${api}&language=${language}`),
        fetch(`https://api.themoviedb.org/3/person/${params.where}/tv_credits${api}&language=${language}`)
      ]);

      if(!res.every(response => response.ok)) throw error(404, 'Failed to fetch person credits');

      const [movie, tv] = await Promise.all(res.map(r => r.json()));

      // Lisa media_type
      movie.cast.forEach(item => item.media_type = 'movie');
      tv.cast.forEach(item => item.media_type = 'tv');

      data.movie = movie;
      data.tv = tv;
      break;
    }
  }



  return {
    ...data,
  };
}
