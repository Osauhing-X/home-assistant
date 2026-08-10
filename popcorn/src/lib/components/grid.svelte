<script>export let column=150;export let padding='1em';</script>
<section class="movie-grid" style={`--card-min:${column}px;--grid-pad:${padding}`} data-sveltekit-preload-data="tap"><slot /></section>
<style>.movie-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(var(--card-min),100%),1fr));gap:14px;padding:var(--grid-pad);min-width:0;width:100%;align-items:start}.movie-grid:global(>*){min-width:0;width:100%}@media(max-width:600px){.movie-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;padding:12px}}</style>
