import { describe, expect, it } from "vitest";
import { copy } from "./i18n";

describe("interface localization", () => {
  it("provides marketplace essentials in both languages", () => {
    for (const language of ["ar", "en"] as const) {
      expect(copy[language].brand).toBeTruthy();
      expect(copy[language].marketplace).toBeTruthy();
      expect(copy[language].submitReport).toBeTruthy();
      expect(copy[language].approve).toBeTruthy();
      expect(copy[language].requestsSubtitle).toBeTruthy();
      expect(copy[language].cash).toBeTruthy();
      expect(copy[language].noReports).toBeTruthy();
      expect(copy[language].noOffers).toBeTruthy();
      expect(copy[language].retry).toBeTruthy();
    }
    expect(copy.en.subtitle).not.toBe(copy.en.requestsSubtitle);
    expect(copy.ar.subtitle).not.toBe(copy.ar.requestsSubtitle);
  });
});
