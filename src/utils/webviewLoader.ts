import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";

const NONCE = "webtestpilot";

/**
 * Load and post-process the built webview HTML from a dist directory path.
 * This is useful for panels that don't have the extensionUri available.
 */
export function loadWebviewHtmlFromDist(
    distPath: string,
    webview: vscode.Webview,
    page: string
): string {
    const indexHtmlPath = path.join(distPath, "index.html");
    if (!fs.existsSync(indexHtmlPath)) {
        throw new Error(`Webview bundle not found at ${indexHtmlPath}`);
    }

    let html = fs.readFileSync(indexHtmlPath, "utf-8");
    const cspMeta = `<meta
  content="default-src 'none'; img-src ${webview.cspSource} https: data:; style-src ${webview.cspSource} 'unsafe-inline'; font-src ${webview.cspSource}; script-src 'nonce-${NONCE}' 'unsafe-inline'; connect-src ${webview.cspSource} https:;">
`;
    //   const cspMeta = `<meta
    //   http-equiv="Content-Security-Policy"
    //   content="default-src 'none'; img-src ${webview.cspSource} https:; script-src ${webview.cspSource}; style-src ${webview.cspSource};">
    // `;
    html = html.replace("</head>", `${cspMeta}</head>`);

    // Inject both the current page and the VS Code UI language into the webview global
    // `vscode.env.language` will be serialized so the webview can detect the user's language
    const pageScript = `<script nonce="${NONCE}">window.__PAGE__ = ${JSON.stringify(
        page
    )}; window.__VSCODE_LANGUAGE__ = ${JSON.stringify(vscode.env.language)};</script>`;
    html = html.replace("</body>", `${pageScript}</body>`);

    // Ensure script tags include nonce
    html = html.replace(/<script(\s)/g, `<script nonce="${NONCE}"$1`);

    const distUri = vscode.Uri.file(distPath);
    html = _rewriteResourceUrls(html, distUri, webview, NONCE);

    return html;
}

/**
 * Load and post-process the built webview HTML using the extensionUri to resolve the dist folder.
 */
export function loadWebviewHtml(
    webview: vscode.Webview,
    page: string
): string {
    const extensionUri = (globalThis as any).extensionUri as vscode.Uri;
    const distUri = vscode.Uri.joinPath(extensionUri, "webview-ui", "dist");
    const distPath = distUri.fsPath;
    return loadWebviewHtmlFromDist(distPath, webview, page);
}

function _rewriteResourceUrls(
    html: string,
    distUri: vscode.Uri,
    webview: vscode.Webview,
    nonce: string
): string {
    const scriptPattern = /<script([^>]*)src="([^"]+)"([^>]*)><\/script>/gi;
    html = html.replace(scriptPattern, (match, preAttrs, src, postAttrs) => {
        if (_isExternalResource(src)) {
            return match;
        }

        const resolvedSrc = _resolveWebviewUri(webview, distUri, src);
        let rebuilt = `<script${preAttrs || ""} src="${resolvedSrc}"${
            postAttrs || ""
        }></script>`;
        if (/nonce\s*=/.test(rebuilt)) {
            rebuilt = rebuilt.replace(/nonce\s*=\s*"[^"]*"/i, `nonce="${nonce}"`);
        } else {
            rebuilt = rebuilt.replace("<script", `<script nonce="${nonce}"`);
        }
        return rebuilt;
    });

    // Also add nonce for async scripts preloaded scripts
    const linkPattern = /<link([^>]*)href="([^"]+)"([^>]*)>/gi;
    html = html.replace(linkPattern, (match, preAttrs, href, postAttrs) => {
        if (_isExternalResource(href)) {
            return match;
        }

        const resolvedHref = _resolveWebviewUri(webview, distUri, href);
        // rebuild with a guaranteed space before href
        let rebuilt = `<link${preAttrs || ""} href="${resolvedHref}"${
            postAttrs || ""
        }>`;

        // Inject nonce for <link rel="preload" as="script"> or rel="modulepreload"
        const isPreloadScript =
      /\brel\s*=\s*["'][^"']*preload[^"']*["']/i.test(match) &&
      /\bas\s*=\s*["']script["']/i.test(match);
        const isModulePreload = /\brel\s*=\s*["']modulepreload["']/i.test(match);

        if (isPreloadScript || isModulePreload) {
            if (/nonce\s*=/.test(rebuilt)) {
                rebuilt = rebuilt.replace(/nonce\s*=\s*"[^"]*"/i, `nonce="${nonce}"`);
            } else {
                rebuilt = rebuilt.replace(/(<link\b)/i, `<link nonce="${nonce}"`);
            }
        }

        return rebuilt;
    });

    return html;
}

function _isExternalResource(resourcePath: string): boolean {
    return (
        /^(https?:)?\/\//i.test(resourcePath) ||
    resourcePath.startsWith("vscode-resource:") ||
    resourcePath.startsWith("vscode-webview-resource:") ||
    resourcePath.startsWith("data:")
    );
}

function _resolveWebviewUri(
    webview: vscode.Webview,
    baseUri: vscode.Uri,
    resourcePath: string
): string {
    const cleanedPath = resourcePath.trim();
    const [pathWithoutHash, hashFragment] = cleanedPath.split("#", 2);
    const [pathPart, queryString] = pathWithoutHash.split("?", 2);

    const normalizedSegments = pathPart
        .replace(/^\//, "")
        .split("/")
        .filter((s) => s.length > 0);
    const resourceUri = vscode.Uri.joinPath(baseUri, ...normalizedSegments);
    let webviewUri = webview.asWebviewUri(resourceUri).toString();

    if (queryString) {
        webviewUri += `?${queryString}`;
    }
    if (hashFragment) {
        webviewUri += `#${hashFragment}`;
    }

    return webviewUri;
}
