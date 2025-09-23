export type Formatter =
  | "text"
  | "number"
  | "date"
  | "json"
  | ((v: unknown, field: Field, all: Record<string, unknown>) => string);

export interface Field {
  key: string;
  label?: string;
  align?: "left" | "right" | "center";
  mono?: boolean; // 고정폭 폰트
  format?: Formatter;
  unit?: string; // number 뒤 단위 (예: 'px')

  // 필드(컬럼)별 클램프 옵션만 사용
  clamp?: boolean; // true 면 적용
  clampLines?: number; // 줄 수(미지정 시 3줄)
  scrollOnClamp?: boolean; // true: 스크롤, false: … 잘라내기
}
