// /@_movie/get_all/+server.js
import { error, json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export async function GET({ url, fetch }) {
	// No Params -> Create own
	if (!url.search) {
		url = new URL(
			url.origin +
				url.pathname +
				'?api=dHJlbmRpbmcvYWxsL2RheQ==&include_adult=false&sort_by=popularity.desc&language=en&fetch=5&page=1'
		);
	}

	// Validate number
	function number(value) {
		let nr = parseInt(value);
		if (typeof nr != 'number') return 1;
		else if (nr <= 0) return 1;
		else return nr;
	}

	// Params
	let params = new URLSearchParams(url.searchParams);
	let request_type = params.get('api') ?? "dHJlbmRpbmcvYWxsL2RheQ==";
	let current_page = number(params.get('page') ?? 1);
	let fetch_count = number(params.get('fetch') ?? 5);

	// API missing
	if (!request_type) throw error(400, 'Missing API hash');

	// Remove unused
	params.delete('api');
	params.delete('page');
	params.delete('show');

	let apiKey = env.THEMOVIEDB_API;
	let decode = atob(request_type);
	let calculated = fetch_count * (current_page - 1) + 1;
	let all = [],
		pages = {};

	// Extract media type from URL
	let what = ['tv', 'movie', 'person'].find((valid) => decode.includes(valid));

	for (let i = 0; i < fetch_count; i++) {
		// Input
		let themoviedb = await fetch(
			`https://api.themoviedb.org/3/${decode}?${params}&page=${calculated}&api_key=${apiKey}`
		);

		let res = await themoviedb.json();

		// First fetch
		if (i == 0)
			pages = {
				current: current_page,
				total: res.total_pages,
				results: res.total_results
			};

		// No content
		if (!res?.results || res.results.length === 0) break;

		// Remove adult / undesired
		res.results = res.results.filter((item) => {
			let title = item?.title || item?.name;
			let genres = item.genre_ids ?? [];
			let vote = item.vote_count ?? 0;

			if (
				genres.some((id) => [10749, 18].includes(id)) ||
				['sex', 'porn', 'love', 'gay', 'lesbian'].some((word) =>
					title.toLowerCase().includes(word)
				)
			) {
				if (vote > 3000) return true;
				if (genres.some((id) => [10751].includes(id))) return true;
				return false;
			}
			return true;
		});

		// Add media_type
		if (what) {
			res.results.forEach((item) => {
				item.media_type = what;
			});
		}

		all = [...all, ...res.results];
		calculated++;
	}

	// Compose new URL
	let back = new URLSearchParams(url.searchParams);
	back.delete('page');
	pages.url = `?${back.toString()}`;
	pages.fetch = fetch_count;

	// Remove duplicates by ID
	let data = Object.values(
		all.reduce((acc, item) => {
			acc[item.id] ??= item;
			return acc;
		}, {})
	);

	if (data == '') data = null;

	return json({ data, pages });
}
