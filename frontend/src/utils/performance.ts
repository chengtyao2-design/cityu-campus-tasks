// Performance monitoring utilities
export class PerformanceMonitor {
  private static startTime: number = 0;
  private static marks: Map<string, number> = new Map();

  static startTiming(label: string = 'default'): void {
    this.startTime = performance.now();
    this.marks.set(`${label}_start`, this.startTime);
  }

  static endTiming(label: string = 'default'): number {
    const endTime = performance.now();
    const startTime = this.marks.get(`${label}_start`) || this.startTime;
    const duration = endTime - startTime;
    
    this.marks.set(`${label}_end`, endTime);
    this.marks.set(`${label}_duration`, duration);
    
    return duration;
  }

  static getDuration(label: string = 'default'): number {
    return this.marks.get(`${label}_duration`) || 0;
  }

  static logPerformance(label: string = 'default'): void {
    const duration = this.getDuration(label);
    console.log(`⏱️ Performance [${label}]: ${duration.toFixed(2)}ms`);
    
    if (duration > 1500) {
      console.warn(`⚠️ Performance warning: ${label} took ${duration.toFixed(2)}ms (>1.5s)`);
    } else {
      console.log(`✅ Performance good: ${label} completed in ${duration.toFixed(2)}ms`);
    }
  }

  static measureFirstPaint(): Promise<number> {
    return new Promise((resolve) => {
      if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const firstPaint = entries.find(entry => entry.name === 'first-paint');
          if (firstPaint) {
            resolve(firstPaint.startTime);
            observer.disconnect();
          }
        });
        observer.observe({ entryTypes: ['paint'] });
      } else {
        // Fallback for environments without PerformanceObserver
        setTimeout(() => resolve(performance.now()), 0);
      }
    });
  }

  static async measureMapLoadTime(): Promise<void> {
    this.startTiming('mapLoad');
    
    // Wait for map container to be ready
    await new Promise(resolve => {
      const checkMap = () => {
        const mapContainer = document.querySelector('.leaflet-container');
        if (mapContainer) {
          resolve(true);
        } else {
          setTimeout(checkMap, 10);
        }
      };
      checkMap();
    });

    // Wait for tiles to load
    await new Promise(resolve => {
      const checkTiles = () => {
        const tiles = document.querySelectorAll('.leaflet-tile');
        const loadedTiles = Array.from(tiles).filter(tile => 
          (tile as HTMLImageElement).complete
        );
        
        if (loadedTiles.length > 0 || tiles.length === 0) {
          resolve(true);
        } else {
          setTimeout(checkTiles, 50);
        }
      };
      setTimeout(checkTiles, 100); // Give some time for tiles to start loading
    });

    this.endTiming('mapLoad');
    this.logPerformance('mapLoad');
    
    return Promise.resolve();
  }

  static clearMarks(): void {
    this.marks.clear();
    this.startTime = 0;
  }
}