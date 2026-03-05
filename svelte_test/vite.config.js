import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
    	host: true,   // kõik IP-d, et konteineris kättesaadav
    	port: 8080    // Home Assistant ingress port
  	}
});
