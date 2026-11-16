import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.wasla.marketplace",
  appName: "Wasla",
  webDir: "dist",
  server: {
    androidScheme: "https",
    iosScheme: "https",
  },
};

export default config;