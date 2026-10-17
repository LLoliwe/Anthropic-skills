import { defineConfig } from 'vite';
import { voidPlugin } from 'void';

// Disposable, local-only proof. Never configure a remote deployment target here.
export default defineConfig({
  plugins: [voidPlugin()],
});
