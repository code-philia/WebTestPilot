const esbuild = require("esbuild");
const path = require("path");
const fs = require("fs");

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

/**
 * @type {import('esbuild').Plugin}
 */
const esbuildProblemMatcherPlugin = {
	name: 'esbuild-problem-matcher',

	setup(build) {
		build.onStart(() => {
			console.log('[watch] build started');
		});
		build.onEnd((result) => {
			result.errors.forEach(({ text, location }) => {
				console.error(`✘ [ERROR] ${text}`);
				console.error(`    ${location.file}:${location.line}:${location.column}:`);
			});
			console.log('[watch] build finished');
		});
	},
};

function copyHtmlFiles() {
	const srcDir = path.join(__dirname, 'src', 'views');
	const destDir = path.join(__dirname, 'dist', 'views');
	
	// Create destination directory if it doesn't exist
	if (!fs.existsSync(destDir)) {
		fs.mkdirSync(destDir, { recursive: true });
	}
	
	// Copy all HTML files
	const files = fs.readdirSync(srcDir);
	files.forEach(file => {
		if (file.endsWith('.html')) {
			const srcPath = path.join(srcDir, file);
			const destPath = path.join(destDir, file);
			fs.copyFileSync(srcPath, destPath);
			console.log(`Copied ${file} to dist/views/`);
		}
	});
}

async function main() {
	const ctx = await esbuild.context({
		entryPoints: [
			'src/extension.ts'
		],
		bundle: true,
		format: 'cjs',
		minify: production,
		sourcemap: !production,
		sourcesContent: false,
		platform: 'node',
		outfile: 'dist/extension.js',
		external: ['vscode', 'playwright-core'],
		logLevel: 'silent',
		plugins: [
			/* add to the end of plugins array */
			esbuildProblemMatcherPlugin,
		],
	});
	
	if (watch) {
		await ctx.watch();
		// Copy HTML files initially in watch mode
		copyHtmlFiles();
	} else {
		await ctx.rebuild();
		await ctx.dispose();
		// Copy HTML files after build
		copyHtmlFiles();
	}
}

main().catch(e => {
	console.error(e);
	process.exit(1);
});
