// 안정적인 HSL 색상 매핑 유틸
export const hashString = (str: string) => {
  let h = 5381;
  for (let i = 0; i < str.length; i++) h = (h << 5) + h + str.charCodeAt(i);
  return h >>> 0; // unsigned
};

// 그룹명을 안정적인 HSL 색으로 매핑
const cache = new Map<string, string>();
export const colorFromGroup = (
  group: unknown,
  opts?: { s?: number; l?: number },
): string => {
  const { s = 65, l = 50 } = opts ?? {};
  const key = String(group ?? "unknown");
  const ck = `${key}_${s}_${l}`;
  const hit = cache.get(ck);
  if (hit) return hit;

  const hue = hashString(key) % 360;
  const color = `hsl(${hue}, ${s}%, ${l}%)`;
  cache.set(ck, color);
  return color;
};
