import { describe, expect, it } from "vitest";
import { copy } from "./i18n";

describe("interface localization", () => {
  it("provides marketplace essentials in both languages", () => {
    for (const language of ["ar", "en"] as const) {
      expect(copy[language].brand).toBeTruthy();
      expect(copy[language].marketplace).toBeTruthy();
      expect(copy[language].submitReport).toBeTruthy();
      expect(copy[language].approve).toBeTruthy();
    }
  });
});
