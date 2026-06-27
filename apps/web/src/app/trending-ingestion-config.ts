export const ingestionLimits: Record<string, number> = {
  daily: 20,
  weekly: 30,
  monthly: 50,
};

export function ingestionLimitForPeriod(period: string): number {
  return ingestionLimits[period] ?? ingestionLimits.daily;
}
