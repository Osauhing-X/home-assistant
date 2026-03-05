import { base } from '$app/paths';
export async function load({fetch, url}) {
  const res = await fetch(base + `/@_movie/json` + url.search)
  let data = await res.json()

  return { ...data }
}