import { useState, useEffect } from 'react';

export interface BreakpointConfig {
  sm: number;
  md: number;
  lg: number;
  xl: number;
  '2xl': number;
}

const defaultBreakpoints: BreakpointConfig = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
};

export type Breakpoint = keyof BreakpointConfig;

export interface ResponsiveState {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLandscape: boolean;
  isPortrait: boolean;
  breakpoint: Breakpoint;
  isTouchDevice: boolean;
}

export function useResponsive(breakpoints: BreakpointConfig = defaultBreakpoints): ResponsiveState {
  const [state, setState] = useState<ResponsiveState>(() => {
    if (typeof window === 'undefined') {
      return {
        width: 1024,
        height: 768,
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        isLandscape: true,
        isPortrait: false,
        breakpoint: 'lg' as Breakpoint,
        isTouchDevice: false
      };
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    return {
      width,
      height,
      isMobile: width < breakpoints.md,
      isTablet: width >= breakpoints.md && width < breakpoints.lg,
      isDesktop: width >= breakpoints.lg,
      isLandscape: width > height,
      isPortrait: height > width,
      breakpoint: getBreakpoint(width, breakpoints),
      isTouchDevice
    };
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

      setState({
        width,
        height,
        isMobile: width < breakpoints.md,
        isTablet: width >= breakpoints.md && width < breakpoints.lg,
        isDesktop: width >= breakpoints.lg,
        isLandscape: width > height,
        isPortrait: height > width,
        breakpoint: getBreakpoint(width, breakpoints),
        isTouchDevice
      });
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, [breakpoints]);

  return state;
}

function getBreakpoint(width: number, breakpoints: BreakpointConfig): Breakpoint {
  if (width >= breakpoints['2xl']) return '2xl';
  if (width >= breakpoints.xl) return 'xl';
  if (width >= breakpoints.lg) return 'lg';
  if (width >= breakpoints.md) return 'md';
  return 'sm';
}

// Hook for specific breakpoint checks
export function useBreakpoint(breakpoint: Breakpoint): boolean {
  const { breakpoint: current } = useResponsive();
  const breakpointOrder: Breakpoint[] = ['sm', 'md', 'lg', 'xl', '2xl'];
  
  const currentIndex = breakpointOrder.indexOf(current);
  const targetIndex = breakpointOrder.indexOf(breakpoint);
  
  return currentIndex >= targetIndex;
}

// Hook for media queries
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia(query);
    const handler = (event: MediaQueryListEvent) => setMatches(event.matches);

    mediaQuery.addEventListener('change', handler);
    setMatches(mediaQuery.matches);

    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}

// Common media queries
export const useCommonQueries = () => ({
  isMobile: useMediaQuery('(max-width: 767px)'),
  isTablet: useMediaQuery('(min-width: 768px) and (max-width: 1023px)'),
  isDesktop: useMediaQuery('(min-width: 1024px)'),
  isLandscape: useMediaQuery('(orientation: landscape)'),
  isPortrait: useMediaQuery('(orientation: portrait)'),
  prefersReducedMotion: useMediaQuery('(prefers-reduced-motion: reduce)'),
  prefersDarkMode: useMediaQuery('(prefers-color-scheme: dark)'),
  isHighDPI: useMediaQuery('(min-resolution: 2dppx)')
});