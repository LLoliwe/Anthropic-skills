import { defineConfig } from 'void/config';

// Verified alternative to billed shared Cloudflare platform. No Cloudflare bindings.
export default defineConfig({
  target: 'node',
  routing: {
    headers: {
      '/*': [
        'X-Content-Type-Options: nosniff',
        'X-Frame-Options: DENY',
        'Referrer-Policy: no-referrer',
      ],
    },
  },
});
