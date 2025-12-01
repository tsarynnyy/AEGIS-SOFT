import AppleHealthKit, {
  HealthValue,
  HealthKitPermissions,
} from 'react-native-health';
import { Platform } from 'react-native';

const permissions: HealthKitPermissions = {
  permissions: {
    read: [
      AppleHealthKit.Constants.Permissions.HeartRate,
      AppleHealthKit.Constants.Permissions.HeartRateVariability,
      AppleHealthKit.Constants.Permissions.RestingHeartRate,
      AppleHealthKit.Constants.Permissions.Steps,
      AppleHealthKit.Constants.Permissions.StepCount,
      AppleHealthKit.Constants.Permissions.DistanceWalkingRunning,
      AppleHealthKit.Constants.Permissions.ActiveEnergyBurned,
      AppleHealthKit.Constants.Permissions.SleepAnalysis,
      AppleHealthKit.Constants.Permissions.BodyMass,
      AppleHealthKit.Constants.Permissions.Height,
    ],
    write: [],
  },
};

export interface HealthKitData {
  heartRate: number[];
  hrv: number[];
  steps: number[];
  sleep: any[];
  weight: number | null;
}

class HealthKitService {
  private isInitialized: boolean = false;

  /**
   * Initialize HealthKit and request permissions
   */
  async initialize(): Promise<{ success: boolean; error?: string }> {
    if (Platform.OS !== 'ios') {
      return { success: false, error: 'HealthKit is only available on iOS' };
    }

    return new Promise((resolve) => {
      AppleHealthKit.initHealthKit(permissions, (error: string) => {
        if (error) {
          console.error('[HealthKit] Initialization error:', error);
          resolve({ success: false, error });
        } else {
          console.log('[HealthKit] Initialized successfully');
          this.isInitialized = true;
          resolve({ success: true });
        }
      });
    });
  }

  /**
   * Check if HealthKit is available
   */
  async isAvailable(): Promise<boolean> {
    if (Platform.OS !== 'ios') return false;

    return new Promise((resolve) => {
      AppleHealthKit.isAvailable((error: Object, available: boolean) => {
        if (error) {
          console.error('[HealthKit] Availability check error:', error);
          resolve(false);
        } else {
          resolve(available);
        }
      });
    });
  }

  /**
   * Get heart rate samples
   */
  async getHeartRate(startDate: Date, endDate: Date = new Date()): Promise<any[]> {
    if (!this.isInitialized) {
      console.warn('[HealthKit] Not initialized');
      return [];
    }

    return new Promise((resolve) => {
      const options = {
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
      };

      AppleHealthKit.getHeartRateSamples(options, (error: Object, results: HealthValue[]) => {
        if (error) {
          console.error('[HealthKit] Heart rate fetch error:', error);
          resolve([]);
        } else {
          console.log(`[HealthKit] Fetched ${results.length} heart rate samples`);
          resolve(results);
        }
      });
    });
  }

  /**
   * Get HRV samples
   */
  async getHRV(startDate: Date, endDate: Date = new Date()): Promise<any[]> {
    if (!this.isInitialized) {
      console.warn('[HealthKit] Not initialized');
      return [];
    }

    return new Promise((resolve) => {
      const options = {
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
      };

      AppleHealthKit.getHeartRateVariabilitySamples(
        options,
        (error: Object, results: any[]) => {
          if (error) {
            console.error('[HealthKit] HRV fetch error:', error);
            resolve([]);
          } else {
            console.log(`[HealthKit] Fetched ${results.length} HRV samples`);
            resolve(results);
          }
        }
      );
    });
  }

  /**
   * Get daily step count
   */
  async getSteps(startDate: Date, endDate: Date = new Date()): Promise<any[]> {
    if (!this.isInitialized) {
      console.warn('[HealthKit] Not initialized');
      return [];
    }

    return new Promise((resolve) => {
      const options = {
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
      };

      AppleHealthKit.getDailyStepCountSamples(
        options,
        (error: Object, results: any[]) => {
          if (error) {
            console.error('[HealthKit] Steps fetch error:', error);
            resolve([]);
          } else {
            console.log(`[HealthKit] Fetched ${results.length} step samples`);
            resolve(results);
          }
        }
      );
    });
  }

  /**
   * Get sleep analysis
   */
  async getSleep(startDate: Date, endDate: Date = new Date()): Promise<any[]> {
    if (!this.isInitialized) {
      console.warn('[HealthKit] Not initialized');
      return [];
    }

    return new Promise((resolve) => {
      const options = {
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
      };

      AppleHealthKit.getSleepSamples(options, (error: Object, results: any[]) => {
        if (error) {
          console.error('[HealthKit] Sleep fetch error:', error);
          resolve([]);
        } else {
          console.log(`[HealthKit] Fetched ${results.length} sleep samples`);
          resolve(results);
        }
      });
    });
  }

  /**
   * Get latest weight
   */
  async getWeight(): Promise<number | null> {
    if (!this.isInitialized) {
      console.warn('[HealthKit] Not initialized');
      return null;
    }

    return new Promise((resolve) => {
      const options = {
        unit: 'kg',
      };

      AppleHealthKit.getLatestWeight(options, (error: Object, result: any) => {
        if (error) {
          console.error('[HealthKit] Weight fetch error:', error);
          resolve(null);
        } else {
          console.log('[HealthKit] Fetched weight:', result?.value);
          resolve(result?.value || null);
        }
      });
    });
  }

  /**
   * Fetch all health data for a date range
   */
  async fetchAllData(days: number = 7): Promise<HealthKitData> {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    console.log(`[HealthKit] Fetching ${days} days of data...`);

    const [heartRate, hrv, steps, sleep, weight] = await Promise.all([
      this.getHeartRate(startDate, endDate),
      this.getHRV(startDate, endDate),
      this.getSteps(startDate, endDate),
      this.getSleep(startDate, endDate),
      this.getWeight(),
    ]);

    return {
      heartRate,
      hrv,
      steps,
      sleep,
      weight,
    };
  }

  /**
   * Calculate sleep efficiency from sleep samples
   */
  calculateSleepEfficiency(sleepSamples: any[]): number {
    if (!sleepSamples || sleepSamples.length === 0) return 0;

    // Group by date
    const sleepByDate: { [key: string]: any[] } = {};
    sleepSamples.forEach((sample) => {
      const date = new Date(sample.startDate).toDateString();
      if (!sleepByDate[date]) sleepByDate[date] = [];
      sleepByDate[date].push(sample);
    });

    // Calculate efficiency for each night
    const efficiencies: number[] = [];
    Object.keys(sleepByDate).forEach((date) => {
      const samples = sleepByDate[date];
      const totalSleep = samples
        .filter((s) => s.value === 'ASLEEP' || s.value === 'INBED')
        .reduce((sum, s) => {
          const start = new Date(s.startDate).getTime();
          const end = new Date(s.endDate).getTime();
          return sum + (end - start);
        }, 0);

      const totalInBed = samples.reduce((sum, s) => {
        const start = new Date(s.startDate).getTime();
        const end = new Date(s.endDate).getTime();
        return sum + (end - start);
      }, 0);

      if (totalInBed > 0) {
        efficiencies.push(totalSleep / totalInBed);
      }
    });

    if (efficiencies.length === 0) return 0;
    return efficiencies.reduce((a, b) => a + b, 0) / efficiencies.length;
  }
}

export default new HealthKitService();
