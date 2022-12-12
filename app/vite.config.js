import { sveltekit } from "@sveltejs/kit/vite";
import replace from "@rollup/plugin-replace";
import child_process from "child_process";
import fs from "fs";

const pkg = JSON.parse(fs.readFileSync(new URL("package.json", import.meta.url), "utf8"));

let replaceVersion = () =>
  replace({
    __VERSION__: process.env.npm_package_version,
    __GIT_COMMIT__: child_process.execSync("git rev-parse HEAD").toString().trim().slice(0, 8),
    __BUILD_TIME__: new Date().toISOString(),
    preventAssignment: true
  });

/** @type {import('vite').UserConfig} */
const config = {
  plugins: [sveltekit(), replaceVersion()]
};

export default config;
