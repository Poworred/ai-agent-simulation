export function formatSimTime(day: number, minute: number): string {
  const hour = Math.floor(minute / 60);
  const mins = minute % 60;
  return `Day ${day} ${hour.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}`;
}
