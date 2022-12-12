import adapter from "@sveltejs/adapter-static";
import { mdsvex } from "mdsvex";
import rehypeKatexSvelte from "rehype-katex-svelte";
import remarkMath from "remark-math";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter()
  },
  extensions: [".svelte", ".svx", ".md"],
  preprocess: mdsvex({
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatexSvelte],
    extensions: [".svx", ".md"]
  })
};

export default config;
