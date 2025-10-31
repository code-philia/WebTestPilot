import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Load and post-process the built webview HTML from a dist directory path.
 * This is useful for panels that don't have the extensionUri available.
 */
export function loadWebviewHtmlFromDist(distPath: string, webview: vscode.Webview, page: string): string {
  const indexHtmlPath = path.join(distPath, 'index.html');
  if (!fs.existsSync(indexHtmlPath)) {
    throw new Error(`Webview bundle not found at ${indexHtmlPath}`);
  }

  let html = fs.readFileSync(indexHtmlPath, 'utf-8');
  const nonce = _getNonce();

  const cspMeta = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${webview.cspSource} https: data:; style-src ${webview.cspSource} 'unsafe-inline'; font-src ${webview.cspSource}; script-src 'nonce-${nonce}'; connect-src ${webview.cspSource} https:;">`;
  html = html.replace('</head>', `${cspMeta}</head>`);

  const pageScript = `<script nonce="${nonce}">window.__PAGE__ = '${page}';</script>`;
  html = html.replace('</body>', `${pageScript}</body>`);

  // Ensure script tags include nonce
  html = html.replace(/<script(\s)/g, `<script nonce="${nonce}"$1`);

  const distUri = vscode.Uri.file(distPath);
  html = _rewriteResourceUrls(html, distUri, webview, nonce);

  return html;
}

/**
 * Load and post-process the built webview HTML using the extensionUri to resolve the dist folder.
 */
export function loadWebviewHtml(extensionUri: vscode.Uri, webview: vscode.Webview, page: string): string {
  const distUri = vscode.Uri.joinPath(extensionUri, 'webview-ui', 'dist');
  const distPath = distUri.fsPath;
  return loadWebviewHtmlFromDist(distPath, webview, page);
}

function _getNonce(): string {
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let text = '';
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

function _rewriteResourceUrls(html: string, distUri: vscode.Uri, webview: vscode.Webview, nonce: string): string {
  const scriptPattern = /<script([^>]*)src="([^"]+)"([^>]*)><\/script>/gi;
  html = html.replace(scriptPattern, (match, preAttrs, src, postAttrs) => {
    if (_isExternalResource(src)) {
      return match;
    }

    const resolvedSrc = _resolveWebviewUri(webview, distUri, src);
    let rebuilt = `<script${preAttrs || ''} src="${resolvedSrc}"${postAttrs || ''}></script>`;
    if (/nonce\s*=/.test(rebuilt)) {
      rebuilt = rebuilt.replace(/nonce\s*=\s*"[^"]*"/i, `nonce="${nonce}"`);
    } else {
      rebuilt = rebuilt.replace('<script', `<script nonce="${nonce}"`);
    }
    return rebuilt;
  });

  const linkPattern = /<link([^>]*)href="([^"]+)"([^>]*)>/gi;
  html = html.replace(linkPattern, (match, preAttrs, href, postAttrs) => {
    if (_isExternalResource(href)) {
      return match;
    }

    const resolvedHref = _resolveWebviewUri(webview, distUri, href);
    return `<link${preAttrs || ''}href="${resolvedHref}"${postAttrs || ''}>`;
  });

  return html;
}

function _isExternalResource(resourcePath: string): boolean {
  return (
    /^(https?:)?\/\//i.test(resourcePath) ||
    resourcePath.startsWith('vscode-resource:') ||
    resourcePath.startsWith('vscode-webview-resource:') ||
    resourcePath.startsWith('data:')
  );
}

function _resolveWebviewUri(webview: vscode.Webview, baseUri: vscode.Uri, resourcePath: string): string {
  const cleanedPath = resourcePath.trim();
  const [pathWithoutHash, hashFragment] = cleanedPath.split('#', 2);
  const [pathPart, queryString] = pathWithoutHash.split('?', 2);

  const normalizedSegments = pathPart.replace(/^\//, '').split('/').filter(s => s.length > 0);
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
