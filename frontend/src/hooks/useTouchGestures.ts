import { useRef, useEffect, useCallback } from 'react';

export interface TouchPoint {
  x: number;
  y: number;
  timestamp: number;
}

export interface SwipeGesture {
  direction: 'left' | 'right' | 'up' | 'down';
  distance: number;
  velocity: number;
  duration: number;
}

export interface PinchGesture {
  scale: number;
  center: { x: number; y: number };
}

export interface TouchGestureOptions {
  onSwipe?: (gesture: SwipeGesture) => void;
  onPinch?: (gesture: PinchGesture) => void;
  onTap?: (point: TouchPoint) => void;
  onDoubleTap?: (point: TouchPoint) => void;
  onLongPress?: (point: TouchPoint) => void;
  swipeThreshold?: number;
  longPressDelay?: number;
  doubleTapDelay?: number;
  preventDefault?: boolean;
}

export function useTouchGestures(options: TouchGestureOptions = {}) {
  const {
    onSwipe,
    onPinch,
    onTap,
    onDoubleTap,
    onLongPress,
    swipeThreshold = 50,
    longPressDelay = 500,
    doubleTapDelay = 300,
    preventDefault = true
  } = options;

  const elementRef = useRef<HTMLElement>(null);
  const touchStartRef = useRef<TouchPoint | null>(null);
  const lastTapRef = useRef<TouchPoint | null>(null);
  const longPressTimerRef = useRef<NodeJS.Timeout | null>(null);
  const initialPinchDistanceRef = useRef<number | null>(null);

  const getTouchPoint = useCallback((touch: Touch): TouchPoint => ({
    x: touch.clientX,
    y: touch.clientY,
    timestamp: Date.now()
  }), []);

  const getDistance = useCallback((point1: TouchPoint, point2: TouchPoint): number => {
    const dx = point2.x - point1.x;
    const dy = point2.y - point1.y;
    return Math.sqrt(dx * dx + dy * dy);
  }, []);

  const getDirection = useCallback((start: TouchPoint, end: TouchPoint): 'left' | 'right' | 'up' | 'down' => {
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    
    if (Math.abs(dx) > Math.abs(dy)) {
      return dx > 0 ? 'right' : 'left';
    } else {
      return dy > 0 ? 'down' : 'up';
    }
  }, []);

  const getPinchDistance = useCallback((touches: TouchList): number => {
    if (touches.length < 2) return 0;
    
    const touch1 = touches[0];
    const touch2 = touches[1];
    
    const dx = touch2.clientX - touch1.clientX;
    const dy = touch2.clientY - touch1.clientY;
    
    return Math.sqrt(dx * dx + dy * dy);
  }, []);

  const getPinchCenter = useCallback((touches: TouchList): { x: number; y: number } => {
    if (touches.length < 2) return { x: 0, y: 0 };
    
    const touch1 = touches[0];
    const touch2 = touches[1];
    
    return {
      x: (touch1.clientX + touch2.clientX) / 2,
      y: (touch1.clientY + touch2.clientY) / 2
    };
  }, []);

  const handleTouchStart = useCallback((event: TouchEvent) => {
    if (preventDefault) {
      event.preventDefault();
    }

    const touch = event.touches[0];
    const touchPoint = getTouchPoint(touch);
    touchStartRef.current = touchPoint;

    // Handle pinch gesture start
    if (event.touches.length === 2) {
      initialPinchDistanceRef.current = getPinchDistance(event.touches);
      return;
    }

    // Start long press timer
    if (onLongPress) {
      longPressTimerRef.current = setTimeout(() => {
        onLongPress(touchPoint);
      }, longPressDelay);
    }
  }, [preventDefault, getTouchPoint, getPinchDistance, onLongPress, longPressDelay]);

  const handleTouchMove = useCallback((event: TouchEvent) => {
    if (preventDefault) {
      event.preventDefault();
    }

    // Handle pinch gesture
    if (event.touches.length === 2 && initialPinchDistanceRef.current && onPinch) {
      const currentDistance = getPinchDistance(event.touches);
      const scale = currentDistance / initialPinchDistanceRef.current;
      const center = getPinchCenter(event.touches);
      
      onPinch({ scale, center });
      return;
    }

    // Cancel long press if finger moves too much
    if (longPressTimerRef.current && touchStartRef.current) {
      const currentTouch = getTouchPoint(event.touches[0]);
      const distance = getDistance(touchStartRef.current, currentTouch);
      
      if (distance > 10) { // 10px threshold
        clearTimeout(longPressTimerRef.current);
        longPressTimerRef.current = null;
      }
    }
  }, [preventDefault, getPinchDistance, getPinchCenter, onPinch, getTouchPoint, getDistance]);

  const handleTouchEnd = useCallback((event: TouchEvent) => {
    if (preventDefault) {
      event.preventDefault();
    }

    // Clear long press timer
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
      longPressTimerRef.current = null;
    }

    // Reset pinch state
    if (event.touches.length < 2) {
      initialPinchDistanceRef.current = null;
    }

    if (!touchStartRef.current || event.changedTouches.length === 0) {
      return;
    }

    const touchEnd = getTouchPoint(event.changedTouches[0]);
    const distance = getDistance(touchStartRef.current, touchEnd);
    const duration = touchEnd.timestamp - touchStartRef.current.timestamp;

    // Handle swipe gesture
    if (distance >= swipeThreshold && onSwipe) {
      const direction = getDirection(touchStartRef.current, touchEnd);
      const velocity = distance / duration;
      
      onSwipe({
        direction,
        distance,
        velocity,
        duration
      });
    }
    // Handle tap gestures
    else if (distance < 10 && duration < 500) { // Small movement and quick tap
      // Check for double tap
      if (lastTapRef.current && onDoubleTap) {
        const timeSinceLastTap = touchEnd.timestamp - lastTapRef.current.timestamp;
        const distanceFromLastTap = getDistance(lastTapRef.current, touchEnd);
        
        if (timeSinceLastTap < doubleTapDelay && distanceFromLastTap < 50) {
          onDoubleTap(touchEnd);
          lastTapRef.current = null; // Reset to prevent triple tap
          return;
        }
      }
      
      // Single tap
      if (onTap) {
        onTap(touchEnd);
      }
      
      lastTapRef.current = touchEnd;
    }

    touchStartRef.current = null;
  }, [
    preventDefault,
    getTouchPoint,
    getDistance,
    getDirection,
    swipeThreshold,
    doubleTapDelay,
    onSwipe,
    onTap,
    onDoubleTap
  ]);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    element.addEventListener('touchstart', handleTouchStart, { passive: !preventDefault });
    element.addEventListener('touchmove', handleTouchMove, { passive: !preventDefault });
    element.addEventListener('touchend', handleTouchEnd, { passive: !preventDefault });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd, preventDefault]);

  return elementRef;
}

// Specialized hooks for common gestures
export function useSwipeGesture(
  onSwipe: (direction: 'left' | 'right' | 'up' | 'down') => void,
  threshold: number = 50
) {
  return useTouchGestures({
    onSwipe: (gesture) => onSwipe(gesture.direction),
    swipeThreshold: threshold
  });
}

export function usePinchZoom(
  onPinch: (scale: number) => void
) {
  return useTouchGestures({
    onPinch: (gesture) => onPinch(gesture.scale)
  });
}

export function useDoubleTap(
  onDoubleTap: () => void
) {
  return useTouchGestures({
    onDoubleTap: () => onDoubleTap()
  });
}