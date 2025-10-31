import { useCallback, useRef } from 'react';

// Type for the VS Code API
interface VSCodeAPI {
  postMessage(message: unknown): void;
  getState(): unknown;
  setState(state: unknown): unknown;
}

declare function acquireVsCodeApi(): VSCodeAPI;

/**
 * Custom React hook for VS Code webview communication
 * Provides methods for messaging and state management between webview and extension
 */
export function useVSCode() {
  const vscodeRef = useRef<VSCodeAPI | undefined>(undefined);

  // Lazy initialization of VS Code API (only call acquireVsCodeApi once)
  if (!vscodeRef.current) {
    if (typeof acquireVsCodeApi === 'function') {
      vscodeRef.current = acquireVsCodeApi();
    }
  }

  /**
   * Send a message to the extension
   */
  const postMessage = useCallback((command: string, data?: any) => {
    if (vscodeRef.current) {
      vscodeRef.current.postMessage({ command, ...data });
    } else {
      console.log('[Dev Mode] postMessage:', { command, ...data });
    }
  }, []);

  /**
   * Register a message listener
   * Returns cleanup function to remove the listener
   */
  const onMessage = useCallback((handler: (message: any) => void) => {
    const listener = (event: MessageEvent) => {
      handler(event.data);
    };
    
    window.addEventListener('message', listener);
    
    // Return cleanup function
    return () => window.removeEventListener('message', listener);
  }, []);

  /**
   * Get persisted state
   */
  const getState = useCallback((): any => {
    if (vscodeRef.current) {
      return vscodeRef.current.getState();
    } else {
      // Fallback for dev mode
      const state = localStorage.getItem('vscodeState');
      return state ? JSON.parse(state) : undefined;
    }
  }, []);

  /**
   * Set persisted state
   */
  const setState = useCallback((state: any) => {
    if (vscodeRef.current) {
      vscodeRef.current.setState(state);
    } else {
      // Fallback for dev mode
      localStorage.setItem('vscodeState', JSON.stringify(state));
    }
  }, []);

  return {
    postMessage,
    onMessage,
    getState,
    setState,
  };
}
