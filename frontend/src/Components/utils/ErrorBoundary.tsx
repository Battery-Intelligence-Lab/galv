import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children?: ReactNode;
  fallback?: ReactNode|((error: Error) => ReactNode);
}

interface State {
  hasError: boolean;
  lastError: Error|null;
}

/**
 * ErrorBoundary component to catch errors in child components and display a
 * fallback UI.
 *
 * https://react-typescript-cheatsheet.netlify.app/docs/basic/getting-started/error_boundaries/
 */
class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    lastError: null,
  };

  public static getDerivedStateFromError(e: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, lastError: e };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
        const fallback = typeof this.props.fallback === 'function' ?
            this.props.fallback(this.state.lastError!) :
            this.props.fallback
      return fallback || <h1>Sorry.. there was an error</h1>;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;